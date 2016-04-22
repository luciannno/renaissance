from sysIB.wrapper_v4 import IBWrapper, IBclient
from swigibpy import Contract as IBcontract

from sentinelle.Event import TickEvent

import random
import logging
import pandas
logging.basicConfig()


class Broker(object):
    """
    
    """
    
    ACCOUNT = "U1734198"
    MARKET = "MKT"
    LIMIT = "LMT"
    BOT = "BOT"
    SLD = "SLD"
    
    tickers = [] # List of Instruments to get Data from IB
    _events_queue = None
    
    def __init__(self, events_queue):

        self.logger = logging.getLogger("renaissance")
        self.ibWrapper = IBWrapper()
        self.ibClient = IBclient(self.ibWrapper, accountid="U1734198")
        self._events_queue = events_queue

    def createContract(self, secType, symbol, exchange, expiry=None, currency=None ):
        """
        Create new IB Contract
        :param secType: Contract sector type: STK, OPT, FUT, IND, FOP, CASH,BAG, NEWS
        :param expiry: The expiration date. Use the format YYYYMM.
        :param symbol: This is the symbol of the underlying asset.
        :param exchange: The order destination, such as Smart.
        """
        ibcontract = IBcontract()
        ibcontract.secType = secType
        
        if expiry:
            ibcontract.expiry = expiry
        if currency:
            ibcontract.currency = currency
            
        ibcontract.symbol = symbol
        ibcontract.exchange = exchange
        
        return ibcontract
    
    
    #def generateSignal(self, ibcontract, trade, lmtPrice="0.0", orderType=MARKET, orderId=None, stopPrice=None, trailStopPrice=None):
    #    """
    #    Generate a signal BUY/SELL
    #    
    #    :param ibcontract: IBContract from swigibpy
    #    :param trade: Quantity
    #    :param lmtPrice: Limit price in case orderType is LMT
    #    :param orderType: MKT or LMT
    #    :param orderid: Order id. If None wrapper will inquire IB for next available code.
    #    :param stopPrice: Order Stop Loss price
    #    :param trailStopPrice: Order Stop Gain price
    #    """
    #    
    #    orderid = placeNewOrder(ibcontract, trade, lmtPrice, orderType, orderId, stopPrice, trailStopPrice)
    #    
    #    return orderid
    
    
    def placeNewOrder(self, ibcontract, trade, lmtPrice="0.0", orderType=MARKET, orderId=None, stopPrice=None, trailStopPrice=None):
        """
        Place an IB Order
        
        :param ibcontract: IBContract from swigibpy
        :param trade: Quantity
        :param lmtPrice: Limit price in case orderType is LMT
        :param orderType: MKT or LMT
        :param orderid: Order id. If None wrapper will inquire IB for next available code.
        :param stopPrice: Order Stop Loss price
        :param trailStopPrice: Order Stop Gain price
        """
    
        orderid = self.ibClient.place_new_IB_order(ibcontract, trade, lmtPrice, orderType, orderId, stopPrice, trailStopPrice)
        
        if not orderid:
            self.logger.fatal("Order was not placed! IB Connection is down!")
        
        return orderid
    
    def getNextTick(self, instrument, durationStr="60 S", barSizeSetting="1 min"):
        """
        Get the next minute DCHLOV (date, close, high, low, open, volume) data
        """
        
        df = self.getHistoricalData(instrument.contract, durationStr=durationStr, barSizeSetting=barSizeSetting)
        tickSignal = TickEvent(instrument, df=df) 
        self._events_queue.put(tickSignal)        
        
    
    def getHistoricalData(self, ibcontract, durationStr="1 Y", barSizeSetting="1 day"):
        result = self.ibClient.get_IB_historical_data(ibcontract, durationStr, barSizeSetting, tickerid=random.randint(1000, 9000))
        return result
    
    
    def getMarketData(self, ibcontract):
        result = self.ibClient.get_IB_market_data(ibcontract)
        return result
    
    def getAccountData(self):
        
        #print "Bid size, Ask size; Bid price; Ask price"
        #ans = ibClient.get_IB_market_data(ibcontract)
        #return ans
            
        (account_value, portfolio_data) = self.ibClient.get_IB_account_data()
        
        return (account_value, portfolio_data)
    