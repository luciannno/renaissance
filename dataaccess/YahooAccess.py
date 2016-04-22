
import datetime
from QuoteAccess import QuoteAccess
import numpy as np
import urllib2 as u
import StringIO

class YahooAccess(QuoteAccess):

    def __init__(self):
        pass

    def getIntradayQuote(self,symbol,time_zone,interval_seconds=60,num_days=5):
        """    
        Get intra day (upto 1 minute ticks) data from Yahoo! Finance.
        
        This function connects to Yahoo! Finance and fetches data. 
        Returns np.nan on failure
        
        Parameters
        ----------
        symbol : Stock or ticker symbol
            Example: GOOG for google. NASDAQ:YHOO for yahoo on NASDAQ
        time_zone : string
            Time zone for this symbol
        interval_seconds : int, optional
            Tick interval in seconds. Default is 60
        num_days : int, optional
            Number of previous days starting from today, to retrive data. 
            Default is 1 day (today)
        
        Returns
        -------
        out : ndarray
            An (n,6) sized array with following columns at each tick.
            (time, open, high, low, close, volume). Time is a number 
            representing the difference between the time and Jan 1, 1970.
            This can be converted to python time object using the datetime
            method in this module.
        """

        urlstr = 'http://chartapi.finance.yahoo.com/instrument/1.0/' + symbol + '/chartdata;type=quote;range='+str(num_days)+'d/csv/'
        #print urlstr
        try:  
            urlid = u.urlopen(urlstr)
        except:
            print "URL not found! Probably 404! %s " % (urlstr)
            return(np.nan)
        
        data = urlid.read()
        s = StringIO.StringIO(data.replace('a',''))
        
        #self.changeTimeZone(time_zone)
        
        while(1):
            
            line = s.next();
            
            if(line[0:9]=='gmtoffset'):
                timeoffset = int(line[10:])
                
            if(line[0:6]=='volume'):
                break
            
            if(s.pos==s.len):
                return(np.nan)
            
        q = np.genfromtxt(s,dtype='float',delimiter=',')
        
        q[:,0]=q[:,0]+timeoffset;
        
        
        
        return(q)
	
