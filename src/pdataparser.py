from HTMLParser import HTMLParser

class PDataParser(HTMLParser):
    Name = "PDataParser"
    
    def __init__(self):
        HTMLParser.__init__(self)