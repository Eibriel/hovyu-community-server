import requests

from bson import ObjectId

from main_server import app
from main_server.mail_client import send_mail

from jinja2 import Environment, PackageLoader

        
class Payments():
    def on_insert_payments(items):
        token = ''
        pay_link = ''
        headers = {'accept': 'application/json',
                   'content-type': 'application/x-www-form-urlencoded'}
        headers2 = {'accept': 'application/json',
                    'content-type': 'application/json'}
        data = {'grant_type': 'client_credentials',
                'client_id': app.config['MERCADOPAGO_CLIENT_ID'],
                'client_secret': app.config['MERCADOPAGO_CLIENT_SECRET']}
        r = requests.post('https://api.mercadopago.com/oauth/token',
                          headers = headers,
                          data = data)
        auth_data = r.json()
        print (auth_data)
        token = auth_data['access_token']
        user_id = auth_data['user_id']
        r = requests.get('https://api.mercadopago.com/users/{0}/mercadopago_account/balance?access_token={1}'.format(user_id, token))
        
        for item in items:
            stores_db = app.data.driver.db['stores']
            store = stores_db.find_one({'_id': ObjectId(item['store_id'])})
            
            if item['product'] == 'highlight_one_year':
                item['amount'] = 2000.0
                item['day_cost'] = 1.0
            elif item['product'] == 'highlight_one_month':
                item['amount'] = 200.0
                item['day_cost'] = 1.0
            
            item['pay_link'] = ''
            item['sandbox_pay_link'] = ''
            
            if item['payment_method'] == 'mercadopago':
                price = float(item['amount'])
                mp_item = {'title': 'Destacar comercio por 1 anio',
                        'category_id': 'services',
                        'quantity': 1,
                        'currency_id': 'ARS',
                        'unit_price': price}

                preference = {'items': [mp_item],
                              'external_reference': store['iid']}
                print (preference)
                r = requests.post('https://api.mercadopago.com/checkout/preferences/?access_token={0}'.format(token),
                                  headers = headers2,
                                  json = preference)
                preference_data = r.json()
                item['method_id'] = preference_data['id']
                item['store_iid'] = store['iid']
                item['pay_link'] = preference_data['init_point']
                item['sandbox_pay_link'] = preference_data['sandbox_init_point']
                print (r)
                print (r.text)
        
            r = requests.get('https://api.mercadopago.com/checkout/preferences/?access_token={0}'.format(token))
            
            print (r)
            print (r.text)

            smtp_server = app.config['PAYMENT_SMTP_SERVER']
            from_ = app.config['PAYMENT_MAIL_FROM']
            username = app.config['PAYMENT_MAIL_USERNAME']
            password = app.config['PAYMENT_MAIL_PASSWORD']
            
            to = item['email']
            
            mail_data = {
                'name': store['name'],
                'iid': store['iid'],
                'amount_text': '',
                'saving_text': '',
                'to': to,
                'method': item['payment_method'],
                'method_name': item['payment_method'],
                'pay_link': item['pay_link']
            }

            env = Environment(loader=PackageLoader('main_server', 'templates/email'))

            template = env.get_template('payment.txt')
            text=template.render(data = mail_data)
            
            template = env.get_template('payment.html')
            html=template.render(data = mail_data)

            subject="Instrucciones de pago ({0})".format(mail_data['iid'])
            
            send_mail(from_, to, subject, text, html, smtp_server, username, password)
