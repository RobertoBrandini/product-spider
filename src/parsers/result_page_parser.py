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
            unknow = false
            if self.soup.title:
                if self.soup.title.get_text() != "302 Moved" and (self.soup.body.h1 and self.soup.body.h1.get_text() != "Server Error"):
                    unknow = true
            
            if unknow:
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
        
        try:
            self.total_results = int(div_total_results.get_text().split(" ")[-2].replace(",", ""))
        except IndexError as e:
            print "Unknown total results! Here's the div:\n"
            print div_total_results.get_text() + "\n"
        
        links = self.soup.find(id="ires").find_all("h3", {"class" : "r"})
        
        for link in links:
            if (len(link.find("a")["href"].split('cid=')) > 1):
                cid = link.find("a")["href"].split('cid=')[1]
                try:
                    long(cid)
                    self.product_cids.append(cid)
                except ValueError:
                    print("Invalid CID: " + cid)
            else:
                print "Unknown product url: " + link.find("a")["href"]
        
    def get_product_cids(self):
        return self.product_cids
    
    def get_total_results(self):
        return self.total_results
        
    def crawled(self):
        return not self.blocked
