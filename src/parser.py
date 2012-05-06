from gps_parser import GPSProductListParser
from gps_config import *
import datetime
from pytz import timezone
import urllib
import pg
import signal
import sys
import socket

log_f = None

def log(f, s):
    print s
    f.write(s + '\n')  

def signal_handler(signal, frame):
    log(log_f, str(datetime.datetime.now(timezone('UTC'))) + 
        ": CID collection process aborted.")
    sys.exit(0)  

crawled = False
curl_index = 0
collected = 0
start_page = 1
last_page = 2
intervals = []

while not crawled and curl_index < len(curl_files):
    try:
        socket.setdefaulttimeout(10)
        
        conn = pg.connect('itemcase', '50.116.1.34', 5432, None, None, 
                          'postgres', 'fastMoving2BreakEverything')
        pgqueryobject = conn.query('SELECT cid_product FROM product')
        result = pgqueryobject.getresult()
        
        log_f = open(log_output_file, 'a')
        
        log(log_f, str(datetime.datetime.now(timezone('UTC'))) + 
            ": CID collection process started." +
            " Bridge: #" + str(curl_index) + "." +
            " Pages: " + str(last_page - start_page) + ".")
            
        signal.signal(signal.SIGINT, signal_handler)
        
        for i in range(start_page, last_page):            
            f = urllib.urlopen(mount_gps_search_url('laptop', i, curl_index))
            s = f.read().decode('UTF-8')
            parser = GPSProductListParser()
            parser.feed(s)
            
            if len(parser.cid) == 0:
                raise Exception(1, 'Request error')
            for c in parser.cid:
                if not (c,) in result:
                    result.append((c,))
                    collected += 1
                    conn.query('INSERT INTO product VALUES(' + 
                               c + ', \'' + str(datetime.date.today()) + '\')')
            parser.close()
        
        log(log_f, str(datetime.datetime.now(timezone('UTC'))) + 
            ": CID collection process finished.")        
        crawled = True
        
    except IOError as e:
        log(log_f, str(datetime.datetime.now(timezone('UTC'))) + 
            ": Server #" + str(curl_index) + " offline.")
        curl_index += 1
        
    except Exception as e:
        if e.args[0] == 1:
            log(log_f, str(datetime.datetime.now(timezone('UTC'))) + 
                ": Server #" + str(curl_index) + " has been blocked.")
            curl_index += 1
        else:
            log(log_f, str(datetime.datetime.now(timezone('UTC'))) + 
                ": " + str(e.args[0]) + ".")
        
    finally:
        log(log_f, str(datetime.datetime.now(timezone('UTC'))) + 
            ": " + str(collected) + " new CIDs was collected.")
        log_f.close()
        conn.close()
