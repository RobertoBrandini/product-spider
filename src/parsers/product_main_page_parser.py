from bs4 import BeautifulSoup

class ProductMainPageParser():
    Name = "ProductMainPageParser"
    
    # title
    pTitle = None
    # current price
    pPrice = None
    # rating meta data
    pCurrentRating = None; pWorstRating = None; pBestRating = None
    # number of reviews
    pReviews = None
    # summary
    pSummary = None
    # description
    pDescription = None
    # summary of features (in text)
    pFeatures = None
    # list of pictures
    pPictures = []
    
    def __init__(self, html):
        self.soup = BeautifulSoup(html)
        
        self.pTitle = self.soup.find(id="product-name").find("span").get_text()        
        
        pBasInfoDiv = self.soup.find(id="product-basic-info")
        
        self.pPrice = pBasInfoDiv.find_all("span", { "class" : "main-price" })[0].get_text()[1:]
        
        ratingDiv = pBasInfoDiv.find_all("div", { "class" : "product-rating-show-plusone" })[0]
        self.pCurrentRating = ratingDiv.find_all("meta", { "itemprop" : "ratingValue"  })[0]["content"]
        self.pBestRating = ratingDiv.find_all("meta", { "itemprop" : "bestRating"  })[0]["content"]
        self.pWorstRating = ratingDiv.find_all("meta", { "itemprop" : "worstRating"  })[0]["content"]
        
        self.pReviews = pBasInfoDiv.find_all("span", { "class" : "product-num-reviews" })[1]
        self.pReviews = self.pReviews.find_all("span", { "class" : "fl" })[0].get_text()
        self.pReviews = self.pReviews.split(" ")[0]
        
        self.pSummary = self.soup.find(id="product-info-cell")
        self.pSummary = self.pSummary.find_all("div", { "class" : "product-attr" })[0].get_text().strip()
        
        self.pDescription = self.soup.find(id="product-info-cell")
        self.pDescription = self.pDescription.find_all("div", { "class" : "product-desc" })[0].get_text().strip()
        
        self.pFeatures = self.soup.find(id="product-features").find_all("div", { "class" : "features" })[0].get_text().strip()