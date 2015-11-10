import math
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
from datetime import date
from datetime import timedelta
from dateutil import relativedelta


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
            secret= random.randint(0, 999999)

            ars_month = 200
            usd_month = 20
            btc_month = 0.08

            months = item['months']

            saving = math.floor(months/12)*2

            ars_pay = (ars_month*months) - (ars_month*saving)
            usd_pay = (usd_month*months) - (usd_month*saving)
            btc_pay = (btc_month*months) - (btc_month*saving)

            #ars_saving = ars_month*saving;
            #usd_saving = usd_month*saving;
            #btc_saving = btc_month*saving;

            ars_amount = money_scale(ars_pay, 'ars')
            ars_saving = money_scale(ars_month*saving, 'ars')
            usd_amount = money_scale(usd_pay, 'usd')
            usd_saving = money_scale(usd_month*saving, 'usd')
            btc_amount = money_scale(btc_pay, 'btc')
            btc_saving = money_scale(btc_month*saving, 'btc')
            title = 'Badge {0} {1} moth/s'.format(item['badge'], item['months'])
            #description = 'Ahorro total $400'

            if item['payment_method'] == 'bitcoin':
                amount = btc_amount
                saving = btc_saving
                currency = 'btc'
            elif item['payment_method'] == 'mercadopago':
                if item['country'] == 'ar':
                    amount = ars_amount
                    saving = ars_saving
                    currency = 'ars'
                else:
                    amount = usd_amount
                    saving = usd_saving
                    currency = 'usd'
            elif item['payment_method'] == 'local_bank':
                amount = ars_amount
                saving = ars_saving
                currency = 'ars'

            title = "{0}: {1} {2}".format(title, currency, money_scale(amount, currency, True))
            description = "Saving: {0} {1}".format(currency, money_scale(saving, currency, True))

            item['currency'] = currency
            item['amount'] = amount
            item['real_amount'] = 0
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
                              'back_urls': {'success': 'http://hovyu.com', 'pending': 'http://hovyu.com', 'failure': 'http://hovyu.com'},
                              'notification_url': 'http://hovyu.com/mercadopago_callback/{0}/{1}'.format(item['_id'], secret)}

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
                callback = "http://hovyu.com/bitcoin_callback/{0}/{1}".format(item['_id'], secret)
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

        first_confirmation = False
        callback = None

        _id = request.view_args['_id']
        # GET PAYMENT AND STORE FROM DB
        payments_db = app.data.driver.db['payments']
        payment = payments_db.find_one({'_id': ObjectId(_id)})

        # BITCOIN CALLBACK
        if 'callback' in request.args and request.args['callback']=='bitcoin':
            callback = 'bitcoin'
            print ('BITCOIN')
            input_address = request.args['input_address']
            destination_address = request.args['destination_address']
            transaction_hash = request.args['transaction_hash']
            input_transaction_hash = request.args['input_transaction_hash']
            confirmations = int(request.args['confirmations'])
            value = int(request.args['value'])
            secret = int(request.args['secret'])
            status = 'processing'
            completed = False
            first_confirmation = False
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
            if not payment['completed'] and completed:
                data['start_date'] = datetime.now()
                first_confirmation = True
            #SAVE DATA TO DB
            payments_db.update({'_id': payment['_id'], '_etag': payment['_etag']}, {"$set": data})
            if completed:
                return '', 200
            else:
                print ('400: confirmations')
                abort(400)
        # MERCADOPAGO CALLBACK
        elif 'callback' in request.args and request.args['callback']=='mercadopago':
            callback = 'mercadopago'
            print ('MERCADOPAGO')
            #_id = request.view_args['_id']
            topic = request.args['topic']
            notification_id = request.args['notification_id']
            auth_data = get_auth_data()
            token = auth_data['access_token']

            #r = requests.get('https://api.mercadopago.com/collections/search?access_token={0}'.format(token))
            #print (r)
            #print (r.text)

            if topic == 'payment':
                r = requests.get('https://api.mercadopago.com/collections/notifications/{0}?access_token={1}'.format(notification_id, token))
                print (r)
                print (r.text)
                payment_info = r.json()
                order_id = payment_info["collection"]["merchant_order_id"]
            elif topic == 'merchant_order':
                order_id = notification_id

            url = 'https://api.mercadopago.com/merchant_orders/{0}?access_token={1}'.format(order_id, token)
            r = requests.get(url)
            #print (url)
            print (r)
            print (r.text)
            merchant_order_info = r.json()

            first_confirmation = False
            completed = False
            paid_amount = 0
            for mp_payment in merchant_order_info["payments"]:
                if mp_payment['status'] == 'approved':
                    paid_amount += mp_payment['transaction_amount']
            if paid_amount >= merchant_order_info["total_amount"]:
                completed = True
            # SECURITY CHECKS
            if not payment:
                print ('404: payment not found')
                abort(404)
            if payment['payment_method'] != 'mercadopago':
                print ('400: bad callback')
                abort(400)
            #if payment['bitcoin']['secret'] != secret:
            #    print ('400: secret')
            #    abort(400)
            data = {'real_amount': money_scale(paid_amount, payment['currency']),
                    'completed': completed
            }
            # FIRST TIME CONFIRMATION
            if not payment['completed'] and completed:
                data['start_date'] = datetime.now()
                first_confirmation = True
            #SAVE DATA TO DB
            print (data)
            payments_db.update({'_id': payment['_id'], '_etag': payment['_etag']}, {"$set": data})
        # TEST CALLBACK
        elif 'callback' in request.args and request.args['callback']=='test':
            callback = 'test'
            print ('TEST')
            first_confirmation = True
            data = {'real_amount': 100000,
                    'completed': True
            }

        if first_confirmation:
            amount_text = money_scale(data['real_amount'], payment['currency'], True)
            stores_db = app.data.driver.db['stores']
            store = stores_db.find_one({'_id': payment['store_id']})
            # BITCOIN
            if callback == 'bitcoin':
                title = "Total pagado: {0} {1}".format(payment['currency'], money_scale(value, 'btc', True))
            else:
                title = "Total pagado: {0} {1}".format(payment['currency'], amount_text)

            # CREATE BADGE OR UPDATE BADGE
            _id = request.view_args['_id']
            payments_db = app.data.driver.db['payments']
            payment = payments_db.find_one({'_id': ObjectId(_id)})
            store_id = payment['store_id']

            store_badge_db = app.data.driver.db['badge_store']
            store_badge = store_badge_db.find_one({'store': ObjectId(store_id)})

            if store_badge:
                #print (store_badge['end_date'].date())
                #print (date.today())
                if store_badge['end_date'].date() < date.today():
                    start_date = datetime.today()
                else:
                    start_date = store_badge['end_date'].date()
                end_date = start_date + relativedelta.relativedelta(months=payment['months'])
                end_date = datetime.combine(end_date, datetime.min.time())
                badge = {
                    'end_date': end_date,
                }
                store_badge_db.update({'_id': store_badge['_id']}, {'$set': badge})
            else:
                end_date = date.today() + relativedelta.relativedelta(months=payment['months'])
                badge = {
                    'store': payment['store_id'],
                    'badge': payment['badge'],
                    'start_date': date.today(),
                    'end_date': end_date,
                    'paused': False
                }
                store_badge_db.insert(badge)

            # SEND MAIL
            to = payment['email']
            smtp_server = app.config['PAYMENT_SMTP_SERVER']
            from_ = app.config['PAYMENT_MAIL_FROM']
            username = app.config['PAYMENT_MAIL_USERNAME']
            password = app.config['PAYMENT_MAIL_PASSWORD']
            mail_data = {
                'name': store['name'],
                'iid': store['iid'],
                'title': title,
                'description': '',
                'to': to,
                'method': payment['payment_method'],
                'method_name': payment['payment_method'],
                'amount': amount_text,
                #'amount': money_scale(value, 'btc', True),
                #'confirmations': confirmations,
                #'input_transaction_hash': input_transaction_hash,
                #'bitcoin_address': input_address
            }
            if callback == 'bitcoin':
                #mail_data['amount'] = money_scale(value, 'btc', True)
                mail_data['confirmations'] = confirmations,
                mail_data['input_transaction_hash'] = input_transaction_hash,
                mail_data['bitcoin_address'] = input_address

            #print (mail_data)
            template = env.get_template('payment_confirmation.txt')
            text=template.render(data = mail_data)
            template = env.get_template('payment_confirmation.html')
            html=template.render(data = mail_data)
            subject="Confirmación de pago ({0})".format(payment['store_iid'])
            send_mail(from_, to, subject, text, html, smtp_server, username, password)
            #print (badge)
        return '', 200
