from parsers.product_main_page_parser import ProductMainPageParser
from parsers.product_sellers_page_parser import ProductSellersPageParser
from parsers.product_specs_page_parser import ProductSpecsPageParser
from user_exceptions.request_exception import RequestException
from config import *
from pytz import timezone
import datetime
import urllib
import psycopg2
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
        
        for cid in self.get_outdated_cids():
            print cid[0]
            
            # collection product basic information
            product_info = self.crawl_page( "MAIN_PAGE", [cid[0]] ).get_product_basic_info()
            
            # collecting product offers
            product_offers = []; page = 0; has_next_page = True
            
            while has_next_page:                
                r = self.crawl_page( "SELLERS_PAGE", [cid[0], page] )
                page += 25
                has_next_page = r.has_next_page
                
            product_offers = product_offers + r.get_product_offers()
            
            # collecting product specifications
            product_specs = self.crawl_page( "SPECS_PAGE", [cid[0]] ).get_product_specs()
            
            self.store_product_data(cid[0], product_info, product_offers, product_specs)
            
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
    
    def db_connect(self):
        return psycopg2.connect("dbname = 'itemcase' host='50.116.1.34' port=5432 user='postgres' password='" + 
                                base64.decodestring('ZmFzdE1vdmluZzJCcmVha0V2ZXJ5dGhpbmc=') + "'" )
    
    def store_product_data(self, cid, info, offers, specs):        
        conn = self.db_connect()
        cur = conn.cursor()
        
        import pdb; pdb.set_trace()
        
        today = str(datetime.date.today())
        
        cur.execute("SELECT * FROM product_info WHERE cid_product = %s", (cid,))        
        r = cur.fetchone()
        
        # if this product doesn't have a product_info table, insert a new table
        if r == None:
            cur.execute("INSERT INTO product_info VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s )", 
                        (cid, today, info["title"], info["reviews"], info["best_rating"],
                         info["worst_rating"], info["summary"], info["description"], info["features"],))
        # otherwise, update the existing table
        else:
            if info["title"] == None: title = r[2]
            else: title = info["title"]
            
            if info["reviews"] == None: reviews = r[3]
            else: reviews = info["reviews"]
            
            if info["best_rating"] == None: best_rating = r[4]
            else: best_rating = info["best_rating"]
            
            if info["worst_rating"] == None: worst_rating = r[5]
            else: worst_rating = info["worst_rating"]
            
            if info["summary"] == None: summary = r[6]
            else: summary = info["summary"]
            
            if info["description"] == None: description = r[7]
            else: description = info["description"]
            
            if info["features"] == None: features = r[8]
            else: features = info["features"]
            
            cur.execute("UPDATE product_info SET ( dt_updated = %s, ds_title = %s, nr_reviews = %s, nr_best_rating = %s, " +
                        "nr_worst_rating = %s, ds_summary = %s, ds_description = %s, ds_features = %s WHERE cid_product = %s )", 
                        (today, info["title"], info["reviews"], info["best_rating"],
                         info["worst_rating"], info["summary"], info["description"], info["features"], cid,))
        
        cur.execute("SELECT dt_collected FROM product_rating WHERE cid_product = %s", (cid,))
        r = cur.fetchone()
        
        if r == None or date.strftime(r[0], '%Y-%m-%d') != today:
            cur.execute("INSERT INTO product_rating VALUES (%s, %s, %s)", (cid, today, info["current_rating"],))
        
        for offer in offers:
            cur.execute("SELECT ds_domain FROM store WHERE ds_domain = %s", (offer["seller_domain"],))
            r = cur.fetchone()
            
            if r == None:
                cur.execute("INSERT INTO store (%s, %s, %s, %s)", (offer["seller_domain"], offer["seller_name"], 
                                                                   offer["seller_has_page"], 0,))
                
            cur.execute("SELECT * FROM offer WHERE ds_url_offer = %s AND dt_end IS NOT NULL", (offer["offer_url"],))
            r = cur.fetchone()
            
            insert_new_offer = False
            if r == None:
                insert_new_offer = True            
            elif r[5] != offer["offer_base_price"] or r[6] != offer["offer_total_price"] or r[7] != offer["offer_condition"]:
                    cur.execute("UPDATE offer SET dt_end = %s WHERE ds_url_offer = %s", (today, offer["offer_url"],))
                    cur.execute("INSERT INTO offer ")
                    insert_new_offer = True
                    
            if insert_new_offer:
                cur.execute("INSERT INTO offer VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", 
                            (offer["offer_url"], offer["seller_domain"], cid, today, None, offer["offer_base_price"],
                             offer["offer_total_price"], offer["offer_condition"]))
                if offer["offer_tax_shipping"] != None:
                    multiple_tax_shipping = offer["offer_tax_shipping"].split(",")
                    for tax_shipping in multiple_tax_shipping:
                        cur.execute("SELECT ds_url_offer FROM tax_shipping WHERE ds_url_offer = %s AND ds_tax_shipping = %s",
                                    (offer["offer_url"], tax_shipping,))
                        r = cur.fetchone()
                        
                        if r == None:
                            cur.execute("INSERT INTO tax_shipping VALUES (%s, %s)", (offer["offer_url"], tax_shipping,))
                            
        for feature_group in specs[0]:
            cur.execute("SELECT * FROM feature_group WHERE ds_name = %s AND id_category = %s", (feature_group, 328))
            r = cur.fetchone()
            
            if r == None:
                cur.execute("INSERT INTO feature_group VALUES (%s, %s)", (feature_group, 328,))
        
        for feature in specs[1]:
            cur.execute("SELECT * FROM feature WHERE ds_name = %s AND ds_name_feature_group = %s AND id_category = %s", 
                        (feature[0], feature[1], 328))
            r = cur.fetchone()
            
            if r == None:
                cur.execute("INSERT INTO feature VALUES (%s, %s, %s)", (feature[0], feature[1], 328,))
        
        for spec in specs[2]:
            cur.execute("SELECT * FROM product_spec WHERE cid_product = %s, ds_name_feature = %s AND " +
                        "ds_name_feature_group = %s AND id_category = %s", 
                        (spec[0], spec[1], spec[2], 328))
            r = cur.fetchone()
            
            if r == None:
                cur.execute("INSERT INTO product_spec VALUES (%s, %s, %s, %s, %s)", (cid, spec[1], spec[2], 328, spec[0],))
        
        conn.commit()
        cur.close()
        conn.close()
        
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
        
    def mount_specs_page_url(self, cid, c_index):
        p = urllib.urlencode({
            'cid': cid
        })
        return c_files[c_index] + '?url=%s' % ('http://www.google.com/products/catalog?' + p + "&os=tech-specs").encode('base64', 'strict')
        
    def get_outdated_cids(self):
        conn = self.db_connect()
        cur = conn.cursor()
        
        cur.execute('SELECT cid_product FROM product ORDER BY dt_last_crawled DESC, dt_collected DESC LIMIT 10')
        
        r = cur.fetchall()        
        cur.close()
        conn.close()
        
        return r
    
    def crawl_page(self, page_type, args):
        crawled = False
        recovered = False
        
        while not crawled:
            if self.c_index < len(c_files):
                if recovered:
                    self.log("Using bridge #" + str(self.c_index) + ".")
                    
                try:
                    if page_type == "MAIN_PAGE":
                        f = urllib.urlopen(self.mount_main_page_url(args[0], self.c_index))
                        parser = ProductMainPageParser()
                        parser.feed(f.read())
                    elif page_type == "SELLERS_PAGE":
                        f = urllib.urlopen(self.mount_sellers_page_url(args[0], args[1], self.c_index))
                        parser = ProductSellersPageParser()
                        parser.feed(f.read())
                    else:
                        f = urllib.urlopen(self.mount_specs_page_url(args[0], self.c_index))
                        parser = ProductSpecsPageParser()
                        parser.feed(f.read())
                    
                    if not parser.crawled():
                        raise RequestException(1, 'Request error')
                        
                    crawled = True
                
                except IOError as e:
                    self.log("Bridge #" + str(self.c_index) + " is offline.")                    
                    self.c_index += 1
                    recovered = True                
                
                except RequestException as e:
                    if e.value == 1:
                         self.log("Bridge #" + str(self.c_index) + " has been blocked.")
                         self.c_index += 1
                         recovered = True
                
            else:
                self.log("All bridges are blocked/offline.")
                sys.exit()
                    
        return parser
    
pDataSpider = PDataSpider()