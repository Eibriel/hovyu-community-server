import json
import random
from eve import Eve

app = Eve()
app.config.from_object('main_server.config.Config')

#from main_server.modules.places import Places
#app.on_pre_GET_places += Places.pre_GET_places

from main_server.modules.stores import Stores
app.on_pre_GET_stores += Stores.pre_GET_stores
app.on_post_GET_stores += Stores.post_GET_stores
app.on_insert_stores += Stores.on_insert_stores

from main_server.modules.products import Products
app.on_pre_GET_products += Products.pre_GET_products

from main_server.modules.points_of_interest import Points_of_interest
app.on_pre_GET_points_of_interest += Points_of_interest.pre_GET_points_of_interest

from main_server.modules.payment_stats import Payment_stats
app.on_post_GET_payment_stats += Payment_stats.post_GET_payment_stats

from main_server.modules.payments import Payments
app.on_insert_payments += Payments.on_insert_payments
app.on_pre_GET_payments += Payments.pre_GET_payments

from main_server.modules.activities import Activities
app.on_pre_GET_activities += Activities.pre_GET_activities

from main_server.modules.products_properties import ProductsProperties
app.on_pre_GET_products_properties += ProductsProperties.pre_GET_products_properties
