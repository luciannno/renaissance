import dataaccess
import datetime as dt
import pytz
from sentinelle.Portfolio import Portfolio
from sentinelle.Instrument import Instrument
from sentinelle import broker
from sentinelle.Event import TickEvent

import getopt, sys, time
import importlib
import Queue as queue
import logging
import pandas

logging.basicConfig()

class ImprovedQueue(queue.Queue):
    
    def to_list(self):
        """
        Returns a copy of all items in the queue without removing them.
        """
        with self.mutex:
            return list(self.queue)

class TradeAlgorithm(object):
    """
    Encapsulate Trades with Portfolio, Event, Strategy, etc...
    """
    
    heartbeat = 1
    portfolio = None
    broker = None
    
    _db = None
    _data = {} # Pandas Dict
    
    logger = None
    events_queue = None # Remember: Everyone should share this event queue
    tickers = [] # A list of tickers all strategies are watching
    
    def __init__(self, portfolio_id):
        """
        Using portfolio_id retrive the portfolio, strategies and positions
        """
        self._db = dataaccess.DBAccess() # Setup DataAccess MySQL
        self.events_queue = ImprovedQueue() # Setup Event Queue
        self.logger = logging.getLogger("renaissance") # Get Logging for Renaissance
        
        self._data.update({'1minData' : {}, '15minData' : {}})
        
        (id, name, active, ext_broker, ext_code) = self._db.retrievePortfolio(portfolio_id)
        
        try:
            if ext_broker == "IB":
                self.broker = broker.Broker(self.events_queue)
            else:
                raise Exception
        except:
            self.logger.critical("No Broker Setup! Sentinelle will stop the run")
            raise Exception
        
        self.logger.info("Initialise Portfolio %s" % (name))
        self.portfolio = Portfolio(id, name)
        self.portfolio.strategies = self._loadStrategies()
                
        acc_data, port_data = self.broker.getAccountData()
        
        #contract = self.broker.createContract("FUT", "ESTX50", "DTB", "201606")
        #print self.broker.getHistoricalData(contract, durationStr="1 W", barSizeSetting="15 mins")
        #print self.broker.getMarketData(contract)
        
        
        for instrInPortfolio in port_data:
            try:
                dbInstrument = self._db.retrieveInstrumentFromIBSymbol(instrInPortfolio[0], instrInPortfolio[1])
    
                instrument = Instrument(dbInstrument['id'][0], dbInstrument['symbol'][0], instrInPortfolio[1],
                                        instrInPortfolio[2], instrInPortfolio[3],
                                        instrInPortfolio[4], instrInPortfolio[5],
                                        instrInPortfolio[6], instrInPortfolio[7],
                                        instrInPortfolio[9], dbInstrument['ib_symbol'][0],
                                        dbInstrument['ib_secType'][0], dbInstrument['world_ex_id'][0])
    
                self.portfolio.addInstrument(instrument)
            except:
                self.logger.info("Not found in database: %s" % (str(instrInPortfolio)))
        
    
    def _loadStrategies(self):
        """
        Load all the strategies available in DB and check if there is code for such a strategy.
        When code is found Initilise the Strategy and take the Tickers to watch turn them into instruments
        """
        strategies = self._db.retrieveStrategies(portfolio_id=self.portfolio._id)
        instances = []         
    
        for s in strategies:
            
            path = "sentinelle.strategy.%s.%s" % (s[0], s[0])
            module_name, class_name = path.rsplit(".", 1)
            strategy = getattr(importlib.import_module(module_name), class_name)
            self.logger.info("Add Strategy: %s" % (module_name))
            
            instance = strategy(self.events_queue, self._data)
            instance.initialise()
            
            for ticker in instance.tickers:
                dbInstrument = self._db.retrieveInstrument(ticker)
                instrument = Instrument(id=dbInstrument['id'][0],
                                        symbol=dbInstrument['symbol'][0],
                                        expiry=dbInstrument['expiry'][0],
                                        ext_secType=dbInstrument['ib_secType'][0],
                                        ext_symbol=dbInstrument['ib_symbol'][0],
                                        world_ex_id=dbInstrument['world_ex_id'][0])
                
                contract = self.broker.createContract(instrument.ext_secType, instrument.ext_symbol, instrument.world_ex_id, instrument.expiry)
                instrument.contract = contract
                self.tickers.append(instrument)
                
                #@TODO: Check if instrument already exists
                histdata1min = self.broker.getHistoricalData(instrument.contract, durationStr="1 W", barSizeSetting="1 min")
                histdata15min = self.broker.getHistoricalData(instrument.contract, durationStr="1 W", barSizeSetting="15 mins")
                self._data['1minData'].update({instrument.symbol : histdata1min})
                self._data['15minData'].update({instrument.symbol : histdata15min})
                
            instances.append(instance)
            
        return instances
    
    
    def _executeStrategies(self):
        """
        Execute Strategies in order of strategy.run_order from DB for a particular portfolio
        At this point strategy is already initialised.
        """
        
        for i in self.portfolio.strategies:
        
            #i.initialise()
            
            #print "Tickers are:", i.tickers
                       
            for idx, ticker in enumerate(i.tickers):
                # Setup the strategy for each instrument in ticker
                dbInstrument = self._db.retrieveInstrument(ticker)
                instrument = Instrument(id=dbInstrument['id'][0],
                                        symbol=dbInstrument['symbol'][0],
                                        expiry=dbInstrument['expiry'][0],
                                        ext_symbol=dbInstrument['ib_symbol'][0],
                                        ext_secType=dbInstrument['ib_secType'][0],
                                        world_ex_id=dbInstrument['world_ex_id'][0]) 

                # Create Data to be used in Strategy
                #data = self._db.retrieveLatestData(instrument.id, i.freq, i.limit)
                
                i.instrument.append(instrument)
                #i.data.append(data)
                #print data
            
            i.now_utc = dt.datetime.utcnow()
            
            try:
                # If Timezone is available for strategy try changing it otherwise keep going
                i.local_tz = pytz.timezone(i.timezone)
                i.now_utc = pytz.utc.localize(i.now_utc)
                i.local_time = i.now_utc.astimezone(i.local_tz)
            except:
                i.local_tz = pytz.timezone("Europe/London")
                i.now_utc = pytz.utc.localize(i.now_utc)
                i.local_time = i.now_utc.astimezone(i.local_tz)
                
            #Run Strategy once for whole dataset
            i.run()
        
    
    def on_order(self, order_event):
        
        self.logger.info("Creating a contract...")
        #(self, secType, symbol, exchange, expiry=None, currency=None )
        contract = self.broker.createContract(order_event.order.instrument.ext_secType,
                                              order_event.order.instrument.ext_symbol,
                                              order_event.order.instrument.world_ex_id,
                                              order_event.order.instrument.expiry)
    
        if order_event.order.side == "BOT":
            
            self.logger.info("Creating a LONG Order")
            self.broker.placeNewOrder(contract,
                                      order_event.order.quantity,
                                      orderType=order_event.order.orderType,
                                      stopPrice=order_event.order.stopPrice,
                                      trailStopPrice=order_event.order.trailStopPrice)
            
        elif order_event.order.side == "SLD":
            
            self.logger.info("Creating a SHORT Order")
            
            self.broker.placeNewOrder(contract,
                                      -order_event.order.quantity,
                                      orderType=order_event.order.orderType,
                                      stopPrice=order_event.order.stopPrice,
                                      trailStopPrice=order_event.order.trailStopPrice)
    
    def trading(self):
    
        self.logger.info("Currently in portfolio: %s" % self.portfolio.instruments)
        
        iters = 0
        event = None
        #time.sleep(20)
        
        #print "Initial Dataframe:",self._data['FESXM6']
        
        while iters < 3:
            
            try:
                #print "Try!", dt.datetime.now().isoformat()
                event = self.events_queue.get(False)
            except queue.Empty:
                #print "Except!", dt.datetime.now().isoformat()
                
                #print "Watching: ", self.tickers
                #time.sleep(10)
                
                for ticker in self.tickers:
                    self.logger.info("Getting next tick for %s" % (ticker))
                    try:
                        #self.broker.getNextTick(ticker, durationStr="60 S", barSizeSetting="1 min")
                        tickSignal = TickEvent(ticker, df=self._data['15minData'][ticker.symbol].tail(10)) 
                        self.events_queue.put(tickSignal) 
                    except Exception, e:
                        self.logger.info("Failed to get Next Tick:" + str(e))
                        time.sleep(15)
            else:
                #print "Else!"
                if event is not None:
                    if event.type == 'TICK':
                        self.logger.info('TICK received! %s' % dt.datetime.now().isoformat())
                        self.logger.info(event.df)
                        #print self._data['1minData']
                        
                        # Add the Min tick from event to 1 min Data
                        #self._data['1minData'][event.instrument.symbol] = self._data['1minData'][event.instrument.symbol].append(event.df)
                        # Housekeeping the data
                        #self._data['1minData'][event.instrument.symbol].drop_duplicates(keep="last", inplace=True)
                        
                        self._executeStrategies()
                        #self.cur_time = event.time
                        #print("Tick %s, at %s" % (ticks, self.cur_time))
                        #self._append_equity_state()
                        #self.strategy.calculate_signals(event)
                        #ticks += 1
                    elif event.type == 'SIGNAL':
                        
                        self.logger.info('SIGNAL received! %s' % (dt.datetime.now().isoformat()))
                        try:
                            order_event = self.portfolio.on_signal(event)
                            #self.portfolio_handler.on_signal(event)
                            
                            if order_event and order_event.type == 'ORDER':
                                self.on_order(order_event)
                            else:
                                self.logger.info("Order Event was interrupted by Portfolio!")
                        except Exception, e:
                            self.logger.info("Order was canceled - Reason: %s" % (str(e)))
                        
                    #elif event.type == 'ORDER':
                    #    print "ORDER received!", dt.datetime.now().isoformat()
                        #self.execution_handler.execute_order(event)
                    #elif event.type == 'FILL':
                    #    print "FILL received!", dt.datetime.now().isoformat()
                    #    self.portfolio_handler.on_fill(event)    
            #finally:
                #histdata15min = self.broker.getHistoricalData(instrument.contract, durationStr="1 W", barSizeSetting="15 mins")
                #self._data['1minData'].update({instrument.symbol : histdata1min})
                #self._data['15minData'].update({instrument.symbol : histdata15min})
                #print "Finally!", dt.datetime.now().isoformat()
                #next_events = self.events_queue.to_list()
                #print self._data
            
            #time.sleep(self.heartbeat)
            iters += 1
        
        
        #agg_10m = df.groupby(pd.TimeGrouper(freq='10Min')).aggregate(numpy.sum)
        #print "Finished Data: ", self._data['1minData']
