from HTMLParser import HTMLParser

class GPSProductListParser(HTMLParser):
    Name = "GPSProductListParser"
    
    def __init__(self):
        HTMLParser.__init__(self)
        self.inWrap = {'res': False, 'ires': False}
        self.inP  = False
        self.inPTit = False
        self.wrapDivLevel = 0
        self.currentP = 0
        self.cid = []
    
    # return True when the parser is inside the product list wrap
    def isInWrap(self):
        return self.inWrap['res'] and self.inWrap['ires'] and self.wrapDivLevel > 0
    
    def handle_starttag(self, tag, attrs):
        # sets the inWrap to [True, True] when the parser enters in a product list wrap and
        # ajusts the wrap div level
        if tag == 'div' and attrs and attrs[0][0] == 'id' and attrs[0][1] in ['res', 'ires']:
            self.inWrap[attrs[0][1]] = True
            self.wrapDivLevel += 1        
        # sets inP to True when the parser enters in a product div
        elif tag == 'li' and attrs and attrs[0][0] == 'class' and attrs[0][1] == 'g':
            self.inP = True        
        # sets inPTit to True when the parser enters in a product title div
        elif tag == 'h3' and self.inP and attrs and attrs[0][0] == 'class' and attrs[0][1] == 'r':
            self.inPTit = True        
        # appends a cid to the cid list
        elif tag == 'a' and self.inPTit:
            self.cid.append(attrs[0][1].split('cid=')[1])
        # ajusts the wrap div level
        elif tag == 'div' and self.isInWrap():
            self.wrapDivLevel += 1
        
    def handle_endtag(self, tag):
        # ajusts the wrap div level
        if tag == 'div' and self.isInWrap():
            self.wrapDivLevel -= 1
        # sets the inP to False when the parser leaves a product div
        elif tag == 'li' and self.inP:
            self.inP = False
        # sets the inPTit to False when the parser leaves a product title div
        elif tag == 'h3' and self.inPTit:
            self.inPTit = False
