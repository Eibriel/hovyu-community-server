from main_server.config.default import Config

class Local(Config):
    DEBUG = False
    ADMIN_PASSWORD = ''

    PAYMENT_SMTP_SERVER = ''
    PAYMENT_MAIL_FROM = ''
    PAYMENT_MAIL_USERNAME = ''
    PAYMENT_MAIL_PASSWORD = ''

    MERCADOPAGO_CLIENT_ID = ''
    MERCADOPAGO_CLIENT_SECRET = ''

    BITCOIN_PAYMENT_ADDRESS = '
