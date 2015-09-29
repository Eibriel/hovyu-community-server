import json

from main_server import app

from bson import ObjectId

class Products():
    def convert_products():
        #from eve.methods.post import post_internal

        stores_db = app.data.driver.db['stores']
        all_stores = stores_db.find()
        for store in all_stores:
            products_documents = []
            for product in store['products']:
                product_store = {
                    'product': ObjectId(product),
                    'properties': [],
                    'brand': '',
                    'price': ''
                }
                products_documents.append(product_store)
                print (products_documents)
            stores_db.update({'_id': store['_id']}, {'$set': {'products_properties': [], 'products_documents': products_documents}})

    def fix_products():
        stores_db = app.data.driver.db['stores']
        all_stores = stores_db.find()
        for store in all_stores:
            for product in store['products']:
                pr_type = type(product)
                #print (pr_type)

        products_db = app.data.driver.db['products']
        all_products = products_db.find()
        for product in all_products:
            pass
            #print (type(product['_id']))

        properties_db = app.data.driver.db['products_properties']
        all_properties = properties_db.find()
        for property_ in all_properties:
            pass
            #print (type(property_['_id']))

    def remove_places():
        places_db = app.data.driver.db['places']
        #all_places = places_db.remove({})
        #app.data.driver.db.repairDatabase()
        import os
        from pymongo import MongoClient
        client = MongoClient(os.environ['MONGODOCKERCOMPOSE_DB_1_PORT_27017_TCP_ADDR'])
        client.db['eve'].repairDatabase()

#    def pre_POST_products(request):
#        if request.args['admin_password'] != app.config['ADMIN_PASSWORD']:
#            abort(403)
#        del request.args['admin_password']

    def pre_GET_products(request, lookup):
        #Products.convert_products()
        #Products.fix_products()
        #Products.remove_places()

        if 'find_products' in request.args:
            lookup["name"] = {"$regex": request.args['find_products'], "$options": "i"}

    def post_GET_products(request, payload):
        products = app.data.driver.db['products']
        raw_payload = json.loads(payload.data.decode("utf-8"))
        #add_ids()
        items = None
        if '_items' in raw_payload:
            items = raw_payload.get('_items')
        elif raw_payload:
            items = [raw_payload]
        if items:
            for item in items:
                if 'inc_count' in request.args:
                    products.update({ "_id": ObjectId(item["_id"]) }, { "$inc": { "use_count": 1} })

