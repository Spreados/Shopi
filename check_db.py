from pymongo import MongoClient
import os

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
client = MongoClient(MONGO_URL)
db = client.petstore

print('=== MongoDB Collections ===')
collections = db.list_collection_names()
print('Collections:', collections)

print('\n=== Products Collection ===')
products = list(db.products.find({}, {'_id': 0}))
print('Products count:', len(products))
for p in products:
    print('- {} (${})'.format(p['name'], p['price']))

print('\n=== Orders Collection ===')
orders = list(db.orders.find({}, {'_id': 0}))
print('Orders count:', len(orders))
for o in orders:
    print('- Order {}: {} items, Total: ${}'.format(o['id'], len(o['items']), o['total']))

print('\n=== Carts Collection ===')
carts = list(db.carts.find({}, {'_id': 0}))
print('Active carts count:', len(carts))