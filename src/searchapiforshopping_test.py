import urllib.request
import urllib.parse
import json

# Search API for Searching - Search
#------------------------------------------------------------------------------ 
params = urllib.parse.urlencode({'key': 'AIzaSyAX3Dm43cyI2c6aU4YtFoVB5tMPP8AzjcI',
                                 'country': 'US',
                                 'q': 'laptop',
                                 'alt' : 'json', 
                                 'startIndex' : 1,
                                 'maxResults' : 100,
                                 'rankBy' : 'relevancy'})

search = urllib.request.urlopen("https://www.googleapis.com/shopping/search/v1/public/products?%s" % params)

# Search API for Searching - Product Lookup
#------------------------------------------------------------------------------ 
productSearch = urllib.request.urlopen("https://www.googleapis.com/shopping/search/v1/" + 
                              "public/products/5968952/gid/5103475116874981233?key=%s" % 
                              'AIzaSyAX3Dm43cyI2c6aU4YtFoVB5tMPP8AzjcI')

# Results
#------------------------------------------------------------------------------ 
searchResult = search.read().decode()
print(searchResult)

searchResultObj = json.loads(searchResult)
#print(searchResultObj)

productSearchResult = productSearch.read().decode()
#print(productSearchResult)

productSearchResultObj = json.loads(productSearchResult)
#print(productSearchResultObj)
