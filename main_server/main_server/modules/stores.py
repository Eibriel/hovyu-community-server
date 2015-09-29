import json
import math
import random

from main_server import app

from bson import ObjectId


wid_chars = [ 0x1f31e, 0x1f33d, 0x1f34e, 0x1f433, 0x1f427,
              0x1f525, 0x2744,  0x2764,  0x1f332, 0x1f343,
              0x1f412, 0x1f407, 0x1f418, 0x1f416, 0x1f347,
              0x1f353, 0x1f6b2, 0x1f3b8, 0x1f3c0, 0x1f3b7,
              0x1f30d, 0x1f31d, 0x1f40d, 0x1f52d, 0x1f308]

def generate_ids():
    wid = ""
    stores_db = app.data.driver.db['stores']
    while True:
        for n in range(0,6):
            wid = "{0}{1}".format(wid, chr(random.choice(wid_chars)))
        stores = stores_db.find({'wid': wid}).count()
        if stores == 0:
            break
    while True:
        iid = random.randint(0,999999999)
        stores = stores_db.find({'iid': iid}).count()
        if stores == 0:
            break
    return wid, iid

def haversine(origin, destination):
    lon1, lat1 = origin
    lon2, lat2 = destination
    radius = 6371
    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c
    return d

class Stores():

    def on_insert_stores(items):
        for item in items:
            wid, iid = generate_ids()
            item['wid'] = wid
            item['iid'] = iid


    def add_ids():
        stores_db = app.data.driver.db['stores']
        stores = stores_db.find({'wid': {'$exists': False}, 'iid': {'$exists': False}})
        #stores = stores_db.find()
        for store in stores:
            wid, iid = generate_ids()
            stores_db.update({'_id': store['_id']}, {"$set":{'wid': wid, 'iid': iid}})


    def pre_GET_stores(request, lookup):
        if 'product' in request.args and request.args['product'] not in ['']:
            product_search = request.args['product']
            lookup["products"] = {'$in': [ObjectId(product_search)]}

        if 'activity' in request.args and request.args['activity'] not in ['']:
            activity_search = request.args['activity']
            activities_db = app.data.driver.db['activities']
            activity_db = activities_db.find_one({'_id': ObjectId(activity_search)})
            if activity_db:
                lookup["products"] = {'$in': activity_db['products']}

        try:
            longitude = float(request.args['longitude'])
            latitude = float(request.args['latitude'])
        except:
            longitude = None
            latitude = None

        if latitude and longitude:
            max_distance = 300
            attempts = 0
            while 1:
                location_lookup = {'location': {"$near":
                                       {"$geometry":
                                          { "type": "Point" ,
                                            "coordinates": [longitude, latitude]},
                                         "$maxDistance": max_distance
                                  }}}
                # $near and $geometry don't work together
                #lookup["location"] = location_lookup
                stores = app.data.driver.db['stores']
                stores_db = stores.find(location_lookup)
                stores_ids = []
                for store in stores_db:
                    stores_ids.append(store['_id'])
                lookup["_id"] = {'$in': stores_ids}
                if len(stores_ids) > 10:
                    break
                attempts = attempts + 1
                if attempts > 4:
                    break
                elif attempts > 2 and len(stores_ids) > 1:
                    break
                else:
                    max_distance = max_distance * 10

        if 'find_stores' in request.args:
            lookup["name"] = {"$regex": request.args['find_stores'], "$options": "i"}


    def post_GET_stores(request, payload):
        stores = app.data.driver.db['stores']
        # TODO pymongo.GEOSPHERE
        #stores.create_index([("location", "2dsphere")])
        points_of_interest = app.data.driver.db['points_of_interest']
        products_db = app.data.driver.db['products']
        products_properties_db = app.data.driver.db['products_properties']
        raw_payload = json.loads(payload.data.decode("utf-8"))
        #add_ids()
        items = None
        if '_items' in raw_payload:
            items = raw_payload.get('_items')
        elif raw_payload:
            items = [raw_payload]

        try:
            latitude = float(request.args['latitude'])
            longitude = float(request.args['longitude'])
        except:
            latitude = None
            longitude = None
        #if '_items' not in items:
        #    items = {'_items': [items]}

        if items:
            high_items = []
            common_items = []

            for item in items:
                # Points of interest
                point_list = []
                distance_klm = None
                if 'location' in item and item['location']:
                    location = item['location']['coordinates']
                    """lookup_ = { 'location' :
                                 { "$near" :
                                   { "$geometry" :
                                      { "type" : "Point" ,
                                        "coordinates" : [ location[0] , location[1] ] } ,
                                     "$maxDistance" : 300
                              } } }
                    near_points = points_of_interest.find(lookup_)
                    for point in near_points:
                        point_list.append(point['name'])"""
                    # Distance
                    if latitude and longitude:
                        distance_klm = haversine([longitude, latitude], location)
                item['distance_klm'] = distance_klm
                item["near_points"] = point_list
                # Products
                for product in item['products_documents']:
                    product_db = products_db.find({'_id': ObjectId(product['product'])})
                    product['name'] = product_db[0]['name']
                    properties_name = product['name']
                    for property_ in product['properties']:
                        property_db = products_properties_db.find({'_id': ObjectId(property_)})
                        properties_name = "{0} {1}".format(properties_name, property_db[0]['name'])
                    product['properties_name'] = properties_name
                # Score
                if 'score' in item and item['score']['count'] > 0:
                    item['total_score'] = item['score']['sum'] / item['score']['count']
                else:
                    item['total_score'] = 0
                # Fix exact_location
                if 'exact_location' not in item:
                    item['exact_location'] = False
                # Fix client_pictures
                if 'client_pictures' not in item:
                    item['client_pictures'] = []
                # Fix process description
                if 'process_description' not in item:
                    item['process_description'] = ""
                # Views
                if 'inc_views' in request.args:
                    stores.update({ "_id": ObjectId(item["_id"]) }, { "$inc": { "views": 1} })
            
            if items[0]['distance_klm']:
                from operator import itemgetter
                sorted_items = sorted(items, key=itemgetter('distance_klm'))
                items = sorted_items
    
            for item in items:
                if 'highlight' in item and item['highlight']:
                    high_items.append(item)
                else:
                    common_items.append(item)

            items = high_items+common_items

            raw_payload = {'_items': items}
            payload.set_data(json.dumps(raw_payload).encode('utf-8'))
