from gps_parser import GPSProductListParser
from gps_config import *
import datetime
from pytz import timezone
import urllib
import pg
import signal
import sys

parse_html = True
collected = 0
start_page = 1
last_page = 100

conn = pg.connect('itemcase', '50.116.1.34', 5432, None, None, 'postgres', 'fastMoving2BreakEverything')
pgqueryobject = conn.query('SELECT cid_product FROM product')
result = pgqueryobject.getresult()

log = open(log_output_file, 'a')


def signal_handler(signal, frame):
    log.write(str(datetime.datetime.now(timezone('UTC'))) + " - CID collection process aborted\n")
    sys.exit(0)
    
signal.signal(signal.SIGINT, signal_handler)

if parse_html:
    log.write(str(datetime.datetime.now(timezone('UTC'))) + " - CID collection process started for " + str(last_page - start_page) + ' pages\n')
    try:
        for i in range(start_page, last_page):
            print 'Page: #' + str(i)
            f = urllib.urlopen(mount_gps_search_url('laptop', i))
            s = f.read().decode('UTF-8')
            parser = GPSProductListParser()
            parser.feed(s)
            if len(parser.cid) == 0:
                print s
                log.write(str(datetime.datetime.now(timezone('UTC'))) + " - Request error\n")
                break
            print parser.cid
            for c in parser.cid:
                if not (c,) in result:
                    result.append((c,))
                    collected += 1
                    log.write(str(datetime.datetime.now(timezone('UTC'))) + " - CID #" + c + " collected\n")
                    conn.query('INSERT INTO product VALUES(' + c + ', \'' + str(datetime.date.today()) + '\')')
            parser.close()
        log.write(str(datetime.datetime.now(timezone('UTC'))) + " - CID collection process finished\n")
    finally:        
        log.write(str(datetime.datetime.now(timezone('UTC'))) + " - " + str(collected) + " new CIDs was collected\n")

log.close()
conn.close()
