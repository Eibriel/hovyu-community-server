import json
from eve import Eve
from bson import ObjectId

def pre_GET_stores(request, lookup):
    if 'products' not in request.args:
        return
    if request.args['products'] == '!all':
        return
    try:
        latitude = float(request.args['latitude'])
        longitude = float(request.args['longitude'])
    except:
        latitude = None
        longitude = None
        
    if request.args['products'] not in ['', '!all']:
        product = app.data.driver.db['products']
        lookup_ = {}
        products_search = request.args['products']
        products = []
        """for product_search in products_search:
            lookup_['_id'] = ObjectId(products_search)
            #lookup_['name'] = {"$regex": product_search}
            product_db = product.find(lookup_)
            if product_db:
                for p in product_db:
                    products.append(ObjectId(p['_id']))"""
        lookup["products"] = {'$in': [ObjectId(products_search)]}
    
    location_lookup = {'location': {"$near":
                           {"$geometry":
                              { "type": "Point" ,
                                "coordinates": [latitude , longitude]},
                             "$maxDistance": 300
                      }}}
    
    if latitude and longitude:
        # $near and $geometry don't work together
        #lookup["location"] = location_lookup
        stores = app.data.driver.db['stores']
        stores_db = stores.find(location_lookup)
        stores_ids = []
        for store in stores_db:
            stores_ids.append(store['_id'])
        lookup["_id"] = {'$in': stores_ids}
    print (lookup)


def post_GET_stores(request, payload):
    points_of_interest = app.data.driver.db['points_of_interest']
    items = json.loads(payload.data.decode("utf-8"))

    if '_items' in items:
        high_items = []
        common_items = []
    
        for item in items['_items']:
            point_list = []
            if 'location' in item and item['location']:
                location = item['location']['coordinates']
                lookup_ = { 'location' :
                             { "$near" :
                               { "$geometry" :
                                  { "type" : "Point" ,
                                    "coordinates" : [ location[0] , location[1] ] } ,
                                 "$maxDistance" : 300
                          } } }

                near_points = points_of_interest.find(lookup_)
                for point in near_points:
                    point_list.append(point['name'])
            item["near_points"] = point_list
            # Score
            if item['score']['count'] > 0:
                item['total_score'] = item['score']['sum'] / item['score']['count']
            else:
                item['total_score'] = 0
        
        for item in items['_items']:
            if item['highlight']:
                high_items.append(item)
            else:
                common_items.append(item)
        
        items = high_items+common_items
        
        payload.set_data(json.dumps(items).encode('utf-8'))


def pre_GET_products(request, lookup):
    if 'find_products' in request.args:
        lookup["name"] = {"$regex": request.args['find_products']}


def pre_GET_points_of_interest(request, lookup):
    if 'find_places' in request.args:
        lookup["name"] = {"$regex": request.args['find_places']}


app = Eve()


app.on_pre_GET_stores += pre_GET_stores
app.on_post_GET_stores += post_GET_stores

app.on_pre_GET_products += pre_GET_products
app.on_pre_GET_points_of_interest += pre_GET_points_of_interest


