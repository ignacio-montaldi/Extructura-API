class CFooter:
    def __init__(self, currency, sub_total, other_taxes_ammout, total, exchange_rate):
        self.currency = currency
        self.sub_total = sub_total
        self.other_taxes_ammout = other_taxes_ammout
        self.total = total
        self.exchange_rate = exchange_rate
