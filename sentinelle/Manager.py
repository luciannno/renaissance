
from sentinelle.Event import OrderEvent

class RiskManager(object):
    """
    Risk Manager should cancel or create an Order Event from a Signal Event
    """
    
    instruments = []
        
    def __init__(self):
        pass
    
    def order_refine(self, risk_order):
        """
        
        """
                
        try:
            cquantity = self.instruments['FESXM6'].quantity
        except:
            cquantity = 0

        if cquantity > 0:
            if risk_order.side == "SLD":
                raise ValueError("Already a LONG position is set!")
            elif cquantity > 5:
                raise ValueError("Maximum Quantity achieved %d" % (cquantity))
        elif cquantity < 0:
            if risk_order.side == "BOT":
                raise ValueError("Already a SHORT position is set!")
            elif cquantity < 5:
                raise ValueError('Maximum Quantity achieved %d' % (cquantity))

        order_event = OrderEvent(risk_order)
        order_event.order.suggested = False
                
        return order_event
    


class PositionManager(object):
    """
    Position Manager should set the size of the trade to create
    """
    
    DEFAULT_QUANTITY = 2
    MAX_QUANTITY = 6
    
    instruments = []
    
    def __init__(self):
        pass
    
    def position_sizer(self, position_order):
        """
        
        """

        try:
            cquantity = self.instruments['FESXM6'].quantity        
        except:
            cquantity = 0
        
        if (cquantity+self.DEFAULT_QUANTITY) > self.MAX_QUANTITY:
            position_order.quantity = self.MAX_QUANTITY - cquantity
        else:
            position_order.quantity = self.DEFAULT_QUANTITY
        
        return position_order

