import os

RESOURCE_METHODS = ['GET', 'POST', 'DELETE']
ITEM_METHODS = ['GET', 'PUT', 'DELETE', 'PATCH']
XML = False
# VERSIONING = True

try:
    MONGO_HOST= os.environ['MONGODOCKERCOMPOSE_DB_1_PORT_27017_TCP_ADDR']
except:
    print ("Error")

stores_schema = { # Required
    'name': {
        'type': 'string',
        'required': True
    },
    'iid': {
        'type': 'integer',
        'required': True,
    },
    'wid': {
        'type': 'string',
        'required': True,
    },
    'views': {
        'type': 'integer',
        'required': True,
        'default': 0
    },
    'score': {
        'type': 'dict',
        'required': True,
        'default': {'count': 0, 'sum': 0},
        'schema': {
            'count': {
                'type': 'integer',
                'required': True,
                'default': 0
            },
            'sum': {
                'type': 'integer',
                'required': True,
                'default': 0
            }
        }
    },
    'exact_location': {
        'type': 'boolean',
        'required': True,
        'default': False
    },
    'location': {
        'type': 'point',
        'required': True
    },
    'place': {
        'type': 'dict',
        'required': True,
        'nullable': True,
        'schema': {
            'place_id': {
                'type': 'objectid',
                'required': True
            },
            'osm_id': {
                'type': 'integer',
                'required': True
            },
            'full_name': {
                'type': 'string',
                'required': True
            },
            'location': {
                'type': 'point',
                'required': True
            }
        }
    }, # Optional
    'highlight': {
        'type': 'boolean',
        'default': False
    },
    'description': {
        'type': 'string'
    },
    'address': {
        'type': 'string'
    },
    'business_hours': {
        'type': 'list',
        'schema': {
            'type': 'list',
            'schema': {
                'type': 'dict',
                'schema': {
                    'open': {
                        'type': 'integer'
                    },
                    'close': {
                        'type': 'integer'
                    }
                }
            }
        }
    },
    'email': {
        'type': 'string'
    },
    'website': {
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': {
                'text': {
                    'type': 'string',
                    'required': True
                },
                'url': {
                    'type': 'string',
                    'required': True
                }
            }
        }
    },
    'tel': {
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': {
                'type': {
                    'type': 'string',
                    'allowed': ['line', 'mobile', 'radio'],
                    'required': True
                },
                'number': {
                    'type': 'string',
                    'required': True
                }
            }
        }
    },
    'badges': {
        'type': 'list',
        'schema': {
            'type': 'objectid'
        }
    },
    'products': {
        'type': 'list',
        'schema': {
            'type': 'objectid',
            'required': True,
            'data_relation': {
                'resource': 'products',
                'field': '_id'
            }
        }
    }
}

products_schema = {
    'name': {
        'type': 'string',
        'required': True
    },
    'description': {
        'type': 'string',
        'required': True
    },
    'wiktionary': {
        'type': 'string',
        'required': True
    }
}

points_of_interest_schema = {
    'name': {
        'type': 'string',
        'required': True
    },
    'location': {
        'type': 'point',
        'required': True
    }
}

payments_schema = {
    'payment_method': {
        'type': 'string',
        'required': True,
        'allowed': ['local_bank', 'pagomiscuentas', 'mercadopago', 'bitcoin', 'bonus']
    },
    'method_id': {
        'type': 'string'
    },
    'description': {
        'type': 'string',
        'required': True
    },
    'email': {
        'type': 'string',
        'required': True
    },
    'pay_link': {
        'type': 'string',
    },
    'sandbox_pay_link': {
        'type': 'string',
    },
    'product': {
        'type': 'string',
    },
    'start_date': {
        'type': 'datetime',
    },
    'end_date': {
        'type': 'datetime',
    },
    'store_id': {
        'type': 'objectid',
        'required': True
    },
    'store_iid': {
        'type': 'integer'
    },
    'currency': {
        'type': 'string',
        'required': True,
        'allowed': ['ar', 'usd', 'euro', 'bitcoin']
    },
    'amount': {
        'type': 'float',
    },
    'day_cost': {
        'type': 'float',
    },
    'completed': {
        'type': 'boolean',
        'required': True
    },
    'refunded': {
        'type': 'boolean',
        'required': True
    },
    'refund_description': {
        'type': 'string',
        'required': True
    }
}

places_schema = {
    'osm_id': {
        'type': 'integer',
        'required': True,
        'unique': True
    },
    'name': {
        'type': 'string',
        'required': True
    },
    'type': {
        'type': 'string',
        'required': True,
    },
    'location': {
        'type': 'point',
        'required': True
    },
    'is_in': {
        'type': 'dict',
        'required': True,
        'schema': {
            'country': {
                'type': 'string',
                'required': True,
                'nullable': True
            },
            'state': {
                'type': 'string',
                'required': True,
                'nullable': True
            },
            'city': {
                'type': 'string',
                'required': True,
                'nullable': True
            }
        }
    },
    'near_place': {
        'type': 'dict',
        'required': True,
        'schema': {
            'name': {
                'type': 'string',
                'required': True,
                'nullable': True
            },
            'country': {
                'type': 'string',
                'required': True,
                'nullable': True
            },
            'state': {
                'type': 'string',
                'required': True,
                'nullable': True
            },
            'city': {
                'type': 'string',
                'required': True,
                'nullable': True
            }
        }
    }
}

stores = {
    # 'soft_delete': True,
    'versioning': True,
    'schema': stores_schema
}

products = {
    'schema': products_schema
}

points_of_interest = {
    'schema': points_of_interest_schema
}

payments = {
    'schema': payments_schema
}

payment_stats = {
    #'schema': {},
    'resource_methods': ['GET'],
    'item_methods': []
}

places = {
    'schema': places_schema
}

DOMAIN = {
    'stores': stores,
    'products': products,
    'points_of_interest': points_of_interest,
    'payments': payments,
    'payment_stats': payment_stats,
    'places': places
}
