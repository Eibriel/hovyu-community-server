import json

from main_server import app

class Store_stats():
    def post_GET_store_stats(request, payload):
        stores = app.data.driver.db['stores']
        #print (payload.data)
        items = json.loads(payload.data.decode("utf-8"))
        #lookup = {
        #    '$group': {
        #        '_id': None,
        #        'total': {'$sum': '$real_amount'}
        #    }
        #}
        stores_db = stores.find({})
        total = 0
        total = stores_db.count()
        #if len(stores_db)>0:
        #    total = payments_db['result'][0]['total']

        items['_items'] = [{
            'total': total
        }]
        payload.set_data(json.dumps(items).encode('utf-8'))
