import requests

from bson import ObjectId

from main_server import app
from main_server.mail_client import send_mail

        
class Payments():
    def on_insert_payments(items):
        token = ""
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
                print (r)
                print (r.text)
        
            r = requests.get('https://api.mercadopago.com/checkout/preferences/?access_token={0}'.format(token))
            
            print (r)
            print (r.text)

            smtp_server = app.config['PAYMENT_SMTP_SERVER']
            from_ = app.config['PAYMENT_MAIL_FROM']
            username = app.config['PAYMENT_MAIL_USERNAME']
            password = app.config['PAYMENT_MAIL_PASSWORD']
            
            name = store['name']
            iid = store['iid']
            amount_text = ''
            saving_text = ''
            to = item['email']

            text="""\
    ¡Hola!
    Para destacar el comercio "{0}"(1) siga estas instrucciones.

    {2} (descuento: {3})

    Métodos de pago disponibles:

    Transferencia Bancaria
    ----------------------
    Realice la transferencia a la siguiente cuenta,
    luego responda este correo con el comprobante de transferencia correspondiente.
    (Es importante que no modifique el asunto del correo)
                
    Cuenta Corriente en pesos
    Banco: BBVA Frances
    Número: 270-7129/2
    CBU: 0170270720000000712925
    Titular: Gabriel Caraballo
    CUIT: 20311134451


    MercadoPago
    -----------
    (Próximamente)


    PagoMisCuentas
    --------------
    (Próximamente)


    Bitcoin
    -------
    (Próximamente)


    Atte.
    Gabriel Caraballo
    WIDU Transmedia

            """.format(name, iid, amount_text, saving_text)
            
            html="""\
            <html>
                <head></head>
                <body>
                    <p>¡Hola!</p>
                    <p>Para destacar el comercio "{0}"({1}) siga estas instrucciones.</p>
                    <p>{2} (descuento: {3})</p>
                    <p>Métodos de pago disponibles</p>
                    <p>Transferencia Bancaria</p>
                    <p>
                    Realice la transferencia a la siguiente cuenta,<br>
                    luego responda este correo con el comprobante de transferencia correspondiente.<br>
                    (Es importante que no modifique el asunto del correo)
                    </p>
                    Cuenta Corriente en pesos<br>
                    Banco: BBVA Frances<br>
                    Número: 270-7129/2<br>
                    CBU: 0170270720000000712925<br>
                    Titular: Gabriel Caraballo<br>
                    CUIT: 20311134451<br>
                    </p>
                    
                    <p>MercadoPago</p>
                    <p>(Próximamente)</p>
                    
                    <p>PagoMisCuentas</p>
                    <p>(Próximamente)</p>

                    <p>Bitcoin</p>
                    <p>(Próximamente)</p>
                    
                    <p>Atte.<br>
                    Gabriel Caraballo<br>
                    WIDU Transmedia</p>
                </body>
            </html>
            """.format(name, iid, amount_text, saving_text)

            subject="Instrucciones de pago ({0})".format(iid)
            
            send_mail(from_, to, subject, text, html, smtp_server, username, password)
