from gps_parser import GPSProductListParser
from gps_config import *
from pytz import timezone
import datetime
import urllib
import pg
import signal
import sys
import socket
import base64
import atexit
import urllib
import math

class CIDSpider:
    "CID Spider"
    query = 'laptop'
    total_results = 0
    price_limit = 10000
    intervals = [[] for row in range(price_limit)]
    current = 1
    upper_limit = 980
    lower_limit = 900
    c_index = 0
    
    def __init__(self):
        founded = 0
        self.log_f = open(log_output_file, 'a')
        socket.setdefaulttimeout(10)
        signal.signal(signal.SIGINT, self.quit_signal_handler)
        atexit.register(self.__destructor__)
        
        self.total_new_collected = 0        
        self.collected = self.get_collected_cids()
        
        r = self.crawl_page(self.query, 1)        
        self.intervals[self.current].append((self.price_limit, r.total_results))
        
        while self.current <= self.price_limit:
            (s_price, e_price, results) = self.get_next_price_interval()
            self.process_query(self.query, 1, int(math.ceil(results/10)), s_price, e_price)
        
    def __destructor__(self):
        self.log_f.close()
    
    def log(self, s):
        print s
        self.log_f.write(s + '\n')
    
    def quit_signal_handler(self, signal, frame):
        self.log(str(datetime.datetime.now(timezone('UTC'))) + ": CID collection process aborted.")
        sys.exit(0)
    
    def mount_url(self, query, page, c_index, tbs = ''):
        # http://50.116.1.34/spider/curl.php?url=aHR0cHM6Ly93d3cuZ29vZ2xlLmNvbS9zZWFyY2g/cT1sYXB0b3Amc3RhcnQ9MCZ0Ym09c2hvcCZobD1lbi1VUw==
        p = urllib.urlencode({
            'q': query,
            'hl': 'en-US',
            'tbm': 'shop',
            'start': page*10-10,
            'tbs': tbs
        })
        return c_files[c_index] + '?url=%s' % ('https://www.google.com/search?' + p).encode('base64', 'strict')
    
    def get_collected_cids(self):
        conn = pg.connect('itemcase', '50.116.1.34', 5432, None, None, 'postgres', 
                          base64.decodestring('ZmFzdE1vdmluZzJCcmVha0V2ZXJ5dGhpbmc='))
        r = conn.query('SELECT cid_product FROM product').getresult()
        conn.close()
        return r
    
    def get_next_price_interval(self):
        s = self.current
        e_index = 0
        e = self.intervals[s][e_index][0]
        total_results = self.intervals[s][e_index][1]
        break_point = s
        requests = 0
        
        while total_results > self.upper_limit or total_results < self.lower_limit:
            if total_results > self.upper_limit:
                e_break = int((break_point + e)/2)
                
                r = self.crawl_page(self.query, 1, s, e_break)
                
                self.intervals[s].append((e_break, r.total_results))
                self.intervals[e_break + 1].append((e, total_results - r.total_results))
                
                e = e_break
                total_results = r.total_results
                requests += 1
            else:
                next_s = e + 1
                if next_s < self.price_limit:
                    next_e = self.intervals[next_s][0][0]
                    next_total_results = self.intervals[next_s][0][1]
                    
                    break_point = next_s
                    e = next_e
                    total_results += next_total_results
                    
                    self.intervals[s].append((next_e, total_results))
                else:
                    break
                
            e_index += 1
        
        self.log(str(datetime.datetime.now(timezone('UTC'))) + ": " + str(requests) + " requests to define the interval.")
        
        r = (s, e, total_results)
        self.current = e + 1
        
        return r
        
    def process_query(self, query, s_page, e_page, s_price, e_price):
        self.log(str(datetime.datetime.now(timezone('UTC'))) + ": CID collection process started." +
            "Pages: " + str(e_page - s_page) + ". " + "Price Interval: " + str(s_price) + "-" + str(e_price) + ".")
        
        self.log(str(datetime.datetime.now(timezone('UTC'))) + ": Using bridge #" + str(self.c_index) + ".")
        
        conn = pg.connect('itemcase', '50.116.1.34', 5432, None, None, 'postgres', 
               base64.decodestring('ZmFzdE1vdmluZzJCcmVha0V2ZXJ5dGhpbmc='))
        
        for i in range(s_page, e_page):
            r = self.crawl_page(self.query, i, s_price, e_price)
            for c in r.cid:
                if not (c,) in self.collected:
                    self.collected.append((c,))
                    self.total_new_collected += 1                    
                    conn.query('INSERT INTO product VALUES(' + c + ', \'' + str(datetime.date.today()) + '\')')
        
        conn.close()
        
        self.log(str(datetime.datetime.now(timezone('UTC'))) + ": CID collection process finished.")            
        self.log(str(datetime.datetime.now(timezone('UTC'))) + ": " + str(self.total_new_collected) + " new CIDs was collected.")

    def crawl_page(self, query, page, s_price = 0, e_price = 0):
        crawled = False
        recovered = False
        
        while not crawled:
            if self.c_index < len(c_files):
                if recovered:
                    self.log(str(datetime.datetime.now(timezone('UTC'))) + ": Using bridge #" + str(self.c_index) + ".")
                    
                try:
                    if s_price == 0 or e_price == 0:
                        f = urllib.urlopen(self.mount_url(query, page, self.c_index))
                    else:
                        f = urllib.urlopen(self.mount_url(query, page, self.c_index,
                            'cat:328,price:1,ppr_min:' + str(s_price) + ',ppr_max:' + str(e_price)))
                except IOError as e:
                    self.log(str(datetime.datetime.now(timezone('UTC'))) + ": Bridge #" + str(self.c_index) + " is offline.")                    
                    self.c_index += 1
                    recovered = True
                    
                try:
                    parser = GPSProductListParser()
                    parser.feed(f.read().decode('UTF-8'))
                    parser.close()
                    if len(parser.cid) == 0:
                        raise Exception(1, 'Request error')
                    crawled = True
                except Exception as e:
                    if e.args[0] == 1:
                         self.log(str(datetime.datetime.now(timezone('UTC'))) + ": Bridge #" + str(self.c_index) + " has been blocked.")
                         self.c_index += 1
                         recovered = True
                    else:
                         self.log(str(datetime.datetime.now(timezone('UTC'))) + ": " + str(e.args[0]) + ".")
                         sys.exit()
            else:
                self.log(str(datetime.datetime.now(timezone('UTC'))) + ": All bridges are blocked/offline.")
                sys.exit()
                    
        return parser

cidSpider = CIDSpider()