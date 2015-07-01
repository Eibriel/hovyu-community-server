import json

from main_server import app

class Payment_stats():
    def post_GET_payment_stats(request, payload):
        payments = app.data.driver.db['payments']
        #print (payload.data)
        items = json.loads(payload.data.decode("utf-8"))
        lookup = {
            '$group': {
                '_id': None,
                'total': {'$sum': '$real_amount'}
            }
        }
        payments_db = payments.aggregate([lookup])
        total = 0
        if len(payments_db['result'])>0:
            total = payments_db['result'][0]['total']

        items['_items'] = [{
            'total': total
        }]
        payload.set_data(json.dumps(items).encode('utf-8'))
