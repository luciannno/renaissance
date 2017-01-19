#
# A quick Python module to obtain stock quotes.
#
# Copyright 1999 Eklektix, Inc.  This sofware is freely distributable under
# the terms of the GNU Library General Public Licence (LGPL).
#
# Written by Jonathan Corbet, corbet@eklektix.com.  Current version is available
# at ftp.eklektix.com/pub/Quote.
#
# $Id: Quote.py,v 1.5 2000/04/24 16:06:28 corbet Exp $
#
# Basic usage is:
#
#       quote = Quote.Lookup (symbol)
#
# where 'symbol' is the stock symbol.  The return value is an instance of the
# Quote class, which has the following attributes:
#
#	symbol		The stock symbol for which the quote applies
#	name		The name of the company
#	time		Time of last trade (internal unix format)
#	value		The current value of the stock
#	change		Change in value since market opening
#	open		Opening value of the stock
#	previous_close	Previous day's closing value
#	percent_change	Percentage change in value of the stock
#	high		Today's high value
#	low		Today's low value
#	volume		Trading volume in shares
#	market_cap	Market capitalization, in millions of dollars
#	year_high	Highest value in last year
#	year_low	Lowest value in last year
#	eps		Earnings per share
#	pe_ratio	Price to earnings ratio (-1 if no earnings)
#
# In case of errors (which happens, web server doesn't always respond) None is
# returned. 
#
# Currently this module only works with quote.yahoo.com.  Future plans involve
# making it work with other web quote services as well...
#
import urllib
import string
import time

#
# Here is the Quote class that we return.  Pretty boring...
#
class Quote:
    pass

#
# The function that actually does quote lookups.
#
def Lookup (symbol):
    (qurl, decoder) = MakeUrl (symbol)
    response = urllib.urlopen (qurl)
    q = Quote ()
    if decoder (q, response):
	return q
    #
    # Try one more time.
    #
    # print 'Retry: ' + symbol
    response = urllib.urlopen (qurl)
    if decoder (q, response):
	return q
    return None

#
# Internal stuff below.
#

#
# Yahoo: create a URL to look up a stock quote.
#
def MakeYahooURL (symbol):
    qurl = 'http://quote.yahoo.com/d/quotes.csv?s=%s&f=sl1d1t1c1ohgvj1pp2owern&e=.csv' \
	   % (symbol)
    return (qurl, DecYahooUrl)

#
# Deal with flaky input.
#
def DecInt (v, flake = 0):
    try:
	return string.atoi (v)
    except ValueError:
	return (flake)

def DecFloat (v, flake = 0.0):
    try:
	return string.atof (v)
    except ValueError:
	return (flake)


#
# Yahoo: Decode a response to a Yahoo stock lookup.
#
def DecYahooUrl (q, response):
    #
    # Pull the info from the server, split it, and make sure it makes sense.
    #
    info = response.readline ()[:-2] # Get rid of CRLF
    sinfo = string.split (info, ',')
    if len (sinfo) < 15:
	return 0
    #
    # Start decoding.
    #
    q.symbol = sinfo[0][1:-1]
    q.value = DecFloat (sinfo[1])
    q.time = YahooDate (sinfo[2], sinfo[3])
    q.change = DecFloat (sinfo[4])
    q.open = DecFloat (sinfo[5])
    q.high = DecFloat (sinfo[6])
    q.low = DecFloat (sinfo[7])
    q.volume = DecInt (sinfo[8])
    #
    # Get the market cap into millions
    #
    q.market_cap = DecFloat (sinfo[9][:-1])
    if sinfo[9][-1] == 'B':
	q.market_cap = q.market_cap*1000
    q.previous_close = DecFloat (sinfo[10])
    q.percent_change = DecFloat (sinfo[11][1:-2])  # Zap training %
    q.open = DecFloat (sinfo[12])
    #
    # Pull apart the range.
    #
    range = string.split (sinfo[13][1:-1], '-')
    q.year_low = DecFloat (range[0])
    q.year_high = DecFloat (range[1])
    q.eps = DecFloat (sinfo[14])
    q.pe_ratio = DecFloat (sinfo[15])
    q.name = sinfo[16][1:-1]
    #
    # We made it.
    #
    return 1

#
# Convert date/times in Yahoo's format into an internal time.
#
def YahooDate (date, tod):
    #
    # Value errors can happen if yahoo declines to give us a date...
    #
    try:
	#
	# Date part is easy.
	#
	sdate = string.split (date[1:-1], '/')
	month = DecInt (sdate[0])
	day = DecInt (sdate[1])
	year = DecInt (sdate[2])
	#
	# Pick apart the time.
	#
	stime = string.split (tod[1:-1], ':')
	hour = DecInt (stime[0])
	minute = DecInt (stime[1][0:2])
	if stime[1][-2:] == 'PM':
	    hour = hour + 12
	#
	# Time to assemble everything.
	#
	ttuple = (year, month, day, hour, minute, 0, 0, 0, -1)
	return time.mktime (ttuple)
    except ValueError:
	return (0)
    except IndexError:
	print 'Date flake: ' + date
	return 0

#
# Create a URL to look somebody up.  Returns a tuple with the URL and
# a function to decode the result.  Someday this will handle multiple
# sources, but currently it only knows yahoo.
#
def MakeUrl (symbol):
    return MakeYahooURL (symbol)