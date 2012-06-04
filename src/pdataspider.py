from parsers.product_sellers_page_parser import ProductSellersPageParser
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

class PDataSpider:
    "PDataSpider"
    
    c_index = 0
    
    def __init__(self):
        self.log_f = open(log_output_file, 'a')
        socket.setdefaulttimeout(20)
        signal.signal(signal.SIGINT, self.quit_signal_handler)
        atexit.register(self.__destructor__)
        
        product_info = self.crawl_page(self.mount_main_page_url(2748933489021536393, self.c_index))
        
        product_offers = []        
        page = 0
        r = self.crawl_page(self.mount_sellers_page_url(2748933489021536393, page, self.c_index))
        while r.has_next_page:
            page += 25
            r = self.crawl_page(self.mount_sellers_page_url(2748933489021536393, page, self.c_index))        
        product_offers = product_offers + r.product_offers
        
        print product_offers
        
    def quit_signal_handler(self, signal, frame):
        self.log("Product data collection process aborted.")
        sys.exit(0)
        
    def __destructor__(self):
        self.log_f.close()
        
    def log(self, m):
        m = str(datetime.datetime.now(timezone('UTC'))).split('.')[0] + " (UTC): " + m
        print m
        self.log_f.write(m + '\n')
        self.log_f.flush()
        os.fsync(self.log_f.fileno())
        
    def mount_main_page_url(self, cid, c_index):
        p = urllib.urlencode({
            'cid': cid
        })
        return c_files[c_index] + '?url=%s' % ('http://www.google.com/products/catalog?' + p).encode('base64', 'strict')
        
    def mount_sellers_page_url(self, cid, page, c_index):
        p = urllib.urlencode({
            'cid': cid,
            'start' : page
        })
        return c_files[c_index] + '?url=%s' % ('http://www.google.com/products/catalog?' + p + "&os=sellers").encode('base64', 'strict')
        
    def crawl_page(self, url):
        crawled = False
        recovered = False
        
        while not crawled:            
            if self.c_index < len(c_files):
                if recovered:
                    self.log("Using bridge #" + str(self.c_index) + ".")
                    
                try:
                    f = urllib.urlopen(url)                     
                    parser = ProductSellersPageParser(f.read())
                    if len(parser.product_offers) == 0:
                        raise Exception(1, 'Request error')
                    crawled = True
                
                except IOError as e:
                    self.log("Bridge #" + str(self.c_index) + " is offline.")                    
                    self.c_index += 1
                    recovered = True
                
                except Exception as e:
                    if e.args[0] == 1:
                         self.log("Bridge #" + str(self.c_index) + " has been blocked.")
                         self.c_index += 1
                         recovered = True
                    else:
                         self.log(str(e.args[0]) + ".")
                         sys.exit()                
                
            else:
                self.log("All bridges are blocked/offline.")
                sys.exit()
                    
        return parser
    
pDataSpider = PDataSpider()