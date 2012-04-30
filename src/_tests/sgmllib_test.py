import sgmllib

class SpiderParser(sgmllib.SGMLParser):
    "A simple parser class."

    def parse(self, s):
        "Parse the given string 's'."
        self.feed(s)
        self.close()

    def __init__(self, verbose=0):
        "Initialise an object, passing 'verbose' to the superclass."

        sgmllib.SGMLParser.__init__(self, verbose)
        self.hyperlinks = []
        self.descriptions = []
        self.inside_a_element = 0
        self.starting_description = 0

    def start_a(self, attributes):
        "Process a hyperlink and its 'attributes'."

        for name, value in attributes:
            if name == "href":
                self.hyperlinks.append(value)
                self.inside_a_element = 1
                self.starting_description = 1

    def end_a(self):
        "Record the end of a hyperlink."

        self.inside_a_element = 0

    def handle_data(self, data):
        "Handle the textual 'data'."

        if self.inside_a_element:
            if self.starting_description:
                self.descriptions.append(data)
                self.starting_description = 0
            else:
                self.descriptions[-1] += data

    def get_hyperlinks(self):
        "Return the list of hyperlinks."

        return self.hyperlinks

    def get_descriptions(self):
        "Return a list of descriptions."

        return self.descriptions

import urllib

p = urllib.urlencode({
    'q': 'laptop',
    'hl': 'pt-BR',
    'tbm': 'shop',
    'oq': 'laptop',
    'start': '10',
    'tbm': 'shop',
    'aq': 'f',
    'aqi': '',
    'aql': '',
    'gs_sm': '3',
    'gs_upl': '1384l1811l0l1955l6l6l0l3l0l2l429l842l1.3-1.1l3l0#q=laptop',
    'hl': 'pt-BR',
    'sa': 'N',
    'tbs': 'vw:l',
    'ei': 'Z2N_T4b0OIWk8gTAzp3OBw',
    'ved': '0CK8BEL0N',
    'bav': 'on.2,or.r_gc.r_pw.r_qf.,cf.osb',
    'fp': '63fae10aeed527cf',
    'biw': '1680',
    'bih': '961',
    'start': '0'
})

p = 'https://www.google.com/search?' + p

f = urllib.urlopen('http://localhost/curl.php?url=%s' % p.encode('base64', 'strict'))
s = f.read().decode()

parser = SpiderParser()
parser.parse(s)

for hl in parser.get_hyperlinks():
    print hl

'''
http://www.google.com/products/catalog?cid=2748933489021536393
http://www.google.com/products/catalog?cid=2748933489021536393&os=tech-specs
http://www.google.com/products/catalog?cid=2748933489021536393&os=sellers#start=0
'''
