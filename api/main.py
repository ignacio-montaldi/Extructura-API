# Fast API
from fastapi import FastAPI

# Scanning
from PIL import Image

# Image Decoding
from base64 import decodebytes

# Enums
from lib.enums.image_type_enum import Image_type

# Models
from lib.models.invoice_model import Invoice

# Functions
from lib.functions.delete_files_in_folder import deleteFilesInFolder
from api.functions.get_footer import getFooter
from api.functions.get_header import getHeader
from api.functions.get_invoice_type import getInvoiceType
from api.functions.get_items import getItems
from api.functions.preprocess_invoice import preprocessInvoice

################## API ########################
app = FastAPI()


@app.get("/")
def read_root():
    return {"welcome_message: Bienvenidos a Extructura"}


global invoice_type
global header
global footer
global items


@app.post("/recieve_image")
def send_image(image: Image):
    with open("data/factura.png", "wb") as f:
        f.write(decodebytes(str.encode(image.base64Image)))
    preprocessInvoice(Image_type(image.imageTypeId))
    global invoice_type
    invoice_type = getInvoiceType()
    return


@app.post("/header")
def get_header():
    global header
    header = getHeader()
    return


@app.post("/items")
def get_items():
    global items
    items = getItems(invoice_type)
    return


@app.post("/footer")
def get_footer():
    global footer
    footer = getFooter(invoice_type)
    return


@app.get("/invoice")
def get_invoice():
    invoice = Invoice(type=invoice_type.name, header=header, items=items, footer=footer)
    deleteFilesInFolder("./pretemp")
    deleteFilesInFolder("./temp")
    deleteFilesInFolder("./processing")
    deleteFilesInFolder("./data")
    return invoice
