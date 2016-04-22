from DBAccess import DBAccess
from QuandlAccess import QuandlAccess
from GoogleAccess import GoogleAccess
from YahooAccess import YahooAccess

import logging
import pandas as pd
import MySQLdb
import MySQLdb.cursors


class DBAccess(object):
    """
    Class for DB access
    @TODO: DB information should be taken from a cfg file or something similiar
    """
    
    _db_connection = None
    _db_cur = None
    logger = None

    def __init__(self):
        hostname = "localhost"
        username = "renaissance"
        password = "luciano"
        database = "renaissance"
        self._db_connection = MySQLdb.connect(hostname, username, password, database) #, cursorclass=MySQLdb.cursors.DictCursor
        self._db_cur = self._db_connection.cursor()
        self.logger = logging.getLogger("renaissance")

    def query(self, query, params=""):
        return self.getCursor().execute(query, params)

    def getConnection(self):
        return self._db_connection

    def getCursor(self):
        return self._db_cur

    def getSingleRow(self, query):
        self.getCursor().execute(query)
        return self.getCursor().fetchone()

    def updateRow(self, table, **data):
        idName = "id"
        id = data[idName]
        del data[idName]
        sets = []
        for key in data.keys():
            sets.append("%s = %%s" % key)
            set = ', '.join(sets)
        
        qq = "UPDATE %s SET %s WHERE %s = %%s" % (table, set, idName,)
        
        try:
            self.getCursor().execute(qq, tuple(data.values()+[id]))
            self._db_connection.commit()
        except:
            self._db_connection.rollback()
            raise Exception
            
        #print self.getCursor()._last_executed
        #return self.getCursor().lastrowid
        #print self.getCursor()._last_executed

    def insertRow(self, table, **data):
        keys = ', '.join(data.keys())
        vals = ', '.join(["%s"] * len(data.values()))
        query = "INSERT INTO %s (%s) VALUES (%s)" % (table, keys, vals)
        
        try:
            self.getCursor().execute(query, tuple(data.values()))
            self._db_connection.commit()
        except:
            self._db_connection.rollback()
            raise Exception
            
        return self.getCursor().lastrowid

    def __del__(self):
        self._db_connection.close()


    def getAllTickers(self):

        self.query("""select i.id, i.google_symbol, i.yahoo_symbol, i.prefered_download, e.time_zone
                                from instrument as i inner join exchange as e
                                on i.exchange_id = e.id""")

        return self.getCursor().fetchall()

    def retrieveMinData(self, instrument_id):
        """
        Retrive Minute Data from Database for a single instrument
        """
        self.query("select * from min_price as i where instrument_id = %s and price_date >= '2016-02-12 20:45:00' order by price_date asc", [ instrument_id ])
        headers =  [n[0] for n in self.getCursor().description]
        rows = self.getCursor().fetchall() # return list of tuples
        ret = pd.DataFrame(list(rows), columns = headers) #need to get
        
        return ret
    
    def retrieveLatestData(self, instrument_id=None, period=15, limit=300):
        """
        Retrive Data from Database for a single instrument in a given period in minutes
        :param instrument_id: The instrument_id from database
        :param period: The time in minutes to group by. ie: For 15 min data period=15.
        :param limit: Maximum amount of lines returned from DB
        """
        if not instrument_id:
            raise Exception("Instrument id is mandatory");
        
        self.logger.debug("Retrieve Lastest Data for instrument %d" % (instrument_id))
        
        query = """select * from (select id,
                substring_index(group_concat(price_date order by a.id), ',', 1) as price_date,
                substring_index(group_concat(open_price order by a.id), ',', 1) as open_price,
                substring_index(group_concat(close_price order by a.id desc), ',', 1) as close_price,
                max(a.high_price) as high_price, 
                min(a.low_price) as low_price, 
                sum(a.volume) as volume
                from min_price as a
                where a.instrument_id = %s
                group by UNIX_TIMESTAMP(a.price_date) DIV %s
                order by a.price_date desc
                limit %s) as q order by price_date asc"""
        
        self.query(query, [ instrument_id, period*60, limit ])
        self.logger.debug("Query: %s" % (query % (instrument_id, period*60, limit)))
        
        try:
            headers =  [n[0] for n in self.getCursor().description]
            rows = self.getCursor().fetchall() # return list of tuples
            df = pd.DataFrame(list(rows), columns = headers) #need to get
            df.index = df.price_date
            df = df.drop("price_date", 1)
        except:
            df = None
            
        return df
    
    def retrieveInstrument(self, symbol):

        query = """select i.id, i.symbol, i.google_symbol, i.yahoo_symbol, i.prefered_download, e.time_zone, i.ib_symbol, date_format(i.expiry, '%%Y%%m') as expiry, t.ib_secType, e.world_ex_id
                    from instrument as i
                    inner join exchange as e on i.exchange_id = e.id
                    inner join instrument_type as t on i.instrument_type_id = t.id
                    where i.symbol = %s"""

        self.query(query, [symbol])
        df = None
        
        try:
            rows = self.getCursor().fetchall() # return list of tuples
            headers =  [n[0] for n in self.getCursor().description]
            df = pd.DataFrame(list(rows), columns=headers)
        except:
            df = None
 
        return df
    
    def retrieveInstrumentFromIBSymbol(self, ib_symbol, expiry=None):

        query = """select i.id, i.symbol, i.google_symbol, i.yahoo_symbol, i.prefered_download, e.time_zone, i.ib_symbol, date_format(i.expiry, '%%Y%%m') as expiry, t.ib_secType, e.world_ex_id
                    from instrument as i
                    inner join exchange as e on i.exchange_id = e.id
                    inner join instrument_type as t on i.instrument_type_id = t.id
                    where i.ib_symbol = %s"""

        params = [ib_symbol]

        if expiry:
            query = query + " and i.expiry = %s"
            params.append(expiry)
        
        #print query.format(ib_symbol, expiry)
        
        self.query(query, params)
        
        try:
            rows = self.getCursor().fetchall() # return list of tuples
            headers =  [n[0] for n in self.getCursor().description]
            df = pd.DataFrame(list(rows), columns=headers)
        except:
            df = None
 
        return df

    def retrievePortfolio(self, portfolio_id):
        query = """select p.id, p.name, p.account_id, broker, ext_account
                    from portfolio as p
                    inner join account as a on a.id = p.account_id
                    where p.id = %s and a.active = 1"""

        self.query(query, [portfolio_id])
        rows = None
        
        try:
            rows = self.getCursor().fetchone()
        except:
            rows = None
        
        return rows
    
    def retrieveStrategies(self, portfolio_id):
        query = """select s.code
                    from strategy as s
                    where s.portfolio_id = %s and s.auto_activate = 1
                    order by s.run_order"""

        self.query(query, [portfolio_id])
        rows = None
        
        try:
            rows = self.getCursor().fetchall()
        except:
            rows = None
        
        return rows
        
