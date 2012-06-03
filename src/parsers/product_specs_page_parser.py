from bs4 import BeautifulSoup

class ProductSpecsPageParser():
    Name = "ProductSpecsPageParser"
    
    # sellers
    pSellers = []
    
    def __init__(self, html):
        self.soup = BeautifulSoup(html)