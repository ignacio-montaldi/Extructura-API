# Fast API
from fastapi import FastAPI, HTTPException, File, UploadFile
from pydantic import BaseModel
from typing import Text, Optional
from datetime import datetime
from uuid import uuid4 as uuid

# Scanning
import shutil
import os
import cv2
import pytesseract
from PIL import Image

# Image Decoding
from base64 import decodebytes

# Other
from enum import Enum


app = FastAPI()

posts = []

######## MAIN SCRIPT ########


# ####### Modelos #######

class Invoice_type(Enum):
    A = 1
    B = 2
    C = 3


class AItem:
    def __init__(self, cod, title, amount, measure, unit_price, discount_perc, subtotal, iva_fee, subtotal_inc_fees):
        self.cod = cod
        self.title = title
        self.amount = amount
        self.measure = measure
        self.unit_price = unit_price
        self.discount_perc = discount_perc
        self.subtotal = subtotal
        self.iva_fee = iva_fee
        self.subtotal_inc_fees = subtotal_inc_fees


class CItem:
    def __init__(self, cod, title, amount, measure, unit_price, discount_perc, discounted_subtotal, subtotal):
        self.cod = cod
        self.title = title
        self.amount = amount
        self.measure = measure
        self.unit_price = unit_price
        self.discount_perc = discount_perc
        self.discounted_subtotal = discounted_subtotal
        self.subtotal = subtotal


def saveCroppedImages(originalImage, preprocededImage, startingIndex, boxWidthTresh, boxHeightTresh, outputImagePrefix, higherThanHeight, folder, reverseSorting):
    # Encuentra los contornos
    cnts = cv2.findContours(
        preprocededImage, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    # Ordena los contornos, más grandes primero
    cnts = sorted(cnts, key=lambda x: cv2.boundingRect(x)[1])

    index = startingIndex
    if reverseSorting:
        cnts.reverse()

    # Guarda las imágenes recortadas según sus contornos, si sus ancho/alto son mayores o menores a unos valorores por parámetro
    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        if higherThanHeight:
            if w > boxWidthTresh and h > boxHeightTresh:
                roi = originalImage[y:y+h, x:x+w]
                fileName = folder + "/" + outputImagePrefix + \
                    "_" + str(index) + ".png"
                cv2.imwrite(fileName, roi)
                index += 1
        else:
            if w > boxWidthTresh and h < boxHeightTresh:
                roi = originalImage[y:y+h, x:x+w]
                fileName = folder + "/" + outputImagePrefix + \
                    "_" + str(index) + ".png"
                cv2.imwrite(fileName, roi)
                index += 1


def processImage(image, rectDimensions, startingIndex, boxWidthTresh, boxHeightTresh, outputImagePrefix, higherThanHeight, folder, savePreprocessingImages, reverseSorting):
    # Poner en blanco y negro la imágen, nada mas
    gray = cv2.cvtColor(image, cv2. COLOR_BGR2GRAY)

    # Difuminar la imágen, permite agrupar objetos (es decir, hacer menos legible su separacion) en la imágen para el siguiente paso Kernel positivo e impar
    blur = cv2.GaussianBlur(gray, (7, 7), 0)

    # Pone en blanco o negro según si el color del pixel se parece mas a uno u otro
    thresh = cv2.threshold(
        blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # En base a las dimensiones de un rectángulo estira los pixeles blancos, para así agrupar objetos
    kernal = cv2.getStructuringElement(cv2.MORPH_RECT, rectDimensions)
    dilate = cv2.dilate(thresh, kernal, iterations=1)

    # Para demostración, se ve paso a paso lo explicado arriba, se puede borrar después
    if (savePreprocessingImages):
        cv2.imwrite("pretemp/invoice_gray.png", gray)
        cv2.imwrite("pretemp/invoice_blur.png", blur)
        cv2.imwrite("pretemp/invoice_thresh.png", thresh)
        cv2.imwrite("pretemp/invoice_dialate.png", dilate)

    saveCroppedImages(originalImage=image,
                      preprocededImage=dilate, startingIndex=startingIndex, boxWidthTresh=boxWidthTresh, boxHeightTresh=boxHeightTresh, outputImagePrefix=outputImagePrefix, higherThanHeight=higherThanHeight, folder=folder, reverseSorting=reverseSorting)

# Borra los archivos temporales


def deleteFilesInFolder(folderPath):
    folder = folderPath
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


####### Código principal #######

def image_cropping():
    starting_image_path = "data/factura.png"

    image = cv2.imread(starting_image_path)
    processImage(image=image, rectDimensions=(1, 100),
                 startingIndex=1, boxWidthTresh=100,  boxHeightTresh=100, folder="pretemp", outputImagePrefix="invoice_aux", higherThanHeight=True, savePreprocessingImages=True, reverseSorting=False)

    # Obtiene encabezado, además tambien remueve los bordes superiores e inferiores
    image2 = cv2.imread("pretemp/invoice_aux_1.png")
    processImage(image=image2, rectDimensions=(100, 15),
                 startingIndex=1,  boxWidthTresh=100, boxHeightTresh=100, folder="temp", outputImagePrefix="header", higherThanHeight=True, savePreprocessingImages=True, reverseSorting=False)

    # Obtiene pie, le remueve todo y conserva el encuadrado
    image3 = cv2.imread("pretemp/invoice_aux_2.png")
    processImage(image=image3, rectDimensions=(3, 5), startingIndex=1,
                 boxWidthTresh=200, boxHeightTresh=100, folder="temp", outputImagePrefix="footer", higherThanHeight=True, savePreprocessingImages=True, reverseSorting=False)

    # Obtiene los items del cuerpo de la factura
    image4 = cv2.imread("pretemp/invoice_aux_1.png")
    processImage(image=image4, rectDimensions=(500, 5),
                 startingIndex=1,  boxWidthTresh=100, boxHeightTresh=50, folder="temp", outputImagePrefix="item", higherThanHeight=False, savePreprocessingImages=True, reverseSorting=False)

    image5 = cv2.imread(starting_image_path)
    invoice_type_image = image5[88:186,
                                (image5.shape[1]//2)-48:(image5.shape[1]//2)+48]
    processImage(image=invoice_type_image, rectDimensions=(1, 1),
                 startingIndex=1,  boxWidthTresh=30, boxHeightTresh=30, folder="pretemp", outputImagePrefix="invoice_type_image", higherThanHeight=True, savePreprocessingImages=True, reverseSorting=False)

    image5 = cv2.imread("pretemp/invoice_type_image_1.png")
    ocr_result = pytesseract.image_to_string(
        image5, lang='spa', config='--psm 6')
    ocr_result = ocr_result.replace('\n\x0c', '')

    match ocr_result:
        case "A":
            invoice_type = Invoice_type.A
        case "B":
            invoice_type = Invoice_type.B
        case "C":
            invoice_type = Invoice_type.C
        case _:
            print("Error")

    # # Borramos los archivos del preprocesado
    deleteFilesInFolder('./pretemp')

    return invoice_type


def item_processing(invoice_type: Invoice_type):
    directory_in_str = "./temp"
    directory = os.fsencode(directory_in_str)

    items = []

    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.startswith("item"):

            img_file = "temp/" + filename
            image = cv2.imread(img_file)
            processImage(image=image, rectDimensions=(10, 100),
                         startingIndex=1,  boxWidthTresh=0, boxHeightTresh=0, folder="temp", outputImagePrefix="value", higherThanHeight=True, savePreprocessingImages=False, reverseSorting=True)

            directory_in_str = "./temp"
            directory = os.fsencode(directory_in_str)

            valuesStr = []

            for file in os.listdir(directory):
                filename = os.fsdecode(file)
                if filename.startswith("value"):
                    img_file = "temp/" + filename
                    image = cv2.imread(img_file)
                    ocr_result = pytesseract.image_to_string(
                        image, lang='spa', config='--psm 6')
                    ocr_result = ocr_result.replace('\n\x0c', '')
                    ocr_result = ocr_result.replace('\n', ' ')
                    valuesStr.append(ocr_result)
            if (invoice_type == Invoice_type.A):
                item = AItem(valuesStr[0], valuesStr[1], valuesStr[2], valuesStr[3],
                             valuesStr[4], valuesStr[5], valuesStr[6], valuesStr[7], valuesStr[8])
            else:
                item = CItem(valuesStr[0], valuesStr[1], valuesStr[2], valuesStr[3],
                             valuesStr[4], valuesStr[5], valuesStr[6], valuesStr[7])

            items.append(item)
        else:
            continue
    deleteFilesInFolder('./temp')
    return items

###################################################################

# Post Model


# class Post(BaseModel):
#     id: Optional[str]
#     title: str
#     author: str
#     content: Text
#     created_at: datetime = datetime.now()
#     published_at: Optional[datetime]
#     published: bool = False


@app.get('/')
def read_root():
    return {"welcome_message: Welcome to Extractur"}


# @app.get('/posts')
# def get_posts():
#     return posts


# @app.post('/posts')
# def save_post(post: Post):

#     post.id = str(uuid())
#     posts.append(post.dict())
#     return posts[-1]  # -1 devuelve el último item


# @app.get('/posts/{post_id}')
# def get_post(post_id: str):
#     for post in posts:
#         if post["id"] == post_id:
#             return post
#     raise HTTPException(status_code=404, detail="Post not found")


# @app.delete("/posts/{post_id}")
# def delete_post(post_id: str):
#     for index, post in enumerate(posts):
#         if post["id"] == post_id:
#             posts.pop(index)
#             return {"message": "Post has been deleted successfully"}
#     raise HTTPException(status_code=404, detail="Post not found")


# @app.put('/posts/{post_id}')
# def update_post(post_id: str, updatedPost: Post):
#     for index, post in enumerate(posts):
#         if post["id"] == post_id:
#             posts[index]["title"] = updatedPost.title
#             posts[index]["content"] = updatedPost.content
#             posts[index]["author"] = updatedPost.author
#             return {"message": "Post has been updated successfully"}
#     raise HTTPException(status_code=404, detail="Post not found")


@app.get('/items')
def get_items():
    image_cropping()
    items = item_processing()
    return items


class Image(BaseModel):
    base64Image: str


@app.post('/send_image')
def send_image(image: Image):
    with open("data/factura.png", "wb") as f:
        f.write(decodebytes(str.encode(image.base64Image)))
    invoice_type = image_cropping()
    items = item_processing(invoice_type=invoice_type)
    deleteFilesInFolder('./data')
    return items
