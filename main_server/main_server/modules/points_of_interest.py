class Points_of_interest():
    def pre_GET_points_of_interest(request, lookup):
        points_of_interest = app.data.driver.db['points_of_interest']
        # TODO pymongo.GEOSPHERE
        points_of_interest.create_index([("location", "2dsphere")])
        if 'find_places' in request.args:
            lookup["name"] = {"$regex": request.args['find_places']}
