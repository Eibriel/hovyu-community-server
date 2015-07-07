class Products():
    def pre_GET_products(request, lookup):
        if 'find_products' in request.args:
            lookup["name"] = {"$regex": request.args['find_products'], "$options": "i"}
