class CItem:
    def __init__(
        self,
        cod,
        title,
        amount,
        measure,
        unit_price,
        discount_perc,
        discounted_subtotal,
        subtotal,
    ):
        self.cod = cod
        self.title = title
        self.amount = amount
        self.measure = measure
        self.unit_price = unit_price
        self.discount_perc = discount_perc
        self.discounted_subtotal = discounted_subtotal
        self.subtotal = subtotal
