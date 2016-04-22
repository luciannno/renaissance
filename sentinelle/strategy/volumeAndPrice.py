from decimal import Decimal
from sentinelle.strategy import BaseStrategy

class volumeAndPrice(BaseStrategy):
    """
    Volume precedes price, meaning that the loss of upside price pressure in an uptrend or downside pressure 
    in a downtrend will show up in the volume figures before presenting itself as a reversal in trend on the bar chart.
    |-----------------------------------------------------------|
    |Price	Volume	Open Interest	Interpretation		|
    |-----------------------------------------------------------|
    |Rising	Rising	Rising		Market is Strong	|
    |Rising	Falling	Falling		Market is Weakining 	|
    |Falling	Rising	Rising		Market is Weak		|
    |Falling	Falling Falling		Market is Strengthening |
    |-----------------------------------------------------------|
    """
        
    def initialise(self):
        self.tickers = ['FESXM6']
        #self.tickers = ['FESXM6', 'STXE 600 OIL+GAS PR.EUR'] # Testing ability of system to request more than one dataframe
        self.limit = 10
        self.freq = 15
        self.timezone = 'Europe/Berlin'
        
    def run(self):
        
        index = -2 # Get Latest data
                
        strategy_data = self.data['15minData'][self.tickers[0]].tail() # Get data only for the first Ticker. The strategy is only run once
        
        price_date = strategy_data.index.get_values()[index]
        close_price = Decimal(strategy_data['close_price'].iloc[index])
        open_price = Decimal(strategy_data['open_price'].iloc[index])
        volume = strategy_data['volume'].iloc[index]
                
        strategy_volume = 55000
        orderType = "MKT"
        
        self.logger.info("Running Strategy Volume and Price - %s" % (self.local_time.isoformat()))
        self.logger.info("Date: %s | Close: %s | Open: %s | Volume: %s | " % (price_date, close_price, open_price, volume))
        
        if (volume >= strategy_volume):
            if (open_price >= close_price):
                stopPrice = int(round(close_price-Decimal(13),0))
                trailStopPrice = int(round(close_price+Decimal(9), 0))
                self.logger.info("=> Should BUY stop: %f trail: %f" % (stopPrice, trailStopPrice))
                orderid = self.generateSignal(instrument=self.instrument[0], side="BOT", orderType=orderType, stopPrice=stopPrice, trailStopPrice=trailStopPrice)
            elif (open_price < close_price):
                #stopPrice = int(round(close_price-Decimal(13),0))
                #trailStopPrice = int(round(close_price+Decimal(9), 0))
                #self.logger.info("=> Should BUY stop: %f trail: %f" % (stopPrice, trailStopPrice))
                #orderid = self.generateSignal(instrument=self.instrument[0], side="BOT", orderType=orderType, stopPrice=stopPrice, trailStopPrice=trailStopPrice)
                
                stopPrice = int(round(close_price+Decimal(13), 0))
                trailStopPrice = int(round(close_price-Decimal(9), 0))
                self.logger.info("=> Should SELL stop: %f trail: %f" % (stopPrice, trailStopPrice))
                orderid = self.generateSignal(instrument=self.instrument[0], side="SLD", orderType=orderType, stopPrice=stopPrice, trailStopPrice=trailStopPrice)
            else:
                self.logger.info("Dont know! Flat Candle!")
            
        else:
            self.logger.info("Not sufficient volume: %f" % (volume))
