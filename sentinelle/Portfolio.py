from sentinelle.Manager import RiskManager
from sentinelle.Manager import PositionManager


from sentinelle.Order import SuggestedOrder

class Portfolio(object):
    """
    Build a portoflio
    """
    
    
    _id = None
    _name = None
    
    instruments = {}
    strategies = []
    
    riskmanager = None
    positionmanager = None
    
    def __init__(self, id, name):
        
        # Setup Portfolio
        self._id = id
        self._name = name
        
        self.riskmanager = RiskManager()
        self.positionmanager = PositionManager()
       
    
    def __repr__(self):
        return "Portfolio %s | Strategies: %s" % (self._id, self.strategies)
    
    def addInstrument(self, instrument):
        self.instruments.update( {instrument.symbol: instrument })
    
    def on_signal(self, signal_event):    
        """
        Signal an event from strategy
        """
        
        #print signal_event
        self.riskmanager.instruments = self.instruments
        self.positionmanager.instruments = self.instruments
        
        initial_order = SuggestedOrder(signal_event.instrument,
                                       signal_event.side,
                                       signal_event.orderType,
                                       signal_event.stopPrice,
                                       signal_event.trailStopPrice )
                
        sized_order = self.positionmanager.position_sizer(initial_order)
        
        if sized_order:
            order_events = self.riskmanager.order_refine(sized_order)
        else:
            order_events = None
            
        return order_events
    