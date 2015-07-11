import os

RESOURCE_METHODS = ['GET', 'POST', 'DELETE']
ITEM_METHODS = ['GET', 'PUT', 'DELETE', 'PATCH']
XML = False
# VERSIONING = True

try:
    MONGO_HOST= os.environ['MONGODOCKERCOMPOSE_DB_1_PORT_27017_TCP_ADDR']
except:
    #print ("Error")
    pass

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
    },
    'edit_reason': {
        'type': 'string',
        'required': True
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
    #'products': {
    #    'type': 'list',
    #    'schema': {
    #        'type': 'objectid',
    #        'data_relation': {
    #            'resource': 'products',
    #            'field': '_id'
    #        }
    #    }
    #}
}

products_stores_schema = {
    'store': {
        'type': 'objectid',
        'required': True,
        'data_relation': {
            'resource': 'stores',
            'field': '_id'
        }
    },
    'product': {
        'type': 'objectid',
        'required': True,
        'data_relation': {
            'resource': 'products',
            'field': '_id'
        }
    },
    'properties': {
        'type': 'list',
        'required': True,
        'schema': {
            'type': 'objectid',
            'data_relation': {
                'resource': 'products_properties',
                'field': '_id'
            }
        }
    },
    'brand': {
        'type': 'string',
        'required': True
    },
    'price': {
        'type': 'string',
        'required': True
    }
}

products_properties_schema = {
    'name': {
        'type': 'string',
        'required': True
    }
}

# Human stuff
products_schema = {
    'name': {
        'type': 'string',
        'required': True
    }
}

attributes_schema = {
    'name': {
        'type': 'string',
        'required': True
    }
}

activities_schema = {
    'name': {
        'type': 'string',
        'required': True
    },
    'products': {
        'type': 'list',
        'required': True,
        'schema': {
            'type': 'objectid',
            'data_relation': {
                'resource': 'products',
                'field': '_id'
            }
        }
    }
}

# End human stuff

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
    'iid': {
        'type': 'integer',
        #'required': True
    },
    'country': {
        'type': 'string',
        'required': True,
        'allowed': ['ar', 'br', 'co', 've', 'mx', '']
    },
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
        'allowed': ['ar', 'usd', 'btc']
    },
    'amount': {
        'type': 'integer',
    },
    'real_amount': {
        'type': 'integer'
    },
    'day_cost': {
        'type': 'integer',
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
    },
    'bitcoin': {
        'type': 'dict',
        'schema': {
            'secret': {
                'type': 'string',
                'required': True
            },
            'status': {
                'type': 'integer',
                'required': True
            },
            'confirmations': {
                'type': 'integer',
                'required': True
            },
            'input_address': {
                'type': 'string',
                'required': True
            },
            'destination_address': {
                'type': 'string',
                'required': True
            },
            'transaction_hash': {
                'type': 'string',
                'required': True
            },
            'input_transaction_hash': {
                'type': 'string',
                'required': True
            },
            'value': {
                'type': 'integer',
                'required': True
            }
        }
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

tipstricks_schema = {
    'text': {
        'type': 'string',
        'required': True
    },
    'image': {
        'type': 'string',
        'allowed': ['stickers_amorzorzores/zzra_riendo_b.png',
                    'stickers_amorzorzores/zzr_saltando_b.png']
    }
}

human_checks_schema = {
    'image': {
        'type': 'string'
    },
    'options': {
        'type': 'list',
        'schema': {
            'type': 'string'
        }
    },
    'right_option': {
        'type': 'string'
    },
    'type': {
        'type': 'string'
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

products_properties = {
    'schema': products_properties_schema
}

products_stores = {
    'schema': products_stores_schema
}

attributes = {
    'schema': attributes_schema
}

activities = {
    'schema': activities_schema
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

tipstricks = {
    'schema': tipstricks_schema
}

human_checks = {
    'schema': human_checks_schema
}

DOMAIN = {
    'stores': stores,
    'products': products,
    'products_properties': products_properties,
    'products_stores': products_stores,
    'attributes': attributes,
    'activities': activities,
    'payments': payments,
    'payment_stats': payment_stats,
    'places': places,
    #
    'points_of_interest': points_of_interest,
    'tipstricks': tipstricks,
    'human_checks': human_checks
}
