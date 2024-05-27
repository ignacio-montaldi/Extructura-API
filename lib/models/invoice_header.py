class InvoiceHeader:
    def __init__(
        self,
        business_name,
        business_address,
        vat_condition,
        document_type,
        checkout_aisle_number,
        document_number,
        issue_date,
        seller_cuit,
        gross_income,
        business_opening_date,
        client_cuit,
        client_name,
        client_vat_condition,
        client_address,
        sale_method,
    ):
        self.business_name = business_name
        self.business_address = business_address
        self.vat_condition = vat_condition
        self.document_type = document_type
        self.checkout_aisle_number = checkout_aisle_number
        self.document_number = document_number
        self.issue_date = issue_date
        self.seller_cuit = seller_cuit
        self.gross_income = gross_income
        self.business_opening_date = business_opening_date
        self.client_cuit = client_cuit
        self.client_name = client_name
        self.client_vat_condition = client_vat_condition
        self.client_address = client_address
        self.sale_method = sale_method
