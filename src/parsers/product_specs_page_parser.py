from bs4 import BeautifulSoup

class ProductSpecsPageParser():
    Name = "ProductSpecsPageParser"
    
    def __init__(self):
        
        # current feature group
        self.c_feature_group = -1
        # feature groups
        self.feature_groups = []
        # features
        self.feature_types = []
        # product specifications
        self.specs = []
        # true when the html was not correctly parsed
        self.blocked = False
    
    def feed(self, html):
        self.soup = BeautifulSoup(html)
        
        self.blocked = False
        
        if self.soup.body == None:
            self.blocked = True
            return
        
        if self.soup.title == "302 Moved":
            self.blocked = True
            return
        
        section_inner = self.soup.find_all("div", { "class" : "section-inner" })
        
        if len(section_inner) > 0:
            rows = section_inner[0].find_all("tr")
            for row in rows:
                row_columns = row.find_all("td")
                if "table-header" in row_columns[0]["class"]:
                    self.c_feature_group += 1
                    self.feature_groups.append(row_columns[0].get_text().strip())
                else:
                    self.feature_types.append( [ row_columns[0].get_text().strip(), 
                                                 self.feature_groups[self.c_feature_group] ] )
                    self.specs.append( [ row_columns[1].get_text().strip(), 
                                         row_columns[0].get_text().strip(), 
                                         self.feature_groups[self.c_feature_group] ] )
    
    def get_product_specs(self):
        return [self.feature_groups, self.feature_types, self.specs]
    
    def crawled(self):
        return not self.blocked