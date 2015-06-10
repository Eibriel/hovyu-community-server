import os

RESOURCE_METHODS = ['GET', 'POST', 'DELETE']
ITEM_METHODS = ['GET', 'PUT', 'DELETE', 'PATCH']

# VERSIONING = True

try:
    MONGO_HOST= os.environ['COMUNIDAD_DB_1_PORT_27017_TCP_ADDR']
except:
    print ("Error")

stores_schema = { # Required
    'name': {
        'type': 'string',
        'required': True
    },
    'country': {
        'type': 'objectid',
        'required': True
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
    'location': {
        'type': 'point',
        'nullable': True,
        'default': None
    },
    'highlight': {
        'type': 'boolean',
        'required': True,
        'default': False
    }, # Optional
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

DOMAIN = {
    'stores': stores,
    'products': products,
    'points_of_interest': points_of_interest
}
