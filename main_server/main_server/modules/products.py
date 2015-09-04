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
            print store['products']

    def pre_GET_products(request, lookup):
        #Products.convert_products()
        Products.fix_products()
        if 'find_products' in request.args:
            lookup["name"] = {"$regex": request.args['find_products'], "$options": "i"}