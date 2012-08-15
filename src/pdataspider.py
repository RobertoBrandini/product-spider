from parsers.product_main_page_parser import ProductMainPageParser
from parsers.product_sellers_page_parser import ProductSellersPageParser
from parsers.product_specs_page_parser import ProductSpecsPageParser
from user_exceptions.request_exception import RequestException
from config import *
from pytz import timezone
import datetime
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
    crawl_limit = 1500
    
    def __init__(self):
        self.log_f = open(pdataspider_logfile, 'a')
        socket.setdefaulttimeout(20)
        signal.signal(signal.SIGINT, self.quit_signal_handler)
        atexit.register(self.__destructor__)
        
        self.log("Product data collection process started (limit: " + str(self.crawl_limit) + " products).\n", True)
        
        crawled_products = 0
        disabled_products = 0
        
        for cid in self.get_outdated_cids():
            self.log("Collecting data from product #" + cid[0] + ".", False)
            
            # collection product basic information
            product_main_page = self.crawl_page( "MAIN_PAGE", [cid[0]] )
            
            if product_main_page.exists:                
                product_info = product_main_page.get_product_basic_info()
                crawled_products += 1
            else:
                self.log("This product no longer exists on Google Product Search and has been disabled in the database.\n", False)
                self.disable_product(cid[0])
                disabled_products += 1
                continue
            
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
            
        self.log("Data were collected from " + str(crawled_products) + " products.", True)
        self.log(str(disabled_products) + " products have been disabled.", True)
        
    def quit_signal_handler(self, signal, frame):
        self.log("Product data collection process aborted.", True)
        sys.exit(0)
        
    def __destructor__(self):
        self.log_f.close()
        
    def log(self, m, email):
        m = str(datetime.datetime.now(timezone('UTC'))).split('.')[0] + " (UTC): " + m
        if email: print m
        self.log_f.write(m + '\n')
        self.log_f.flush()
        os.fsync(self.log_f.fileno())
    
    def db_connect(self):
        return psycopg2.connect("dbname = 'itemcase' host='50.116.1.34' port=5432 user='postgres' password='" + 
                                base64.decodestring('ZmFzdE1vdmluZzJCcmVha0V2ZXJ5dGhpbmc=') + "'" )
    
    def store_product_data(self, cid, info, offers, specs):
        conn = self.db_connect()
        cur = conn.cursor()
        
        today = str(datetime.date.today())
        
        cur.execute("UPDATE product SET dt_last_crawled = %s WHERE cid_product = %s", (today, cid,))
        
        cur.execute("SELECT * FROM product_info WHERE cid_product = %s", (cid,))        
        r = cur.fetchone()
        
        # if this product doesn't have a product_info table, insert a new table
        if r == None:
            cur.execute("INSERT INTO product_info VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s )", 
                        (cid, today, info["title"], info["reviews"], info["summary"], info["description"], 
                         info["features"], info["best_rating"], info["worst_rating"],))
                
            self.log("The product info table was created.", False)
        # otherwise, update the existing table
        else:
            if info["title"] == None: title = r[2]
            else: title = info["title"]
            
            if info["reviews"] == None: reviews = r[3]
            else: reviews = info["reviews"]
            
            if info["best_rating"] == None: best_rating = r[7]
            else: best_rating = info["best_rating"]
            
            if info["worst_rating"] == None: worst_rating = r[8]
            else: worst_rating = info["worst_rating"]
            
            if info["summary"] == None: summary = r[4]
            else: summary = info["summary"]
            
            if info["description"] == None: description = r[5]
            else: description = info["description"]
            
            if info["features"] == None: features = r[6]
            else: features = info["features"]
            
            cur.execute("UPDATE product_info SET dt_updated = %s, ds_title = %s, nr_reviews = %s, nr_best_rating = %s, " +
                        "nr_worst_rating = %s, ds_summary = %s, ds_description = %s, ds_features = %s WHERE cid_product = %s", 
                        (today, info["title"], info["reviews"], info["best_rating"],
                         info["worst_rating"], info["summary"], info["description"], info["features"], cid,))
            
            self.log("Product info table updated.", False)
        
        if info["current_rating"] != None:
            cur.execute("SELECT cid_product, dt_collected FROM product_rating WHERE cid_product = %s AND dt_collected = %s", (cid, today,))
            r = cur.fetchone()
            
            if r == None:
                cur.execute("INSERT INTO product_rating VALUES (%s, %s, %s)", (cid, today, info["current_rating"],))
                self.log("A new rating has been set for this product.", False)
        
        new_stores = 0
        new_offers = 0
        closed_offers = 0
        
        for offer in offers:
            cur.execute("SELECT ds_domain FROM store WHERE ds_domain = %s", (offer["seller_domain"],))
            r = cur.fetchone()
            
            if r == None:
                cur.execute("INSERT INTO store VALUES (%s, %s, %s, %s)", (offer["seller_domain"], offer["seller_name"], 
                                                                          0, offer["seller_domain_type"],))
                new_stores += 1
                
            cur.execute("SELECT * FROM offer WHERE ds_url_offer = %s AND dt_end IS NULL", (offer["offer_url"],))
            r = cur.fetchone()
            
            if offer["offer_base_price"] == None: offer_base_price = None
            else: offer_base_price = float(offer["offer_base_price"])
                
            if offer["offer_total_price"] == None: offer_total_price = None
            else: offer_total_price = float(offer["offer_total_price"])
            
            insert_new_offer = False
            if r == None:
                insert_new_offer = True            
            elif r[6] != offer_base_price or r[7] != offer_total_price or r[8] != offer["offer_condition"]:
                    closed_offers += 1
                    id_offer = r[0]
                    cur.execute("UPDATE offer SET dt_end = %s WHERE id_offer = %s", (today, id_offer,))                    
                    insert_new_offer = True
            
            if insert_new_offer:
                cur.execute("INSERT INTO offer (id_offer, ds_domain_store, cid_product, ds_url_offer, dt_start, nr_base_price, " +
                            "nr_total_price, ds_condition) VALUES (DEFAULT, %s, %s, %s, %s, %s, %s, %s) RETURNING id_offer", 
                            (offer["seller_domain"], cid, offer["offer_url"], today, offer["offer_base_price"],
                             offer["offer_total_price"], offer["offer_condition"]))
                new_offers += 1
                
                last_id = cur.fetchone()
                
                if offer["offer_tax_shipping"] != None:
                    multiple_tax_shipping = offer["offer_tax_shipping"].split(",")                    
                    for tax_shipping in multiple_tax_shipping:
                        cur.execute("INSERT INTO tax_shipping (id_offer, ds_tax_shipping) VALUES (%s, %s)", 
                                    (last_id[0], tax_shipping,))
        
        if new_stores > 0:
            self.log(str(new_offers) + " IDs of new stores were collected.", False)
        
        if closed_offers > 0:
            self.log(str(closed_offers) + " offers for this product were closed.", False)
            
        if new_offers > 0:
            self.log(str(new_offers) + " new offers for this product were collected.", False)
        
        new_feature_groups = 0
        
        for feature_group in specs[0]:
            cur.execute("SELECT * FROM feature_group WHERE ds_name = %s AND id_category = %s", (feature_group, 328))
            r = cur.fetchone()
            
            if r == None:
                new_feature_groups += 1
                cur.execute("INSERT INTO feature_group VALUES (%s, %s)", (feature_group, 328,))                
        
        if new_feature_groups > 0:
            self.log(str(new_feature_groups) + " new feature groups were collected.", False)
        
        new_features = 0
        
        for feature in specs[1]:
            cur.execute("SELECT * FROM feature WHERE ds_name = %s AND ds_name_feature_group = %s AND id_category = %s", 
                        (feature[0], feature[1], 328))
            r = cur.fetchone()
            
            if r == None:
                new_features += 1
                cur.execute("INSERT INTO feature VALUES (%s, %s, %s)", (feature[0], feature[1], 328,))
        
        if new_features > 0:
            self.log(str(new_features) + " new features were collected.", False)
        
        new_specs = 0
        
        for spec in specs[2]:
            cur.execute("SELECT * FROM product_spec WHERE cid_product = %s AND ds_name_feature = %s AND " +
                        "ds_name_feature_group = %s AND id_category = %s", 
                        (cid, spec[1], spec[2], 328,))
            r = cur.fetchone()
            
            if r == None:
                new_specs += 1
                
                cur.execute("INSERT INTO product_spec VALUES (%s, %s, %s, %s, %s)", (cid, spec[1], spec[2], 328, spec[0],))
        
        if new_specs > 0:
            self.log(str(new_specs) + " new specifications for this product were collected.", False)
        
        conn.commit()
        cur.close()
        conn.close()
    
    def disable_product(self, cid):
        conn = self.db_connect()
        cur = conn.cursor()
        
        today = str(datetime.date.today())
        
        cur.execute("SELECT cid_product FROM product_info WHERE cid_product = %s", (cid,))
        r = cur.fetchone()
        
        if r != None:
            cur.execute("UPDATE offer SET dt_end = %s WHERE cid_product = %s", (today, cid,))
            cur.execute("UPDATE product_info SET dt_updated = %s WHERE cid_product = %s", (today, cid,))
        
        cur.execute("UPDATE product SET bl_exists = false WHERE cid_product = %s", (cid,))
        
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
        
        cur.execute('SELECT cid_product FROM product WHERE bl_exists = true ' + 
                    'ORDER BY dt_last_crawled ASC NULLS FIRST, dt_collected DESC LIMIT %s', (self.crawl_limit,))
        
        r = cur.fetchall()
        cur.close()
        conn.close()
        
        return r
    
    def crawl_page(self, page_type, args):
        crawled = False
        recovered = False
        first_failure_index = -1
        
        while not crawled:
            if self.c_index != first_failure_index:
                if recovered:
                    self.log("Using bridge #" + str(self.c_index) + ".", True)
                    
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
                    self.log("Bridge #" + str(self.c_index) + " is offline.", True)
                    self.c_index += 1
                    recovered = True
                
                except RequestException as e:
                    if e.value == 1:
                         self.log("Bridge #" + str(self.c_index) + " has been blocked.", True)
                         if first_failure_index == -1: first_failure_index = self.c_index
                         self.c_index += 1
                         recovered = True
                         
                finally:
                    if (len(c_files) - 1) < self.c_index: self.c_index = 0
                
            else:
                self.log("All bridges are blocked/offline.", True)
                sys.exit()
                    
        return parser
    
pDataSpider = PDataSpider()
