from parsers.result_page_parser import ResultPageParser
from user_exceptions.request_exception import RequestException
from config import *
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
import os

class PIDSpider:
    "PIDSpider"
    
    query = 'laptop'
    total_results = 0
    price_limit = 10000
    intervals = [[] for row in range(price_limit)]
    current = 1
    upper_limit = 980
    lower_limit = 300
    c_index = 0
    
    def __init__(self):
        self.log_f = open(pidspider_logfile, 'a')
        socket.setdefaulttimeout(20)
        signal.signal(signal.SIGINT, self.quit_signal_handler)
        atexit.register(self.__destructor__)
        
        self.total_new_collected = 0
        self.collected = self.get_collected_cids()
        
        r = self.crawl_page(self.query, 1)
        self.intervals[self.current].append((self.price_limit, r.total_results))
        
        while self.current <= self.price_limit:
            (s_price, e_price, results) = self.get_next_price_interval()
            self.process_query(self.query, 1, int(math.ceil(results/10)), s_price, e_price)
        
        self.log("At this moment, the database contains " + str(len(self.collected)) + " unique CIDs.", True)
    
    def __destructor__(self):
        self.log_f.close()
    
    def log(self, m, email):
        m = str(datetime.datetime.now(timezone('UTC'))).split('.')[0] + " (UTC): " + m
        if email: print m
        self.log_f.write(m + '\n')
        self.log_f.flush()
        os.fsync(self.log_f.fileno())
    
    def quit_signal_handler(self, signal, frame):
        self.log("CID collection process aborted.", True)
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
        r = conn.query('SELECT cid_product, bl_exists FROM product').getresult()
        conn.close()
        return r
    
    def get_next_price_interval(self):
        s = self.current
        e_index = 0
        e = self.intervals[s][e_index][0]
        total_results = self.intervals[s][e_index][1]
        break_point = s
        requests = 0
        
        self.log("Initial price interval: " + str(s) + "-" + str(e) + " (" + str(total_results) + " results)", False)
        
        while total_results > self.upper_limit or total_results < self.lower_limit:            
            if total_results > self.upper_limit:
                if (e - break_point) == 1:
                    e = break_point
                    break
                
                e_break = int(round((break_point + e)/2))
                
                r = self.crawl_page(self.query, 1, s, e_break)
                
                self.intervals[s].append((e_break, r.total_results))
                self.intervals[e_break + 1].append((e, total_results - r.total_results))
                
                self.log("Break: " + str(s) + "-" + str(e) + " -> " + str(s) + "-" + str(e_break) + " (" + str(r.total_results) + " results)", False)
                
                e = e_break
                total_results = r.total_results
                requests += 1
            else:
                next_s = e + 1
                if next_s < self.price_limit:
                    next_e = self.intervals[next_s][0][0]
                    next_total_results = self.intervals[next_s][0][1]
                    
                    break_point = next_s
                    total_results += next_total_results
                    
                    self.log("Join: " + str(s) + "-" + str(e) + " -> " + str(s) + "-" + str(next_e) + " (" + str(total_results) + " results)", False)
                    
                    e = next_e
                    
                    self.intervals[s].append((next_e, total_results))
                else:
                    break
                
            e_index += 1
        
        self.log(str(requests) + " requests were performed to define the filters.", True)
        
        r = (s, e, total_results)
        self.current = e + 1
        
        return r
    
    def process_query(self, query, s_page, e_page, s_price, e_price):
        self.log("CID collection process started (pages: " + str(e_page - s_page + 1) + 
                 ", p. interval: " + str(s_price) + "-" + str(e_price) + ").", True)
        
        self.log("Using bridge #" + str(self.c_index) + ".", False)
        
        conn = pg.connect('itemcase', '50.116.1.34', 5432, None, None, 'postgres', 
               base64.decodestring('ZmFzdE1vdmluZzJCcmVha0V2ZXJ5dGhpbmc='))
        
        for i in range(s_page, e_page + 1):
            r = self.crawl_page(self.query, i, s_price, e_price)
            for c in r.cid:
                if not (c,'t') in self.collected:
                    if (c, 'f') in self.collected:
                        self.log('ATTENTION ==> The product #' + c + ' is enabled again.', True)
                    else:
                        self.collected.append((c, 't'))
                        self.total_new_collected += 1
                        self.log('CID #' + str(c) + " was collected.", False)
                        conn.query('INSERT INTO product (cid_product, dt_collected, id_category) VALUES(' + c + ', \'' + str(datetime.date.today()) + '\', 328)')
                    
        conn.close()
        
        self.log("CID collection process finished.", False)
        self.log(str(self.total_new_collected) + " new CIDs have been collected so far.\n", False)
    
    def crawl_page(self, query, page, s_price = 0, e_price = 0):
        crawled = False
        recovered = False
        first_failure_index = -1
        
        while not crawled:
            if self.c_index != first_failure_index:
                if recovered:
                    self.log("Using bridge #" + str(self.c_index) + ".", True)
                    
                try:
                    if s_price == 0 or e_price == 0:
                        f = urllib.urlopen(self.mount_url(query, page, self.c_index))
                    else:
                        f = urllib.urlopen(self.mount_url(query, page, self.c_index,
                            'cat:328,price:1,ppr_min:' + str(s_price) + ',ppr_max:' + str(e_price)))                        
                    parser = ResultPageParser()
                    parser.feed(f.read().decode('UTF-8'))
                    parser.close()
                    if len(parser.cid) == 0:
                        raise RequestException(1, 'Request error')
                    crawled = True
                
                except IOError as e:
                    self.log("Bridge #" + str(self.c_index) + " is offline.", True)                    
                    self.c_index += 1
                    recovered = True
                except RequestException as e:
                    if e.value == 1:
                         self.log("Bridge #" + str(self.c_index) + " has been blocked.", True)
                         if first_failure_index == -1: first_failure_index = self.c_index
                         self.c_index += 1
                         if (len(c_files) - 1) < self.c_index: self.c_index = 0
                         recovered = True
                    else:
                         self.log(str(e.args[0]) + ".", True)
                         sys.exit()
            else:
                self.log("All bridges are blocked/offline.", True)
                sys.exit()
                    
        return parser
    
pidSpider = PIDSpider()