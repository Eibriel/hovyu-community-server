import os

RESOURCE_METHODS = ['GET', 'POST', 'DELETE']
ITEM_METHODS = ['GET', 'PUT', 'DELETE', 'PATCH']
XML = False
PAGINATION = False
EXTENDED_MEDIA_INFO = ['content_type']
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
        'default': 0,
        #'versioned': False
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
    'edit_reason': {
        'type': 'string',
        'required': True
    }, # Optional
    'logo_picture': {
        'type': 'objectid',
        'nullable': True
    },
    'main_picture': {
        'type': 'objectid',
        'nullable': True
    },
    'client_pictures': {
        'type': 'list',
        'schema': {
            'type': 'objectid',
            'data_relation': {
                'resource': 'client_pictures',
                'field': '_id'
            }
        }
    },
    'highlight': {
        'type': 'boolean',
        'default': False
    },
    'description': {
        'type': 'string'
    },
    'process_description': {
        'type': 'string'
    },
    #'process_picture': {
    #    'type': 'media',
    #},
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
            'data_relation': {
                'resource': 'products',
                'field': '_id'
            }
        }
    },
    'products_properties': {
        'type': 'list',
        'schema': {
            'type': 'objectid',
            'data_relation': {
                'resource': 'products_properties',
                'field': '_id'
            }
        }
    },
    'products_documents': {
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': {
                'product': {
                    'type': 'string',
                },
                'properties': {
                    'type': 'list',
                    'schema': {
                        'type': 'string',
                    }
                },
                'brand': {
                    'type': 'string',
                },
                'price': {
                    'type': 'string',
                }
            }
        }
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
    },
    'use_count': {
        'type': 'integer',
        'default': 0
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
    #'product': {
    #    'type': 'string',
    #},
    'completion_date': {
       'type': 'datetime',
       'nullable': True
    },
    #'end_date': {
    #   'type': 'datetime',
    #},
    'badge': {
        'type': 'string',
        'required': True
    },
    'months': {
        'type': 'number',
        'required': True
    },
    'store_id': {
        'type': 'objectid',
        'required': True
    },
    'store_iid': {
        'type': 'integer'
    },
    'badge_store': {
        'type': 'objectid',
        'nullable': True,
        'data_relation': {
            'resource': 'badge_store',
            'field': '_id'
        }
    },
    'currency': {
        'type': 'string',
        'allowed': ['ar', 'usd', 'btc']
    },
    'amount': {
        'type': 'integer'
    },
    'real_amount': {
        'type': 'integer'
    },
    #'day_cost': {
    #     'type': 'integer',
    #},
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

badge_store_schema = {
    'store': {
        'type': 'objectid',
        'required': True,
        'data_relation': {
            'resource': 'stores',
            'field': '_id'
        }
    },
    'badge': {
        'type': 'string',
        'required': True,
        'allowed': ['recycling',
                    'clean_energy',
                    'organic',
                    'vegan',
                    'kosher',
                    'gluten_free',
                    'cruelty_free',
                    'free_software',
                    'free_hardware',
                    'creative_commons']
    },
    'start_date': {
        'type': 'datetime',
        'required': True
    },
    'end_date': {
        'type': 'datetime',
        'required': True
    },
    'paused': {
        'type': 'boolean',
        'default': False
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

client_pictures_schema = {
    'name': {
        'type': 'string',
        #'required': True,
        'default': ''
    },
    'store_id': {
        'type': 'string',
        'default': ''
    },
    'picture_binary': {
        'type': 'media',
        #'required': True
    },
    'approved': {
        'type': 'boolean',
        'default': False
    },
    'admin_comments': {
        'type': 'string',
        'default': ''
    },
    'score': {
        'type': 'integer',
        'default': 0
    },
    'album': {
        'type': 'string',
        'allowed': ['client',
                    'process']
    }
}

logo_pictures_schema = {
    'picture_binary': {
        'type': 'media',
    },
    'approved': {
        'type': 'boolean',
        'default': False
    },
    'admin_comments': {
        'type': 'string',
        'default': ''
    }
}


access_log_schema = {
    'page': {
        'type': 'string'
    },
    'ip_md5': {
        'type': 'string'
    },
    'useragent': {
        'type': 'string'
    },
    'useragent_platform': {
        'type': 'string',
        'nullable': True
    },
    'useragent_browser': {
        'type': 'string',
        'nullable': True
    },
    'useragent_version': {
        'type': 'string',
        'nullable': True
    },
    'useragent_language': {
        'type': 'string',
        'nullable': True
    },
    'acceptlanguage': {
        'type': 'string'
    },
    'robot': {
        'type': 'boolean'
    },
    'harmful': {
        'type': 'boolean'
    },
    'referrer': {
        'type': 'string',
        'nullable': True
    }
}


stores = {
    # 'soft_delete': True,
    'versioning': True,
    'schema': stores_schema,
    'public_methods': ['GET', 'POST'],
    'public_item_methods': ['GET', 'PATCH']
}

store_stats = {
    #'schema': {},
    'resource_methods': ['GET'],
    'item_methods': [],
    'public_methods': ['GET'],
    'public_item_methods': ['GET']
}

products = {
    'schema': products_schema,
    'public_methods': ['GET'],
    'public_item_methods': ['GET']
}

products_properties = {
    'schema': products_properties_schema,
    'public_methods': ['GET'],
    'public_item_methods': ['GET']
}

attributes = {
    'schema': attributes_schema
}

activities = {
    'schema': activities_schema,
    'public_methods': ['GET'],
    'public_item_methods': ['GET']
}

points_of_interest = {
    'schema': points_of_interest_schema,
    'public_methods': ['GET'],
    'public_item_methods': ['GET']
}

payments = {
    'schema': payments_schema,
    'public_methods': ['GET', 'POST'],
    'public_item_methods': ['GET']
}

payment_stats = {
    #'schema': {},
    'public_methods': ['GET'],
    'resource_methods': ['GET'],
    'item_methods': []
}

badge_store = {
    'schema': badge_store_schema,
    'public_methods': ['GET'],
    'public_item_methods': ['GET']
}

tipstricks = {
    'schema': tipstricks_schema,
    'public_methods': ['GET'],
    'public_item_methods': ['GET']
}

human_checks = {
    'schema': human_checks_schema,
    #'resource_methods': ['GET'],
    'public_methods': ['GET', 'POST'],
    'public_item_methods': ['GET']
}

client_pictures = {
    'schema': client_pictures_schema,
    #'resource_methods': ['GET'],
    'public_methods': ['GET', 'POST'],
    'public_item_methods': ['GET']
}

logo_pictures = {
    'schema': logo_pictures_schema,
    #'resource_methods': ['GET'],
    'public_methods': ['GET', 'POST'],
    'public_item_methods': ['GET']
}

access_log = {
    'schema': access_log_schema,
    'public_methods': ['GET', 'POST'],
    'public_item_methods': ['GET', 'PATCH']
}

DOMAIN = {
    'stores': stores,
    'store_stats': store_stats,
    'products': products,
    'products_properties': products_properties,
    'attributes': attributes,
    'activities': activities,
    'payments': payments,
    'payment_stats': payment_stats,
    'badge_store': badge_store,
    'client_pictures': client_pictures,
    'logo_pictures': logo_pictures,
    #
    'points_of_interest': points_of_interest,
    'tipstricks': tipstricks,
    'human_checks': human_checks,
    #
    'access_log': access_log
}
