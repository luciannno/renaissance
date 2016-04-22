
import os,time

class QuoteAccess(object):
    """Common base class for all Quote access"""
    
    def __init__(self):
        pass

    def getIntradayQuote(self, symbol, time_zone, interval_seconds=60, num_days=5):
        raise NotImplementedError

    def changeTimeZone(self, timezone):
        os.environ['TZ'] = timezone
        time.tzset()
        return time.ctime()
