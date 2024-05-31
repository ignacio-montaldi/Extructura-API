import json
from fuzzywuzzy import fuzz

from lib.enums.image_type_enum import Image_type
from lib.models.invoice_model import Invoice


def testResult(
    analizedInvoice: Invoice,
    jsonPath: str,
    invoiceFileName: str,
    image_type: Image_type,
):
    result: float = 0
    itemsCompared: int = 0

    # Convierto el json perfecto guardado
    with open(jsonPath, "r") as file:
        file_content = file.read()

    perfect_invoice = dict(json.loads(file_content))

    # Tipo de factura
    analizedValue = str(analizedInvoice.type)
    perfectValue = str(perfect_invoice["type"])
    result = result + fuzz.ratio(analizedValue, perfectValue)
    itemsCompared = itemsCompared + 1

    # Elementos del encabezado
    for key, value in dict(analizedInvoice.header.__dict__).items():
        analizedValue = dict(analizedInvoice.header.__dict__).get(key)
        perfectValue = dict(perfect_invoice["header"]).get(key)
        result = result + fuzz.ratio(str(analizedValue), str(perfectValue))
        itemsCompared = itemsCompared + 1

    # Elementos de los productos
    for i in range(len(analizedInvoice.items)):
        for key, value in dict(analizedInvoice.items[i].__dict__).items():
            analizedValue = dict(analizedInvoice.items[i].__dict__).get(key)
            perfectValue = dict(perfect_invoice["items"][i]).get(key)
            result = result + fuzz.ratio(str(analizedValue), str(perfectValue))
            itemsCompared = itemsCompared + 1

    # Elementos del pie
    for key, value in dict(analizedInvoice.footer.__dict__).items():
        analizedValue = dict(analizedInvoice.footer.__dict__).get(key)
        perfectValue = dict(perfect_invoice["footer"]).get(key)
        result = result + fuzz.ratio(str(analizedValue), str(perfectValue))
        itemsCompared = itemsCompared + 1

    # Guardo resultado
    f = open("finalTest.txt", "a")
    f.write(
        "('"
        + str(invoiceFileName)
        + "','"
        + str(image_type.name)
        + "',"
        + str(round(result / itemsCompared, 2))
        + "),\n"
    )
    f.close()
