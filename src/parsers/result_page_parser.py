from bs4 import BeautifulSoup

class ResultPageParser():
    Name = "ResultPageParser"
    
    def __init__(self):        
        # product cids
        self.product_cids = []
        # total results
        self.total_results = None
        # true when the html was not correctly parsed
        self.blocked = False
        
    def feed(self, html):
        self.soup = BeautifulSoup(html)
                
        self.blocked = False
        
        if self.soup.body == None:
            self.blocked = True
            return
        
        links = self.soup.find(id="ires").find_all("h3", {"class" : "r"})
        
        for link in links:
            self.product_cids.append(link.find("a")["href"].split('cid=')[1])
        
        div_total_results = self.soup.find(id="subform_ctrl").find_all("div")[1]
        self.total_results = int(div_total_results.get_text().split(" ")[-2].replace(",", ""))
        
    def get_product_cids(self):
        return self.product_cids
    
    def get_total_results(self):
        return self.total_results
        
    def crawled(self):
        return not self.blocked
