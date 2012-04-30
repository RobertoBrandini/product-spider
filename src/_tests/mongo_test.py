from pymongo import Connection
c = Connection('50.116.1.34', 27017)
db = c.itemcase

print db.products.insert({'cid': 1})

for p in db.products.find():
    print p