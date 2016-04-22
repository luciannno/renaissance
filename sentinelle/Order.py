
import abc

class Order:
    """
    
    """
    
    __metaclass__ = abc.ABCMeta
    
    instrument = None
    side = None
    orderType = None
    stopPrice = None
    trailStopPrice = None
    suggested = False
    quantity = 0


    def __init__(self, instrument, side, orderType, stopPrice=None, trailStopPrice=None):
        self.instrument = instrument
        self.side = side
        self.orderType = orderType
        self.stopPrice = stopPrice
        self.trailStopPrice = trailStopPrice

    def isSuggested(self):
        return self.suggested
    
    def __repr__(self):
        return "This is an order for %s" % (self.instrument)


class SuggestedOrder(Order):
    """
    
    """
        
    def __init__(self, instrument, side, orderType, stopPrice=None, trailStopPrice=None):
        super(SuggestedOrder, self).__init__(instrument, side, orderType, stopPrice, trailStopPrice)
        #Only RiskManager Should be able to remove the suggested flag
        self.suggested = True

