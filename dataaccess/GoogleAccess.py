
import datetime
from QuoteAccess import QuoteAccess
import urllib2 as u
import StringIO
import numpy as np

class GoogleAccess(QuoteAccess):

    def __init__(self):
        pass
            
    def getIntradayQuote(self, symbol, time_zone, interval_seconds=60, num_days=5):

        #http://www.google.com/finance/getprices?q=IXIC&x=INDEXNASDAQ&i=60&p=5d&f=d,o,h,l,c,v

        exchange, instrument = symbol.split(':')
        
        urlstr = "http://www.google.com/finance/getprices?q={0}&x={1}".format(instrument, exchange)
        urlstr += "&i={0}&p={1}d&f=d,o,h,l,c,v".format(interval_seconds,num_days)

        headers = {'User-Agent' : "Mozilla/5.0 (Windows NT 6.0; WOW64) AppleWebKit/534.24 (KHTML, like Gecko) Chrome/11.0.696.16 Safari/534.24"}
        req = u.Request(urlstr,None,headers)
        
        #print urlstr
        
        try:  
            urlid = u.urlopen(req)
        except:
            return(np.nan)
        
        data = urlid.read()
        s = StringIO.StringIO(data.replace('a',''))
        
        #self.changeTimeZone(time_zone)
        
        while(1):
            
            line = s.next();
            
            if(line[0:15]=='TIMEZONE_OFFSET'):
                timeoffset = int(line[16:])
                break
            
            if(s.pos==s.len):
                return(np.nan)
              
        q = np.genfromtxt(s,dtype='float',delimiter=',')
        idx = np.nonzero(q[:,0]>1000)[0]
        n = np.size(idx)
        
        for i in range(0,n-1):
            q[idx[i],0] += timeoffset*60
            q[idx[i]+1:idx[i+1],0] = q[idx[i]+1:idx[i+1],0]*60 + q[idx[i],0]
            
        q[idx[n-1],0] += timeoffset*60
        q[idx[n-1]+1:,0] = q[idx[n-1]+1:,0]*60 + q[idx[n-1],0]
        
        return q

        #print url_string

        #csv = urllib.urlopen(url_string).readlines()
        #quotes = []


        #for bar in xrange(7,len(csv)):
        #
        #    if csv[bar].count(',') != 5: continue
        #
        #    offset,close,high,low,open_,volume = csv[bar].split(',')
        #
        #    if offset[0] == 'a':
        #        day = float(offset[1:])
        #        offset = 0
        #    else:
        #        offset = float(offset)
        #
        #    open_, high, low, close = [float(x) for x in [open_,high,low,close]]
        #    dt = datetime.datetime.fromtimestamp(day + (interval_seconds*offset) )
        #
        #    quotes.append([dt,open_,high,low,close,volume])

        #while(1):
        #    
        #    line = s.next();
        #    
        #    if(line[0:9]=='gmtoffset'):
        #        timeoffset = int(line[10:])
        #        
        #    if(line[0:6]=='volume'):
        #        break
        #    
        #    if(s.pos==s.len):
        #        return(np.nan)
        #    
        #quotes = np.genfromtxt(s,dtype='float',delimiter=',')
        #
        #quotes[:,0]=q[:,0]+timeoffset;
        #
        #return quotes


    #def fetchGF(self, googleticker):
    #
    #    url = "http://www.google.com/finance?&q="
    #    txt = urllib.urlopen(url+googleticker).read()
    #    k = re.search('id="ref_(.*?)">(.*?)<',txt)
    #
    #    if k:
    #        tmp = k.group(2)
    #        q = tmp.replace(',','')
    #    else:
    #        q = "Nothing found for: %s" % (googleticker)
    #    
    #    return q
    #
    #def combine(self, ticker):
    #    quote = self.fetchGF(ticker) # use the core-engine function
    #    t = time.localtime()    # grasp the moment of time
    #    output = [t.tm_year,t.tm_mon,t.tm_mday,t.tm_hour,  # build a list
    #              t.tm_min,t.tm_sec,ticker,quote]
    #    return output
    #
    #def fetchPreMarket(self, ticker):
    #
    #    link = "http://finance.google.com/finance/info?client=ig&q="
    #    #link = "http://www.google.com/finance/info?infotype=infoquoteall&q="
    #    url = link+"%s" % (ticker)
    #    u = urllib2.urlopen(url)
    #    content = u.read()
    #    data = json.loads(content[3:])
    #    info = data[0]
    #
    #    try:
    #        t = str(info["lt"].replace(',', ''))    # time stamp
    #        l = float(info["l"].replace(',', ''))    # close price (previous trading day)
    #    #p = float(info["el"])   # stock price in pre-market (after-hours)
    #        p = 0.
    #    except:
    #        t = 0
    #        l = 0
    #        p = 0
    #
    #    return (t,l,p)
