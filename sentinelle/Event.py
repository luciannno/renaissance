
from sentinelle.Order import Order

import abc


class Event(object):
    """
    
    """
    
    __metaclass__ = abc.ABCMeta
    
    type = None
    
    pass
    

class TickEvent(Event):
    """
    
    """
    
    def __init__(self, instrument, **kwargs):
        
        self.type = 'TICK'
        self.instrument = instrument
        
        for key, value in kwargs.iteritems():
            setattr(self, key, value)
        
    
    def __repr__(self):
        return "Tick event for %s | %s" % (self.instrument, self.df)

    
    
class SignalEvent(Event):   
    """
    
    """
    
    instrument = None
    side = None
    orderType = None
    stopPrice = None
    trailStopPrice = None
    
    
    def __init__(self, instrument, side, orderType, stopPrice=None, trailStopPrice=None):
        self.type = 'SIGNAL'
        self.instrument = instrument
        self.side = side
        self.orderType = orderType
        self.stopPrice = stopPrice
        self.trailStopPrice = trailStopPrice
    
    def __repr__(self):
        return "Signal Event for %s" % (self.instrument)
    
    
    
class OrderEvent(Event):
    """
    
    """
    
    def __init__(self, order):
        self.type = 'ORDER'
        self.order = order
        self.instrument = order.instrument
        self.side = order.side
        self.orderType = order.orderType
        self.stopPrice = order.stopPrice
        self.trailStopPrice = order.trailStopPrice
    
    def __repr__(self):
        return "Order Event for %s %s %s" % (self.order.instrument, self.order.quantity, self.order.isSuggested())
    