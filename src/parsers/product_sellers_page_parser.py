from bs4 import BeautifulSoup

class ProductSellersPageParser():
    Name = "ProductSellersPageParser"
    
    # sellers
    pSellers = []
    
    def __init__(self, html):
        self.soup = BeautifulSoup(html)