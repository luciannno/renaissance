#from sentinelle import TradeAlgorithm
import sentinelle
import getopt, sys, time
import importlib

import smtplib

import logging
import datetime as dt

logging.basicConfig()

class TradeExecution(object):
    """
    Setup and Execute the Algorithm
    """
    
    _portfolio_id = None
    
    def __init__(self, argv):
        """
        Get the necessary parameters to initialise a strategy properly
        """
        
        try:
            opts, args = getopt.getopt(argv,"p:h:",["p=","help="])
        except getopt.GetoptError:
            print 'execute.py -p <portfolio>'
            sys.exit(2)
            
        for opt, arg in opts:
            if opt == '-h':
                print 'execute.py -p <portfolio>'
                sys.exit()
            elif opt in ("-p", "--portfolio"):
                self._portfolio_id = arg

    def execute(self):
        """
        Initilise the strategy:
            - Setup the instrument to be run
            - Request the data
            - Setup Portfolio
            - Setup Broker/Backtester_Broker
            - Run Strategy
        """
        
        algo = sentinelle.TradeAlgorithm(portfolio_id = self._portfolio_id)
        
        
        algo.trading()
        
        
        
        #path = "sentinelle.strategy.%s.%s" % (self.strategy, self.strategy)
        #module_name, class_name = path.rsplit(".", 1)
        #strategy = getattr(importlib.import_module(module_name), class_name)
        #
        #instance = strategy(broker)
        #
        #instance.initialise()
        #
        #for idx, ticker in enumerate(instance.tickers):
        #    #Setup the strategy for each instrument in ticker
        #    instrument = self._db.retrieveInstrument(ticker)
        #    data = self._db.retrieveLatestData(instrument['id'][0], instance.freq, instance.limit)
        #    instance.instrument.append(instrument)
        #    instance.data.append(data)
        #
        ##Run Strategy once for whole dataset
        #instance.run()
        
        
        
    
        
if __name__ == '__main__':
    
    email_to = 'luciano@brunette.com.br'
    
    #Setup General Logging for Application
    logger = logging.getLogger("renaissance")
    logger.propagate = False 
    logging.basicConfig()
    logger.setLevel(logging.DEBUG)
 
    # create the logging file handler
    fh = logging.FileHandler("log/renaissance.log")
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    
    # add handler to logger object
    logger.addHandler(fh)
    logger.info("---------------------- %s ---------------------------" % dt.datetime.now().strftime('%d/%m/%Y'))
    logger.info("Started at %s" % (dt.datetime.now().strftime('%H:%M:%S')))
    #try:
    ex = TradeExecution(sys.argv[1:])
    ex.execute()
    #except Exception, e:
    #    message = """From: Luciano Brunette <luciano@brunette.com.br>
    #                To: Luciano Brunette <luciano@brunette.com.br>
    #                Subject: Error in Sentinelle
    #                
    #                Error: %s
    #                """
    #    s = smtplib.SMTP('localhost')
    #    s.sendmail( email_to, [email_to], message % (e) )
        
        
    logger.info("Finished at %s" % (dt.datetime.now().strftime('%H:%M:%S')))
    logger.info("-------------------------------------------------------------")
