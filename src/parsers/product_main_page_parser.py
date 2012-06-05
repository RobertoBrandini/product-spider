from bs4 import BeautifulSoup

class ProductMainPageParser():
    Name = "ProductMainPageParser"
    
    def __init__(self):
        
        # product basic info
        self.product_info = None
        # list of pictures
        self.product_pictures = []
        # true when the html was not correctly parsed
        self.blocked = False
        
    def feed(self, html):
        self.soup = BeautifulSoup(html)
                
        self.blocked = False
        
        if self.soup.body == None:
            self.blocked = True
            return
        
        # setting the product title
        title = self.soup.find(id="product-name").find("span").get_text()
        if title == "":  title = None
        
        product_basic_info_div = self.soup.find(id="product-basic-info")
        
        # setting the product rating values
        rating_div = product_basic_info_div.find_all("div", { "class" : "product-rating-show-plusone" })        
        if len(rating_div) > 0:
            current_rating = rating_div[0].find_all("meta", { "itemprop" : "ratingValue"  })[0]["content"]
            best_rating = rating_div[0].find_all("meta", { "itemprop" : "bestRating"  })[0]["content"]
            worst_rating = rating_div[0].find_all("meta", { "itemprop" : "worstRating"  })[0]["content"]
        else:
            current_rating = None; best_rating = None; worst_rating = None
        
        # setting the product review count
        product_reviews_div = product_basic_info_div.find_all("span", { "class" : "product-num-reviews" })
        if len(product_reviews_div) > 0:
            reviews_count = product_reviews_div[1].find_all("span", { "class" : "fl" })[0].get_text().split(" ")[0]
        else:
            reviews_count = None
        
        # settings the product summary
        product_summary_div = self.soup.find(id="product-info-cell").find_all("div", { "class" : "product-attr" })
        if len(product_summary_div) > 0:
            summary = product_summary_div[0].get_text().strip()
            if summary == "": summary = None
        else:
            summary = None
        
        # setting the product description
        description = self.soup.find(id="product-info-cell")
        description = description.find_all("div", { "class" : "product-desc" })[0].get_text().strip()
        if description == "": description = None
        
        # setting the product features
        features_div = self.soup.find(id="product-features")
        if features_div != None:
            features = features_div.find_all("div", { "class" : "features" })[0].get_text().strip()
            if features == "": features = None
        else:
            features = None
        
        self.product_info = { "title" : title,
                              "current_rating" : current_rating,
                              "best_rating" : best_rating,
                              "worst_rating" : worst_rating,
                              "reviews" : reviews_count,
                              "summary" : summary,
                              "description" : description,
                              "features" : features }
        
    def get_product_basic_info(self):
        return self.product_info
        
    def crawled(self):
        return not self.blocked