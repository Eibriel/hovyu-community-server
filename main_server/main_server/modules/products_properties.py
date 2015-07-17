class ProductsProperties():
    def pre_GET_products_properties(request, lookup):
        if 'find_products_properties' in request.args:
            lookup["name"] = {"$regex": request.args['find_products_properties'], "$options": "i"}
