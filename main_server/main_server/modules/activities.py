class Activities():
    def pre_GET_activities(request, lookup):
        if 'find_activities' in request.args:
            lookup["name"] = {"$regex": request.args['find_activities'], "$options": "i"}
