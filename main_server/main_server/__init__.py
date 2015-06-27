import json
import random
from eve import Eve
from bson import ObjectId

from main_server.mail_client import send_mail

Eve.debug = True

wid_chars = [ 0x1f31e, 0x1f33d, 0x1f34e, 0x1f433, 0x1f427,
              0x1f525, 0x2744,  0x2764,  0x1f332, 0x1f343,
              0x1f412, 0x1f407, 0x1f418, 0x1f416, 0x1f347,
              0x1f353, 0x1f6b2, 0x1f3b8, 0x1f3c0, 0x1f3b7,
              0x1f30d, 0x1f31d, 0x1f40d, 0x1f52d, 0x1f308]

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
    raw_payload = json.loads(payload.data.decode("utf-8"))
    #add_ids()
    items = None
    if '_items' in raw_payload:
        items = raw_payload.get('_items')
    elif raw_payload:
        items = [raw_payload]

    #if '_items' not in items:
    #    items = {'_items': [items]}
    
    if items:
        high_items = []
        common_items = []
    
        for item in items:
            #print (item)
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
            if 'score' in item and item['score']['count'] > 0:
                item['total_score'] = item['score']['sum'] / item['score']['count']
            else:
                item['total_score'] = 0
            # Fix exact_location
            if 'exact_location' not in item:
                item['exact_location'] = False
            # Fix place
            if 'place' not in item:
                item['place'] = None
        
        for item in items:
            if 'highlight' in item and item['highlight']:
                high_items.append(item)
            else:
                common_items.append(item)
        
        items = high_items+common_items
        
        raw_payload = {'_items': items}
        payload.set_data(json.dumps(raw_payload).encode('utf-8'))


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
        stores = stores_db.find({'wid': iid}).count()
        if stores == 0:
            break
    return wid, iid


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
    total = 0
    if len(payments_db['result'])>0:
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
            'location': {"type":"Point","coordinates":[latitude, longitude]},
            'is_in': {
                'country': country,
                'state': state,
                'city': city
            },
            'near_place': {
                'name': None,
                'country': None,
                'state': None,
                'city': None
            }
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


def on_insert_payments(items):
    import requests
    token = ""
    headers = {'accept': 'application/json',
               'content-type': 'application/x-www-form-urlencoded'}
    headers2 = {'accept': 'application/json',
                'content-type': 'application/json'}
    data = {'grant_type': 'client_credentials',
            'client_id': app.config['MERCADOPAGO_CLIENT_ID'],
            'client_secret': app.config['MERCADOPAGO_CLIENT_SECRET']}
    r = requests.post('https://api.mercadopago.com/oauth/token',
                      headers = headers,
                      data = data)
    auth_data = r.json()
    print (auth_data)
    token = auth_data['access_token']
    user_id = auth_data['user_id']
    r = requests.get('https://api.mercadopago.com/users/{0}/mercadopago_account/balance?access_token={1}'.format(user_id, token))
    
    for item in items:
        stores_db = app.data.driver.db['stores']
        store = stores_db.find_one({'_id': ObjectId(item['store_id'])})
            
        if item['payment_method'] == 'mercadopago':
            price = float(item['amount'])
            mp_item = {'title': 'Destacar comercio por 1 anio',
                    'category_id': 'services',
                    'quantity': 1,
                    'currency_id': 'ARS',
                    'unit_price': price}

            preference = {'items': [mp_item],
                          'external_reference': store['iid']}
            print (preference)
            r = requests.post('https://api.mercadopago.com/checkout/preferences/?access_token={0}'.format(token),
                              headers = headers2,
                              json = preference)
            preference_data = r.json()
            item['method_id'] = preference_data['id']
            item['store_iid'] = store['iid']
            print (r)
            print (r.text)
    
        r = requests.get('https://api.mercadopago.com/checkout/preferences/?access_token={0}'.format(token))
        
        print (r)
        print (r.text)

        smtp_server = app.config['PAYMENT_SMTP_SERVER']
        from_ = app.config['PAYMENT_MAIL_FROM']
        username = app.config['PAYMENT_MAIL_USERNAME']
        password = app.config['PAYMENT_MAIL_PASSWORD']
        
        name = store['name']
        iid = store['iid']
        amount_text = ''
        saving_text = ''
        to = item['email']

        text="""\
¡Hola!
Para destacar el comercio "{0}"(1) siga estas instrucciones.

{2} (descuento: {3})

Métodos de pago disponibles:

Transferencia Bancaria
----------------------
Realice la transferencia a la siguiente cuenta,
luego responda este correo con el comprobante de transferencia correspondiente.
(Es importante que no modifique el asunto del correo)
            
Cuenta Corriente en pesos
Banco: BBVA Frances
Número: 270-7129/2
CBU: 0170270720000000712925
Titular: Gabriel Caraballo
CUIT: 20311134451


MercadoPago
-----------
(Próximamente)


PagoMisCuentas
--------------
(Próximamente)


Bitcoin
-------
(Próximamente)


Atte.
Gabriel Caraballo
WIDU Transmedia

        """.format(name, iid, amount_text, saving_text)
        
        html="""\
        <html>
            <head></head>
            <body>
                <p>¡Hola!</p>
                <p>Para destacar el comercio "{0}"({1}) siga estas instrucciones.</p>
                <p>{2} (descuento: {3})</p>
                <p>Métodos de pago disponibles</p>
                <p>Transferencia Bancaria</p>
                <p>
                Realice la transferencia a la siguiente cuenta,<br>
                luego responda este correo con el comprobante de transferencia correspondiente.<br>
                (Es importante que no modifique el asunto del correo)
                </p>
                Cuenta Corriente en pesos<br>
                Banco: BBVA Frances<br>
                Número: 270-7129/2<br>
                CBU: 0170270720000000712925<br>
                Titular: Gabriel Caraballo<br>
                CUIT: 20311134451<br>
                </p>
                
                <p>MercadoPago</p>
                <p>(Próximamente)</p>
                
                <p>PagoMisCuentas</p>
                <p>(Próximamente)</p>

                <p>Bitcoin</p>
                <p>(Próximamente)</p>
                
                <p>Atte.<br>
                Gabriel Caraballo<br>
                WIDU Transmedia</p>
            </body>
        </html>
        """.format(name, iid, amount_text, saving_text)

        subject="Instrucciones de pago ({0})".format(iid)
        
        send_mail(from_, to, subject, text, html, smtp_server, username, password)
    

app = Eve()
app.config.from_object('main_server.config.Config')

app.on_pre_GET_places += pre_GET_places

app.on_pre_GET_stores += pre_GET_stores
app.on_post_GET_stores += post_GET_stores
app.on_insert_stores += on_insert_stores

app.on_pre_GET_products += pre_GET_products
app.on_pre_GET_points_of_interest += pre_GET_points_of_interest

app.on_post_GET_payment_stats += post_GET_payment_stats

app.on_insert_payments += on_insert_payments


