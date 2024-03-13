# Fast API
from fastapi import FastAPI
from pydantic import BaseModel

# Scanning

import os
import cv2
import pytesseract
from PIL import Image
import numpy as np


# Image Decoding
from base64 import decodebytes

# Other
import time
from lib.functions.preprocess_image import preprocess_image

start_time = time.time()

#Models
from lib.models.invoice_model import Invoice
from lib.models.invoice_c_type_footer import CFooter

#Enums
from lib.enums.invoice_type_enum import Invoice_type

#Functions
from lib.functions.add_borders import addBorder
from lib.functions.create_images_from_boxes import createImagesFromImageBoxes
from lib.functions.crop_header_box_2 import cropHeaderBox2
from lib.functions.delete_files_in_folder import deleteFilesInFolder
from lib.functions.get_footer import getFooter
from lib.functions.get_header import getHeader
from lib.functions.get_items import getItems
from lib.functions.get_smallest_image_path import getSmallestImagePath
from lib.functions.image_cleaning import imageCleaning
from lib.functions.perspective_transform import perspective_transform
from lib.functions.process_image import processImage

######## MAIN SCRIPT ########

####### Funciones #######





def edgeCleaning(
    image,
    path,
    paddingToPaint=10,
    top=False,
    left=False,
    right=False,
    bottom=False,
    all=False,
):
    if left or all:
        cv2.rectangle(
            image, (0, 0), (paddingToPaint, image.shape[0]), (255, 255, 255), -1
        )
    if top or all:
        cv2.rectangle(
            image, (0, 0), (image.shape[1], paddingToPaint), (255, 255, 255), -1
        )
    if right or all:
        cv2.rectangle(
            image,
            (image.shape[1] - paddingToPaint, 0),
            (image.shape[1], image.shape[0]),
            (255, 255, 255),
            -1,
        )
    if bottom or all:
        cv2.rectangle(
            image,
            (0, image.shape[0] - paddingToPaint),
            (image.shape[1], image.shape[0]),
            (255, 255, 255),
            -1,
        )
    cv2.imwrite(path, image)
    return image


def remove_lines_from_image(image):
    result = image.copy()
    thresh = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    # Remove horizontal lines
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 1))
    remove_horizontal = cv2.morphologyEx(
        thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=2
    )
    cnts = cv2.findContours(
        remove_horizontal, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
        cv2.drawContours(result, [c], -1, (255, 255, 255), 5)
    # Remove vertical lines
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 20))
    remove_vertical = cv2.morphologyEx(
        thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=2
    )
    cnts = cv2.findContours(remove_vertical, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
        cv2.drawContours(result, [c], -1, (255, 255, 255), 5)
    return result


def getVerticalLinePosition(image):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[
        1
    ]
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 20))
    remove_vertical = cv2.morphologyEx(
        thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=2
    )
    cnts = cv2.findContours(remove_vertical, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    sum = 0

    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        sum += x

    return sum


def areHeaderMainBoxesInverted(header1, header2):
    header1Sum = getVerticalLinePosition(header1)
    header2Sum = getVerticalLinePosition(header2)

    if header1Sum > header2Sum:
        return True
    else:
        return False


def invertFileNames(file1Path, file2Path):
    os.rename(file1Path, "pretemp/aux.png")
    os.rename(file2Path, file1Path)
    os.rename("pretemp/aux.png", file2Path)


def reduceToBiggestByArea(folder, file_name_prefix):
    biggestArea = 0
    for file in os.listdir(folder):
        filename = os.fsdecode(file)
        if filename.startswith(file_name_prefix) and filename.find("wol") == -1:
            file_path = os.path.join(folder, filename)
            image = cv2.imread(file_path)
            if image.shape[0] * image.shape[1] > biggestArea:
                biggestArea = image.shape[0] * image.shape[1]
                imageToSave = image

    deleteFilesInFolder("./" + folder, fileNamePrefix=file_name_prefix)
    cv2.imwrite(os.path.join(folder, file_name_prefix) + "_1.png", imageToSave)
    gray_image = cv2.cvtColor(imageToSave, cv2.COLOR_BGR2GRAY)
    invoiceWithoutLines = remove_lines_from_image(gray_image)
    cv2.imwrite(
        os.path.join(folder, file_name_prefix) + "_1_wol.png", invoiceWithoutLines
    )


def getInvoiceType():
    # Obtiene el tipo de factura
    image = cv2.imread(getSmallestImagePath(dir="temp", fileNamePrefix="header_box"))
    processImage(
        imageToProcess=image,
        rectDimensions=(1, 1),
        boxWidthTresh=25,
        boxHeightTresh=25,
        folder="pretemp",
        outputImagePrefix="invoice_type_image",
    )

    image = cv2.imread("pretemp/invoice_type_image_1.png")
    addBorder(image, "pretemp/invoice_type_image_1.png")
    image = cv2.imread("pretemp/invoice_type_image_1.png")
    ocr_result = pytesseract.image_to_string(image, lang="spa", config="--psm 6")
    ocr_result = ocr_result.replace("\n\x0c", "")

    match ocr_result:
        case "A":
            invoice_type = Invoice_type.A
        case "B":
            invoice_type = Invoice_type.B
        case "C":
            invoice_type = Invoice_type.C
        case _:
            print("Error")

    return invoice_type


####### Código principal #######


def preprocessImage(isPerfectImage):
    starting_image_path = "data/factura.png"
    original_img = cv2.imread(starting_image_path)

    if isPerfectImage:
        image = imageCleaning(original_img)
    else:
        image = preprocess_image(original_img)
        image = edgeCleaning(
            image=image, path="data/page_preprocessed.png", paddingToPaint=10, all=True
        )

    # Obtenemos duplicado sin líneas en el cuerpo de la factura
    invoiceWithoutLines = remove_lines_from_image(image)
    cv2.imwrite("data/page_without_lines.png", invoiceWithoutLines)

    # Separación inicial, remueve bordes de los costados
    processImage(
        imageToProcess=image,
        imageWoLines=invoiceWithoutLines,
        rectDimensions=(1, 100),
        boxWidthTresh=100,
        boxHeightTresh=100,
        folder="pretemp",
        outputImagePrefix="invoice_aux",
        savePreprocessingImages=False,
        isImageGray=True,
    )

    # Obtiene de encabezado, además tambien remueve los bordes superiores e inferiores
    image = cv2.imread("pretemp/invoice_aux_1.png")
    imageWol = cv2.imread("pretemp/invoice_aux_1_wol.png")
    processImage(
        imageToProcess=image,
        imageWoLines=imageWol,
        rectDimensions=(100, 15),
        boxWidthTresh=100,
        boxHeightTresh=100,
        folder="pretemp",
        outputImagePrefix="header",
    )

    # Obtiene pie, le remueve todo y conserva el encuadrado
    image = cv2.imread("pretemp/invoice_aux_2.png")
    imageWol = cv2.imread("pretemp/invoice_aux_2_wol.png")
    processImage(
        imageToProcess=image,
        imageWoLines=imageWol,
        rectDimensions=(3, 5),
        boxWidthTresh=200,
        boxHeightTresh=100,
        folder="pretemp",
        outputImagePrefix="footer",
    )

    # Del pie, se queda con el cuadro importante (sin marco) y desecha los demás

    def check_valid_footer_box(height, width):
        ratio = height / width
        return ratio > 0.15 and ratio < 0.35

    image = cv2.imread("pretemp/footer_1.png", 0)
    imageWol = cv2.imread("pretemp/footer_1_wol.png", 0)
    createImagesFromImageBoxes(
        imageToProcess=image,
        imageWoLines=imageWol,
        savePreprocessingImages=False,
        originalName="footer",
        check_function=check_valid_footer_box,
    )

    reduceToBiggestByArea("temp", "footer_box")

    # Obtiene los items del cuerpo de la factura
    image = cv2.imread("pretemp/invoice_aux_1.png")
    processImage(
        imageToProcess=image,
        rectDimensions=(500, 5),
        boxWidthTresh=100,
        boxHeightTresh=150,
        folder="temp",
        outputImagePrefix="item",
        higherThanHeight=False,
    )

    # Recorta cada una de las "cajas" del encabezado

    def check_valid_header_boxes(height, width):
        ratio = height / width
        return ratio > 0.1 and ratio < 1 and height * width > 6000

    image = cv2.imread("pretemp/header_1.png", 0)
    imageWol = cv2.imread("pretemp/header_1_wol.png", 0)
    createImagesFromImageBoxes(
        imageToProcess=image,
        imageWoLines=imageWol,
        savePreprocessingImages=False,
        originalName="header",
        check_function=check_valid_header_boxes,
    )

    # Chequeamos que el encabezado 1 y 2 están bien ubicados (problema viene de ver cual es primero por ser del mismo tamaño)
    header1 = cv2.imread("temp/header_box_1.png")
    header2 = cv2.imread("temp/header_box_2.png")
    if areHeaderMainBoxesInverted(header1=header1, header2=header2):
        invertFileNames("temp/header_box_1.png", "temp/header_box_2.png")
        invertFileNames("temp/header_box_1_wol.png", "temp/header_box_2_wol.png")

    # Recorte del resto del tipo de factura en los dos cuadros donde estorba en la esquina
    image = cv2.imread("temp/header_box_1_wol.png")
    processImage(
        imageToProcess=image,
        rectDimensions=(10, 500),
        boxWidthTresh=50,
        boxHeightTresh=1,
        folder="temp",
        outputImagePrefix="header_box",
        outPutImageSufix="_wol",
        savePreprocessingImages=False,
    )

    image = cv2.imread("temp/header_box_2_wol.png")
    cropHeaderBox2(image)

    image = cv2.imread("temp/header_box_2_wol.png")
    processImage(
        imageToProcess=image,
        rectDimensions=(500, 34),
        boxWidthTresh=1,
        boxHeightTresh=100,
        folder="temp",
        outputImagePrefix="header_box",
        outPutImageSufix="_wol",
        startingIndex=2,
        savePreprocessingImages=False,
    )


################## API ########################
app = FastAPI()


@app.get("/")
def read_root():
    return {"welcome_message: Welcome to Extructura"}

global invoice_type
global header
global footer
global items


class Image(BaseModel):
    base64Image: str
    isPerfectImage: bool


@app.post("/recieve_image")
def send_image(image: Image):
    with open("data/factura.png", "wb") as f:
        f.write(decodebytes(str.encode(image.base64Image)))
    preprocessImage(image.isPerfectImage)
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
