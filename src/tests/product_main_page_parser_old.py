from HTMLParser import HTMLParser
import sys

class ProductMainPageParser(HTMLParser):
    Name = "ProductMainPageParser"
    
    # levels
    levels = []; currentLevel = -1
    # title
    pTitle = None
    # current price
    pPrice = None
    # rating meta data
    pCurrentRating = None; pWorstRating = None; pBestRating = None
    # number of reviews
    pReviewsCount = None
    # summary
    pSummary = None
    # description
    pDescription = None
    # summary of features (in text)
    pFeatures = None
    # list of pictures
    pPictures = []
    
    def __init__(self): HTMLParser.__init__(self)
    
    def inLevels(self, parents):
        if len(self.levels) < len(parents): return False
        for i in range(len(parents)):
            if parents[i] == None: continue
            if self.levels[len(self.levels) - (1 + i)] != self.makeTagID(parents[i][0], parents[i][1]):
                return False
        return True
    
    def makeTagID(self, tag, attrs):
        attrs_str = []
        for attr in attrs:
            if attr[0] not in ['onclick', 'href']:
                attrs_str.append(str(attr[0]) + "=" + str(attr[1]))
        return tag + ":" + ','.join(attrs_str)
    
    def handle_starttag(self, tag, attrs):
        self.levels.append(self.makeTagID(tag, attrs))
        
        if (self.pCurrentRating == None and 
            self.inLevels([ None, None, None, None,
                           ['div', [('id', 'product-rating-plusone')]] ])):

            self.pCurrentRating = attrs[1][1]
            
        if (self.pWorstRating == None and 
            self.inLevels([ None, None, None,
                           ['div', [('id', 'product-rating-plusone')]] ])):

            self.pWorstRating = attrs[1][1]
            
        if (self.pBestRating == None and 
            self.inLevels([ None, None,
                           ['div', [('id', 'product-rating-plusone')]] ])):

            self.pBestRating = attrs[1][1]
        
    def handle_data(self, data):
        cLevel = len(self.levels) - 1
        
        if (self.pTitle == None and 
            self.inLevels([ ['span', [('class', 'main-title'), ('itemprop', 'name')]],
                            ['h1', [('id', 'product-name')]] ])):

            self.pTitle = data
            
        if (self.pPrice == None and 
            self.inLevels([ ['span', [('class', 'main-price')]],
                            ['span', [('class', 'product-price')]] ])):

            self.pPrice = data[1:].replace(',', '')
            
        if (self.pReviewsCount == None and 
            self.inLevels([ ['span', [('class', 'fl')]],
                            ['span', [('class', 'product-num-reviews')]], 
                            None, None, None, None, None,
                            ['span', [('class', 'fl')]],
                            ['span', [('class', 'product-num-reviews')]] ])):

            self.pReviewsCount = data.split(" ")[0]
        
        if (self.pSummary == None and 
            self.inLevels([ ['div', [('class', 'product-attr')]],
                            ['a', [] ], None, None,
                            ['div', [('class', 'popularity-badge')]] ])):

            self.pSummary = data
            
        if (self.pDescription == None and 
            self.inLevels([ ['div', [('class', 'product-desc')]],
                            ['div', [('class', 'product-desc-cont')]],
                            ['div', [('class', 'product-attr')]],
                            ['a', [] ], None, None,
                            ['div', [('class', 'popularity-badge')]] ])):

            self.pDescription = data
        
        if (self.pFeatures == None and 
            self.inLevels([ ['div', [('class', 'features')]], None,
                            ['div', [('id', 'product-features'), ('class', 'section')]] ])):
            
            self.pFeatures = data
        