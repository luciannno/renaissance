


class Instrument(object):
    
    id = None
    symbol = None
    expiry = None
    quantity = None
    marketPrice = None
    marketValue = None
    avgCost = None
    unrealizedPnL = None
    realizedPnL = None
    currency = None
    ext_symbol = None
    ext_secType = None
    world_ex_id = None
    
    contract = None # Broker's Contract
    
    def __init__(self, id, symbol, expiry=None, quantity=0, mktPrice=0, mktValue=0, avgCost=0, unrealizedPnL=0, realizedPnL=0, currency=None, ext_symbol=None, ext_secType=None, world_ex_id=None):
        self.id = id
        self.symbol = symbol
        self.expiry = expiry
        self.quantity = quantity
        self.marketPrice = mktPrice
        self.marketValue = mktValue
        self.avgCost = avgCost
        self.unrealizedPnL = unrealizedPnL
        self.realizedPnL = realizedPnL
        self.currency = currency
        self.ext_symbol = ext_symbol
        self.ext_secType = ext_secType
        self.world_ex_id = world_ex_id
        
    def __repr__(self):
        return "Instrument: (%05d) %s | QTY: %d" % (self.id, self.symbol, self.quantity)
