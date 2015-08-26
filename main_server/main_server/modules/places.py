from main_server import app

class Places():
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
                'location': {"type":"Point","coordinates":[longitude, latitude]},
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
        #from eve.methods.patch import patch_internal
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
