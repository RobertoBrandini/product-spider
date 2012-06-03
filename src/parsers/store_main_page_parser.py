from bs4 import BeautifulSoup

class StoreMainPageParser():
    Name = "StoreMainPageParser"
    
    # sellers
    pSellers = []
    
    def __init__(self, html):
        self.soup = BeautifulSoup(html)