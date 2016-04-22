# -*- coding: utf-8 -*-
"""

Google Finance
=============
Functions for downloading and processing financial data from Google finance.

Available functions
---------------------
intraDay
    Get intra day (upto 1 minute ticks) data from Google Finance.
getdata
    Get current data from Google Finance.
volumeAlert
    Find stocks with highest volume change.
priceAlert
    Find stocks with highest price change.
datetime
     Return a time object corresponding to the secnum from Google data.

    
Created on Fri Aug  2 16:54:59 2013

@author: nvankaya

"""
import urllib2 as u
import StringIO
import numpy as np
import datetime as dt
from xml.dom import minidom
import time

def intraDay(SYMB,interval=60,days=1):
    """    
    Get intra day (upto 1 minute ticks) data from Google Finance.
  
    This function connects to Google Finance and fetches data. 
    Returns np.nan on failure
  
    Parameters
    ----------
    SYMB : Stock or ticker symbol
        Example: GOOG for Google. NASDAQ:YHOO for Yahoo! on NASDAQ
    interval : int, optional
        Tick interval in seconds. Default is 60
    days : int, optional
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
        
  
    See Also
    --------
    yahoo_finance.intraDay : equivalent function for fetching data from Yahoo!.
  
    Examples
    ---------
    >>> aapl = google_finance.intraDay('AAPL')
  
    
    """
      #http://www.google.com/ig/api?stock=AAPL&stock=GOOG
    urlstr = 'http://www.google.com/finance/getprices?q='+SYMB+'&i='+str(interval)+'&p='+str(days)+'d&f=d,o,h,l,c,v';
    headers = {'User-Agent' : "Mozilla/5.0 (Windows NT 6.0; WOW64) AppleWebKit/534.24 (KHTML, like Gecko) Chrome/11.0.696.16 Safari/534.24"}
    req = u.Request(urlstr,None,headers)
    
    try:  
        urlid = u.urlopen(req)
    except:
        return(np.nan)
    
    data = urlid.read()
    s = StringIO.StringIO(data.replace('a',''))
    
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
        q[idx[i],0]+=timeoffset*60
        q[idx[i]+1:idx[i+1],0] = q[idx[i]+1:idx[i+1],0]*60 + q[idx[i],0]
        
    q[idx[n-1],0]+=timeoffset*60
    q[idx[n-1]+1:,0]=q[idx[n-1]+1:,0]*60 + q[idx[n-1],0]
    return(q)
  
def getdata(n=-1,  dtype = [('symbol','S10'),
           ('last',float),
           ('open',float),
            ('volume',float),
            ('avg_volume',float),
            ('y_close',float)] ):
    """
    Get current data from Google Finance.
  
    This function connects to Google Finance and fetches current data. 
    During market hours, this is the real time data provided by Google
    Returns np.nan on failure
  
    Parameters
    ----------
    SYMB : Stock or ticker symbol
        Example: GOOG for google. NASDAQ:YHOO for yahoo on NASDAQ
    interval : int, optional
        Tick interval in seconds. Default is 60
    days : int, optional
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
        
  
    See Also
    --------
    google_finance.intraDay : equivalent function for fetching data from Google.
  
    Examples
    ---------
    >>> aapl = google_finance.getdata()
    
    s - Stock symbol
    w1 - Day's valus change, w4 - Day's value change (real time)
    v - Volume, a2 - Average daily volume
    p - Previous close
    o - open
    """
    
    baseurlstr = 'http://www.google.com/ig/api?'
    
    symbs = np.genfromtxt('nasdaqsymbs.csv',dtype='str',delimiter=',')
    symbs = np.core.defchararray.add('stock=',symbs)
    symbs = np.core.defchararray.add(symbs,'&')
    
    if(n==-1):
        n = np.size(symbs)
    else:
        symbs = symbs[0:n]
    
    result = 0
    print "Fetching data.",
    for k in range(0,n,175):
      
        symbstr = symbs[k:k+175].tostring().replace('\x00','')
        symbstr = symbstr[0:len(symbstr)-1]
              
        urlstr=baseurlstr+symbstr
        try:  
            urlData = u.urlopen(urlstr)
        except:
            print k
            return(np.nan)
          
        data = urlData.read()
        print ".",
        q = genfromxml(data,dtype=dtype)
        
        if(result==0):
            result = q
        else:
            result = np.hstack((result,q))
        
        time.sleep(1)
      
    return(result)    
    
def volumeAlert(q,n=10,big=False):
    """
    Find stocks with highest volume change.
  
    This function returns the stocks with the highest volume/average_volume
  
    Parameters
    ----------
    q : List of stock tuples. This is returned by getdata()
        Example: q = google_finance.getdata()
    n : int, optional
        Number of stocks to return. The top n stocks will be returned. Default is 10.
    big : bool, optional
        If set to True, only stocks with average volume over 100,000 will be considered. 
        Default is False.
    
    Returns
    -------
    out : ndarray
        An (n,6) sized array with the same columns as input q.
            
  
    See Also
    --------
    google_finance.priceAlert : equivalent function for returning stocks with highest price change.
  
    Examples
    ---------
    >>> q = google_finance.getdata()
    >>> volstocks = google_finance.volumeAlert(q,5)
    
    """
    
    vol=q['volume']
    avgvol=q['avg_volume']
    
    avgvol[avgvol==0]=np.inf
    
    pervol = vol/avgvol
    
    pervol[np.isnan(pervol)]=-np.inf
    if(big):
        pervol[np.nonzero(avgvol<100000)]=-np.inf
    result = list()
    for k in range(0,n):
      
        m = np.argmax(pervol)
        result.append(q[m])
        pervol[m] = -np.inf
      
    dtype = np.result_type(q)
    result = np.array(result,dtype=dtype)
    return(result)
  
def priceAlert(q,n=10,num ='last',den='open'):
    """
    Find stocks with highest price change.
  
    This function returns the stocks with the highest last/open ratio.
  
    Parameters
    ----------
    q : List of stock tuples. This is returned by getdata()
        Example: q = google_finance.getdata()
    n : int, optional
        Number of stocks to return. The top n stocks will be returned. Default is 10.
    num : str, optional
        The price to be used as numerator in the ratio computation. 
        Default is 'last'.
    den : str, optional
        The price to be used as denominator in the ratio computation.
        Default is 'open'
    Returns
    -------
    out : ndarray
        An (n,6) sized array with the same columns as input q.
            
  
    See Also
    --------
    google_finance.volumeAlert : equivalent function for returning stocks with highest volume change.
  
    Examples
    ---------
    >>> q = google_finance.getdata()
    >>> pricestocks = google_finance.priceAlert(q,5)
    
    """
    
    t = q[num]
    p = q[den]
    
    p[p==0]=np.inf
    
    perpri = (t/p-1)*100
    
    perpri[np.isnan(perpri)]=-np.inf
    
    result = list()
    for k in range(0,n):
      
        m = np.argmax(perpri)
        result.append(q[m])
        perpri[m] = -np.inf
      
    dtype = np.result_type(q)
    result = np.array(result,dtype=dtype)  
    return(result)

  
 
def datetime(secnum):
    """
    Return a time object corresponding to the secnum from google data.
    
    This function returns a time object corresponding to the second number google data.
    
    Parameters
    ----------
    secnum : array_like
        A scalar or vector of the seconds numbers.
    Returns
    -------
    out : ndarray
        An ndarray of date.datetime objects with the same size as input.
  
    Examples
    ---------
    >>> q = google_finance.intraDay()
    >>> t = google_finance.datetime(q[:,0])
    
    """
    
    N = np.size(secnum)
    
    # Scalar input
    if(N==1):
        return(dt.datetime(1970,01,01,00,00,00) + dt.timedelta(seconds=secnum))
    
    # Vector input
    start = np.repeat(dt.datetime(1970,01,01,00,00,00),N)
    diff_secs = np.repeat(dt.timedelta(0),N)  
    for i in range(0,N):
        diff_secs[i] = dt.timedelta(seconds=secnum[i])
      
    return(start+diff_secs)


def genfromxml(xmlstr,dtype):
    """
    Helper function to parse the XML output from Google Finance
    """
    
    ncols = len(dtype)
    tmp = list()
    
    for i in range(0,ncols):
      
        if(type(dtype[i][1])==str):
            tmp.append('0000000000')
        else:
            tmp.append(dtype[i][1](0))
            
    tmp = np.array(tuple(tmp),dtype=dtype)
  
    itemlist=list()
    for i in range(0,ncols):
        xmldoc = minidom.parseString(xmlstr)
        itemlist.append(xmldoc.getElementsByTagName(dtype[i][0]))
    
    nrows = len(itemlist[0])
    result = np.repeat(tmp,nrows)
    
    for i in range(0,ncols):
        for j in range(0,nrows):
            try:
                result[dtype[i][0]][j]= itemlist[i][j].attributes['data'].value
            except:
                result[dtype[i][0]][j]=np.nan
     
    return(result)
  

def main():
    q = getdata()
    volstocks = volumeAlert(q)
    print volstocks
    pricestocks = priceAlert(q)
    print pricestocks
  
  
if __name__ == "__main__":
    main()

