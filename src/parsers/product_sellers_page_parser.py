from bs4 import BeautifulSoup

class ProductSellersPageParser():
    Name = "ProductSellersPageParser"
    
    # sellers
    product_offers = []
    has_next_page = False
    
    def __init__(self, html):
        self.soup = BeautifulSoup(html)
        
        rows = self.soup.find(id="ps-sellers-content").find_all("tr", { "class" : "online-sellers-row" })
        
        for row in rows:
            seller_name_spam = row.find_all("td", { "class" : "seller-col" })[0].find_all("span", { "class" : "seller-name" })[0]
            
            # collection store name and url
            name = seller_name_spam.a.get_text()
            url = seller_name_spam.a["href"]
            url = url.split("url?q=")[1].split("&usg=")[0]
            
            # collection store domain
            domain = row.find_all("td", { "class" : "rating-col" })[0].find_all("a", { "class" : "a" })
            
            if len(domain) > 0:
                domain = domain[0]["href"].split("mi=")[1].split("&q=")[0]
                has_page = True
            else:
                domain = url.replace("http://", "").replace("www.", "").split("/")[0]
                has_page = False
            
            # collecting "Condition"
            condition = row.find_all("td", { "class" : "condition-col" })[0].find_all("span", { "class" : "f" })[0].get_text()
            if len(condition) == 0: condition = ""            
            
            # collecting "Tax and shipping (estimated)"
            tax_shipping_spam = row.find_all("td", { "class" : "taxship-col" })[0].find_all("span", { "class" : "f" })
            
            if len(tax_shipping_spam) == 0:
                tax_shipping = ""
            else:                
                tax_shipping_nb = tax_shipping_spam[0].find_all("nobr")
                
                if len(tax_shipping_nb) > 0:
                    multiple_tax_shipping = []
                    for i in range(len(tax_shipping_nb)):
                        multiple_tax_shipping.append(tax_shipping_nb[i].get_text().strip())
                        tax_shipping = ', '.join(multiple_tax_shipping)
                elif len(tax_shipping_spam[0].get_text().strip()) > 0:
                    tax_shipping = tax_shipping_spam[0].get_text().strip()
                else:
                    tax_shipping = ""
            
            # collecting "Total price"
            total_price_spam = row.find_all("td", { "class" : "total-col" })[0].find_all("span", { "class" : "f" })
            
            if len(total_price_spam) == 0:
                total_price = ""
            else:
                total_price = total_price_spam[0].get_text().strip()[1:].split(".")[0].replace(",", "")
                
            # collecting "Base price"
            base_price_spam = row.find_all("td", { "class" : "price-col" })[0].find_all("span", { "class" : "base-price" })
            
            if len(base_price_spam) == 0:
                base_price = ""
            else:
                base_price = base_price_spam[0].get_text().strip()[1:].split(".")[0].replace(",", "")
                
            self.product_offers.append({ "seller_name" : name,
                                         "seller_domain" : domain,
                                         "seller_has_page" : has_page,
                                         "offer_url" : url,
                                         "offer_condition" : condition,
                                         "offer_tax_shipping" : tax_shipping,
                                         "offer_total_price" : total_price,
                                         "offer_base_price" : base_price
                                       })
            
        current_page = self.soup.find(id="online_stores_pagination").find(id="n-to-n-start").get_text().strip()
        current_page = current_page.split(" of ")
        
        if len(current_page) > 0:            
            if current_page[0].split(" - ")[1] < current_page[1]:
                self.has_next_page = True
        