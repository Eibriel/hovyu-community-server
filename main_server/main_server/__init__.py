import json
from eve import Eve
from bson import ObjectId

Eve.debug = True

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
    
    if 'place_id' in request.args:
        place_id = request.args['place_id']
    else:
        place_id = None
        
    if place_id:
        lookup["place.place_id"] = place_id
    #print (lookup)


def post_GET_stores(request, payload):
    stores = app.data.driver.db['stores']
    # TODO pymongo.GEOSPHERE
    stores.create_index([("location", "2dsphere")])
    points_of_interest = app.data.driver.db['points_of_interest']
    items = json.loads(payload.data.decode("utf-8"))

    if '_items' not in items:
        items = {'_items': [items]}

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
            # Fix exact_location
            if 'exact_location' not in item:
                item['exact_location'] = False
            # Fix place
            if 'place' not in item:
                item['place'] = None
        
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
    points_of_interest = app.data.driver.db['points_of_interest']
    # TODO pymongo.GEOSPHERE
    points_of_interest.create_index([("location", "2dsphere")])
    if 'find_places' in request.args:
        lookup["name"] = {"$regex": request.args['find_places']}


def post_GET_payment_stats(request, payload):
    payments = app.data.driver.db['payments']
    #print (payload.data)
    items = json.loads(payload.data.decode("utf-8"))
    lookup = {
        '$group': {
            '_id': None,
            'total': {'$sum': '$amount'}
        }
    }
    payments_db = payments.aggregate([lookup])
    total = payments_db['result'][0]['total']
    
    items['_items'] = [{
        'total': total
    }]
    payload.set_data(json.dumps(items).encode('utf-8'))


def rebuild_places():
    from eve.methods.post import post_internal
    places_db = app.data.driver.db['places']
    
    from main_server.config import argentina
    for relation in argentina['elements']:
        name = relation['tags'].get('name')
        type_ = relation['tags'].get('place')
        osm_id = relation['id']
        country = relation['tags'].get('is_in:country')
        state = relation['tags'].get('is_in:state')
        city = relation['tags'].get('is_in:city')
        latitude = relation['lat']
        longitude = relation['lon']
        
        if not name:
            continue

        place = {
            'osm_id': osm_id,
            'name': name,
            'type': type_,
            'is_in': {
                'country': country,
                'state': state,
                'city': city
            },
            'location': {"type":"Point","coordinates":[latitude, longitude]}
        }
        print (place)
        
        place_db = places_db.find_one({'osm_id': osm_id})
        if place_db:
            print ("")
            continue
        
        r = post_internal('places', place)
        #print (r)
        print ("POST")


def interpolate_places():
    from eve.methods.patch import patch_internal
    places_db = app.data.driver.db['places']
    places = places_db.find({'is_in.city': None, 'is_in.state': None})
    print(places.count())
    for place in places:
        #print (place)
        location = place['location']['coordinates']
        lookup_ = { 'location' :
                     { "$near" :
                       { "$geometry" :
                          { "type" : "Point" ,
                            "coordinates" : [ location[0] , location[1] ] } ,
                         "$maxDistance" : 30000
                  } } }
        places_near = places_db.find(lookup_)
        id_list = []
        nearest_place = None
        for place_near in places_near:
            if place_near['is_in']['city'] or place_near['is_in']['state'] or place_near['is_in']['country']:
                nearest_place = place_near
                break
                #id_list.append(place_near['_id'])
        #lookup_ = {"_id": {"$in": id_list}}
        #place_near = places_db.find_one(lookup_)
        if not nearest_place:
            print ("continue")
            continue
        near_place = {
            'name': nearest_place['name'],
            'city': nearest_place['is_in']['city'],
            'state': nearest_place['is_in']['state'],
            'country': nearest_place['is_in']['country']
        }
        #print ("{0} ({1})".format(place['name'], nearest_place['name']))
        #print ("Patch {0}".format(place['_id']))
        #r = patch_internal("places", payload={"near_place": near_place}, lookup={'_id': place['_id'], '_etag': place['_etag']})
        print (near_place)
        places_db.update({'_id': place['_id'], '_etag': place['_etag']}, {"$set": {"near_place": near_place}})
        


def pre_GET_places(request, lookup):
    places = app.data.driver.db['places']
    # TODO pymongo.GEOSPHERE
    places.create_index([("location", "2dsphere")])
    if 'rebuild_places' in request.args:
        rebuild_places()
    if 'interpolate_places' in request.args:
        interpolate_places()
    if 'find_places' in request.args:
        lookup["name"] = {"$regex": request.args['find_places'], "$options": "i"}


app = Eve()

app.on_pre_GET_places += pre_GET_places

app.on_pre_GET_stores += pre_GET_stores
app.on_post_GET_stores += post_GET_stores

app.on_pre_GET_products += pre_GET_products
app.on_pre_GET_points_of_interest += pre_GET_points_of_interest

app.on_post_GET_payment_stats += post_GET_payment_stats

