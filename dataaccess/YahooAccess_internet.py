# -*- coding: utf-8 -*-
"""
Yahoo Finance
=============
Functions for downloading and processing financial data from yahoo finance.

Available functions
---------------------
intraDay
    Get intra day (upto 1 minute ticks) data from Yahoo! Finance.
getdata
    Get current data from Yahoo! Finance.
volumeAlert
    Find stocks with highest volume change.
priceAlert
    Find stocks with highest price change.
datetime
     Return a time object corresponding to the secnum from yahoo data.

    
Created on Fri Aug  2 16:54:59 2013

@author: nvankaya
"""

import urllib2 as u
import StringIO
import numpy as np
import datetime as dt
import time


def intraDay(SYMB,interval=60,days=1):
    """    
    Get intra day (upto 1 minute ticks) data from Yahoo! Finance.
    
    This function connects to Yahoo! Finance and fetches data. 
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
    >>> aapl = yahoo_finance.intraDay('YHOO')
    
    """
      
    urlstr = 'http://chartapi.finance.yahoo.com/instrument/1.0/'+SYMB+'/chartdata;type=quote;range='+str(days)+'d/csv/'
    
    try:  
      urlid = u.urlopen(urlstr)
    except:
      return(np.nan)
    
    data = urlid.read()
    s = StringIO.StringIO(data.replace('a',''))
    
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
  
def getdata(n=-1,  dtype = [('symbol','S10'), 
                            ('last',float),
                            ('open',float),
                            ('volume',float),
                            ('average_volume',float),
                            ('y_close',float)] ):
                              
    """
    Get current data from Yahoo! Finance.
  
    This function connects to Yahoo! Finance and fetches current data. 
    During market hours, this is the real time data provided by Yahoo!
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
    >>> aapl = yahoo_finance.getdata()
    
    s - Stock symbol
    w1 - Day's valus change, w4 - Day's value change (real time)
    v - Volume, a2 - Average daily volume
    p - Previous close
    o - open
    
    
    """
    baseurl ="http://download.finance.yahoo.com/d/quotes.csv?s="
    #baseurl = 'http://finance.yahoo.com/d/quotes.csv?s='
    
    nametag = {'symbol':'s', 'last':'l1', 'open':'o', 'volume':'v', 'average_volume':'a2','y_close':'p'}
    
    tags=''
    for i in range(0,np.shape(dtype)[0]):
        tags = tags+nametag[dtype[i][0]]
    
    
    symbs = np.genfromtxt('symbs.csv',dtype='str',delimiter=',')
    symbs = np.core.defchararray.add(symbs,'+')  
    
    if(n==-1):
        n = np.size(symbs)
    else:
        symbs = symbs[0:n]
    
    result = 0
    print "Fetching data.",
    for k in range(0,n,200):
      
        #symbstr = symbs[k:k+200].tostring().replace('\x00','')
        symbstr = symbs.tostring()
        symbstr = symbstr[0:len(symbstr)-1]
        
        symbstr+='&f='+tags
      
        urlstr=baseurl+symbstr+"&e=.csv"
        print urlstr
        try:  
            urlData = u.urlopen(urlstr)
        except:
            print k
            return(np.nan)
        data = urlData.read()
        print '.',
        s = StringIO.StringIO(data)
        q = np.genfromtxt(s,dtype=dtype,delimiter=',')
        
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
        Example: q = yahoo_finance.getdata()
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
    yahoo_finance.priceAlert : equivalent function for returning stocks with highest price change.
  
    Examples
    ---------
    >>> q = yahoo_finance.getdata()
    >>> volstocks = yahoo_finance.volumeAlert(q,5)
    
    """
    
    vol=q['volume']
    avgvol=q['average_volume']
    
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
  
def priceAlert(q,n=10,num='last',den='open'):
    """
    Find stocks with highest price change.
  
    This function returns the stocks with the highest last/open ratio.
  
    Parameters
    ----------
    q : List of stock tuples. This is returned by getdata()
        Example: q = yahoo_finance.getdata()
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
    yahoo_finance.volumeAlert : equivalent function for returning stocks with highest volume change.
  
    Examples
    ---------
    >>> q = yahoo_finance.getdata()
    >>> pricestocks = yahoo_finance.priceAlert(q,5)
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
    Return a time object corresponding to the secnum from yahoo data.
    
    This function returns a time object corresponding to the second number yahoo data.
    
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
    >>> q = yahoo_finance.intraDay()
    >>> t = yahoo_finance.datetime(q[:,0])
    
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
  

def main():
  
    q = getdata()
    print q
    volstocks = volumeAlert(q)
    print volstocks
    pricestocks = priceAlert(q)
    print pricestocks
  
if __name__ == "__main__":
    main()
