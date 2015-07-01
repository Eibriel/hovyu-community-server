def money_scale(value, currency, inverse=False):
    if not inverse:
        if currency == 'btc':
            return int(value * 100000000)
        else:
            return int(value * 1000)
    else:
        if currency == 'btc':
            return "{0}".format(value / 100000000)
        else:
            return "{0}".format(value / 1000)
