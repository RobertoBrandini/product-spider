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
        
        if not self.soup.body:
            self.blocked = True
            return
        
        div_total_results = self.soup.find(id="subform_ctrl")
        
        if div_total_results == None:
            if not self.soup.title or self.soup.title.get_text() != "302 Moved":
                print "Unknown page! Here's the html:\n"
                print html + "\n"
            self.blocked = True
            return
        
        # this an exception! sometimes, the "advanced search div" is not returned in the html
        # making the "total results div" be the first one
        if len(div_total_results.find_all("div")) >= 2:        
            div_total_results = div_total_results.find_all("div")[1]
        else:
            div_total_results = div_total_results.find_all("div")[0]
            
        self.total_results = int(div_total_results.get_text().split(" ")[-2].replace(",", ""))        
        
        links = self.soup.find(id="ires").find_all("h3", {"class" : "r"})
        
        for link in links:
            if (len(link.find("a")["href"].split('cid=')) > 1):
                self.product_cids.append(link.find("a")["href"].split('cid=')[1])
            else:
                print "Unknown link! Here's the link:\n"
                print link.find("a")["href"]
        
    def get_product_cids(self):
        return self.product_cids
    
    def get_total_results(self):
        return self.total_results
        
    def crawled(self):
        return not self.blocked
