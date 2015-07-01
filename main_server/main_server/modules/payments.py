import random
import requests

from bson import ObjectId

from main_server import app
from main_server.mail_client import send_mail
from main_server.money import money_scale

from jinja2 import Environment, PackageLoader

from requests.exceptions import ConnectionError
from requests.exceptions import Timeout

from flask import abort

from datetime import datetime


env = Environment(loader=PackageLoader('main_server', 'templates/email'))

headers = {'accept': 'application/json',
           'content-type': 'application/x-www-form-urlencoded'}
headers2 = {'accept': 'application/json',
            'content-type': 'application/json'}
data = {'grant_type': 'client_credentials',
        'client_id': app.config['MERCADOPAGO_CLIENT_ID'],
        'client_secret': app.config['MERCADOPAGO_CLIENT_SECRET']}


def get_auth_data():
    r = requests.post('https://api.mercadopago.com/oauth/token',
                  headers = headers,
                  data = data)
    auth_data = r.json()
    return auth_data


class Payments():
    def on_insert_payments(items):
        token = ''
        pay_link = ''

        for item in items:
            stores_db = app.data.driver.db['stores']
            store = stores_db.find_one({'_id': ObjectId(item['store_id'])})

            # Ensure correct Country => Payment Method relation
            if item['country'] != 'ar':
                if item['payment_method'] == 'bitcoin':
                    pass
                elif item['payment_method'] == 'mercadopago':
                    pass
                else:
                    abort(403)
            elif item['country'] == '':
                if item['payment_method'] != 'bitcoin':
                    abort(403)
            else: # AR
                if item['payment_method'] not in ['mercadopago', 'local_bank', 'bitcoin']:
                    abort(403)

            payments_db = app.data.driver.db['payments']
            while True:
                _id = ObjectId()
                payments = payments_db.find({'_id': _id}).count()
                if payments == 0:
                    break
            item['_id'] = _id

            if item['product'] == 'highlight_one_year':
                ars_amount = money_scale(2000, 'ars')
                ars_day_cost = money_scale(1, 'ars')
                ars_saving = money_scale(400, 'ars')
                usd_amount = money_scale(200, 'usd')
                usd_day_cost = money_scale(1, 'usd')
                usd_saving = money_scale(40, 'usd')
                btc_amount = money_scale(0.8, 'btc')
                btc_day_cost = money_scale(0.01, 'btc')
                btc_saving = money_scale(0.16, 'btc')
                title = 'Destacar comercio por 1 año'
                #description = 'Ahorro total $400'
            elif item['product'] == 'highlight_one_month':
                ars_amount = money_scale(200, 'ars')
                ars_day_cost = money_scale(1, 'ars')
                ars_saving = money_scale(0, 'ars')
                usd_amount = money_scale(20, 'usd')
                usd_day_cost = money_scale(1, 'usd')
                usd_saving = money_scale(0, 'usd')
                btc_amount = money_scale(0.08, 'btc')
                btc_day_cost = money_scale(0.01, 'btc')
                btc_saving = money_scale(0, 'btc')
                title = 'Destacar comercio por 1 mes'
                #description = 'Ahorro total $0'

            if item['payment_method'] == 'bitcoin':
                amount = btc_amount
                day_cost = btc_day_cost
                saving = btc_saving
                currency = 'btc'
            elif item['payment_method'] == 'mercadopago':
                if item['country'] == 'ar':
                    amount = ars_amount
                    day_cost = ars_day_cost
                    saving = ars_saving
                    currency = 'ars'
                else:
                    amount = usd_amount
                    day_cost = usd_day_cost
                    saving = usd_saving
                    currency = 'usd'
            elif item['payment_method'] == 'local_bank':
                amount = ars_amount
                day_cost = ars_day_cost
                saving = ars_saving
                currency = 'ars'

            title = "{0}: {1} {2}".format(title, currency, money_scale(amount, currency, True))
            description = "Estas ahorrando: {0} {1}".format(currency, money_scale(saving, currency, True))

            item['currency'] = currency
            item['amount'] = amount
            item['real_amount'] = 0
            item['day_cost'] = day_cost
            item['pay_link'] = ''
            item['sandbox_pay_link'] = ''
            item['store_iid'] = store['iid']
            item['description'] = "{0}\n{1}".format(title, description)

            # Mercadopago
            if item['payment_method'] == 'mercadopago':
                auth_data = get_auth_data()
                print (auth_data)
                token = auth_data['access_token']
                user_id = auth_data['user_id']
                r = requests.get('https://api.mercadopago.com/users/{0}/mercadopago_account/balance?access_token={1}'.format(user_id, token))
                price = float(money_scale(item['amount'], currency, True))
                if currency == 'ars':
                    mp_currency = 'ARS'
                elif currency == 'usd':
                    mp_currency = 'USD'
                else:
                    print("Bad mp currency")
                    abort(403)
                mp_item = {'title': title,
                           'description': description,
                           'category_id': 'services',
                           'quantity': 1,
                           'currency_id': mp_currency,
                           'unit_price': price}

                preference = {'items': [mp_item],
                              'external_reference': store['iid'],
                              'back_urls': {'success': 'http://xn--wid-boa.com', 'pending': 'http://xn--wid-boa.com', 'failure': 'http://xn--wid-boa.com'},
                              'notification_url': 'http://xn--wid-boa.com/mercadopago_payment_notification'}

                print (preference)
                r = requests.post('https://api.mercadopago.com/checkout/preferences/?access_token={0}'.format(token),
                                  headers = headers2,
                                  json = preference)
                print (r)
                print (r.text)
                preference_data = r.json()
                item['method_id'] = preference_data['id']
                item['pay_link'] = preference_data['init_point']
                item['sandbox_pay_link'] = preference_data['sandbox_init_point']

                r = requests.get('https://api.mercadopago.com/checkout/preferences/?access_token={0}'.format(token))
                print (r)
                print (r.text)
            # Bitcoin
            elif item['payment_method'] == 'bitcoin':
                apiurl =  "https://blockchain.info/es/api/receive"
                address = app.config['BITCOIN_PAYMENT_ADDRESS']
                secret= random.randint(0, 999999)
                callback = "http://xn--wid-boa.com/bitcoin_callback/{0}/{1}".format(item['_id'], secret)
                params = {
                    "method": "create",
                    "address": address,
                    "callback": callback,
                }
                try:
                    r = requests.get(apiurl, params=params)
                except ConnectionError:
                    abort(500) #return 'BlockChain Connection Error', 500
                except Timeout:
                    abort(500) #return 'BlockChain Timeout', 500

                try:
                    rjson = r.json()
                except:
                    abort(500) #return "Error on Json", 500
                if not 'input_address' in rjson:
                    abort(500) #return "No input_address", 500
                print (r.text)

                input_address = rjson['input_address']
                item['bitcoin'] = {'secret': secret,
                                    'status': 'waiting',
                                    'confirmations': 0,
                                    'input_address': input_address,
                                    'destination_address': address,
                                    'transaction_hash': '',
                                    'input_transaction_hash': '',
                                    'value': 0}

            smtp_server = app.config['PAYMENT_SMTP_SERVER']
            from_ = app.config['PAYMENT_MAIL_FROM']
            username = app.config['PAYMENT_MAIL_USERNAME']
            password = app.config['PAYMENT_MAIL_PASSWORD']
            to = item['email']
            mail_data = {
                'name': store['name'],
                'iid': store['iid'],
                'title': title,
                'description': description,
                'to': to,
                'method': item['payment_method'],
                'method_name': item['payment_method'],
                'amount': money_scale(amount, currency, True),
                'pay_link': item['pay_link'],
            }

            if item['payment_method'] == 'bitcoin':
                mail_data['bitcoin_address'] = item['bitcoin']['input_address']

            template = env.get_template('payment.txt')
            text=template.render(data = mail_data)
            template = env.get_template('payment.html')
            html=template.render(data = mail_data)
            subject="Instrucciones de pago ({0})".format(mail_data['iid'])
            send_mail(from_, to, subject, text, html, smtp_server, username, password)

    def pre_GET_payments(request, lookup):
        # Take payment callbacks
        # BITCOIN CALLBACK
        if 'callback' in request.args and request.args['callback']=='bitcoin':
            _id = request.view_args['_id']
            input_address = request.args['input_address']
            destination_address = request.args['destination_address']
            transaction_hash = request.args['transaction_hash']
            input_transaction_hash = request.args['input_transaction_hash']
            confirmations = int(request.args['confirmations'])
            value = int(request.args['value'])
            secret = int(request.args['secret'])
            status = 'processing'
            completed = False
            # IF CONFIRMED
            if confirmations > 5:
                status = 'confirmed'
                completed = True
            data = {'bitcoin.status': status,
                    'bitcoin.confirmations': confirmations,
                    'bitcoin.transaction_hash': transaction_hash,
                    'bitcoin.input_transaction_hash': input_transaction_hash,
                    'bitcoin.value': value,
                    'real_amount': value,
                    'completed': completed
            }
            # GET PAYMENT AND STORE FROM DB
            payments_db = app.data.driver.db['payments']
            payment = payments_db.find_one({'_id': ObjectId(_id)})
            # SECURITY CHECKS
            if not payment:
                print ('404: payment not found')
                abort(404)
            if payment['payment_method'] != 'bitcoin':
                print ('400: bad callback')
                abort(400)
            if payment['bitcoin']['destination_address'] != destination_address:
                print ('400: destination_address')
                abort(400)
            if payment['bitcoin']['secret'] != secret:
                print ('400: secret')
                abort(400)
            # FIRST TIME CONFIRMATION
            if not payment['completed'] and completed or True:
                data['start_date'] = datetime.now()
                # SEND MAIL
                stores_db = app.data.driver.db['stores']
                store = stores_db.find_one({'_id': payment['store_id']})
                to = payment['email']
                smtp_server = app.config['PAYMENT_SMTP_SERVER']
                from_ = app.config['PAYMENT_MAIL_FROM']
                username = app.config['PAYMENT_MAIL_USERNAME']
                password = app.config['PAYMENT_MAIL_PASSWORD']
                title = "Total pagado: {0} {1}".format(payment['currency'], money_scale(value, 'btc', True))
                mail_data = {
                    'name': store['name'],
                    'iid': store['iid'],
                    'title': title,
                    'description': '',
                    'to': to,
                    'method': payment['payment_method'],
                    'method_name': payment['payment_method'],
                    'amount': money_scale(value, 'btc', True),
                    'confirmations': confirmations,
                    'input_transaction_hash': input_transaction_hash,
                    'bitcoin_address': input_address
                }
                #print (mail_data)
                template = env.get_template('payment_confirmation.txt')
                text=template.render(data = mail_data)
                template = env.get_template('payment_confirmation.html')
                html=template.render(data = mail_data)
                subject="Confirmación de pago ({0})".format(payment['store_iid'])
                send_mail(from_, to, subject, text, html, smtp_server, username, password)
            #SAVE DATA TO DB
            payments_db.update({'_id': payment['_id'], '_etag': payment['_etag']}, {"$set": data})
            if confirmations > 5:
                return '', 200
            else:
                print ('400: confirmations')
                abort(400)
        # MERCADOPAGO CALLBACK
        elif 'callback' in request.args and request.args['callback']=='mercadopago':
            print ('MERCADOPAGO')
            topic = request.args['topic']
            notification_id = request.args['notification_id']
            auth_data = get_auth_data()
            token = auth_data['access_token']
            r = requests.get('https://api.mercadopago.com/collections/notifications/{0}?access_token={1}'.format(notification_id, token))
            print (r)
            print (r.text)
            return '', 200
