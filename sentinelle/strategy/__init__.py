import logging
import abc
import os, time
import datetime as dt

from sentinelle.Event import SignalEvent


class BaseStrategy(object):
    """Base class for strategies.
    
    .. note::
        This is a base class. Do not use it directly.
    """

    __metaclass__ = abc.ABCMeta
    
    _now = None # Time when class got called
    _events_queue = None 
    
    logger = None
    instrument = []
    data = [] #All the Data will be available for each strategy
    contract = None
    tickers = []
    now_utc = None
    local_time = None
    
    limit = 100 # How much data to load
    freq  = 60 # Frequency of the data to be requested
    
    def __init__(self, events_queue, data):
        self._now = dt.datetime.now()
        self.logger = logging.getLogger("renaissance")
        self._events_queue = events_queue
        self.data = data
    
    def __repr__(self):
        return "This is a Strategy Class"
    
    
    @abc.abstractmethod
    def initialise(self):
        """
        Override (**mandatory**)
        First method called when any Strategy is being executed
        """
        raise NotImplementedError()
    
    @abc.abstractmethod
    def run(self):
        """
        Override (**mandatory**)
        Method called after initialisation any Strategy
        """
        raise NotImplementedError()
    
    
    def generateSignal(self, instrument, side, orderType, stopPrice=None, trailStopPrice=None):
        """
        
        """
        
        
        
        eventSignal = SignalEvent(instrument, side, orderType, stopPrice, trailStopPrice)
        self._events_queue.put(eventSignal)
        #print "Add Signal to the queue:", instrument, trade, orderType
    
