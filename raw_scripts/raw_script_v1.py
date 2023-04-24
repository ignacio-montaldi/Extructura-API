#### Script para capturas del pdf unicamente ####

import shutil
import os
import cv2

import pytesseract
from PIL import Image
import numpy as np

from enum import Enum


# ####### Modelos #######

class Invoice_type(Enum):
    A = 1
    B = 2
    C = 3


class InvoiceHeader:
    def __init__(self, business_name, business_address, vat_condition, document_type, checkout_aisle_number, document_number, issue_date, seller_cuit, gross_income, business_opening_date, client_cuit, client_name, client_vat_condition, client_address, sale_method):
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


class AFooter:
    def __init__(self, currency, net_amount_taxed, vat_27, vat_21, vat_10_5, vat_5, vat_2_5, vat_0, other_taxes_ammout, total):
        self.currency = currency
        self.net_amount_taxed = net_amount_taxed
        self.vat_27 = vat_27
        self.vat_21 = vat_21
        self.vat_10_5 = vat_10_5
        self.vat_5 = vat_5
        self.vat_2_5 = vat_2_5
        self.vat_0 = vat_0
        self.other_taxes_ammout = other_taxes_ammout
        self.total = total


class CFooter:
    def __init__(self, currency, sub_total, other_taxes_ammout, total):
        self.currency = currency
        self.sub_total = sub_total
        self.other_taxes_ammout = other_taxes_ammout
        self.total = total


####### Funciones #######


def saveCroppedImages(originalImage, proprocessedImage, startingIndex, boxWidthTresh, boxHeightTresh, outputImagePrefix, higherThanHeight, folder, reverseSorting):
    # Encuentra los contornos
    cnts = cv2.findContours(
        proprocessedImage, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
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


def processImage(image, rectDimensions, boxWidthTresh, boxHeightTresh, outputImagePrefix, folder, startingIndex=1, higherThanHeight=True, reverseSorting=False, savePreprocessingImages=False):
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
                      proprocessedImage=dilate, startingIndex=startingIndex, boxWidthTresh=boxWidthTresh, boxHeightTresh=boxHeightTresh, outputImagePrefix=outputImagePrefix, higherThanHeight=higherThanHeight, folder=folder, reverseSorting=reverseSorting)


# Devuelve el detalle de los productos


def getItems(invoice_type: Invoice_type):
    directory_in_str = "./temp"
    directory = os.fsencode(directory_in_str)

    items = []

    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.startswith("item"):

            img_file = "temp/" + filename
            image = cv2.imread(img_file)
            processImage(image=image, rectDimensions=(10, 100),
                         startingIndex=1,  boxWidthTresh=0, boxHeightTresh=0, folder="temp", outputImagePrefix="value", savePreprocessingImages=False, reverseSorting=True)

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
    return items

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


def getBoxesContours(img, originalName, savePreprocessingImages=False):
    # Thresholding the image
    (thresh, img_bin) = cv2.threshold(
        img, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    # Invert the image
    img_bin = 255-img_bin

    # Defining a kernel length
    kernel_length = np.array(img).shape[1]//80

    # A verticle kernel of (1 X kernel_length), which will detect all the verticle lines from the image.
    verticle_kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT, (1, kernel_length))
    # A horizontal kernel of (kernel_length X 1), which will help to detect all the horizontal line from the image.
    hori_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_length, 1))
    # A kernel of (3 X 3) ones.
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))

    # Morphological operation to detect vertical lines from an image
    img_temp1 = cv2.erode(img_bin, verticle_kernel, iterations=3)
    verticle_lines_img = cv2.dilate(img_temp1, verticle_kernel, iterations=3)

    # Morphological operation to detect horizontal lines from an image
    img_temp2 = cv2.erode(img_bin, hori_kernel, iterations=3)
    horizontal_lines_img = cv2.dilate(img_temp2, hori_kernel, iterations=3)

    # Weighting parameters, this will decide the quantity of an image to be added to make a new image.
    alpha = 0.5
    beta = 1.0 - alpha
    # This function helps to add two image with specific weight parameter to get a third image as summation of two image.
    img_final_bin = cv2.addWeighted(
        verticle_lines_img, alpha, horizontal_lines_img, beta, 0.0)
    img_final_bin = cv2.erode(~img_final_bin, kernel, iterations=2)
    (thresh, img_final_bin) = cv2.threshold(
        img_final_bin, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    # Find contours for image, which will detect all the boxes
    contours, hierarchy = cv2.findContours(
        img_final_bin, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # Sort all the contours by top to bottom.
    contours = sort_contours(contours, method="top-to-bottom")

    if (savePreprocessingImages):
        cv2.imwrite("pretemp/" + originalName +
                    "_binirized_image.jpg", img_bin)
        cv2.imwrite("pretemp/" + originalName +
                    "_verticle_lines.jpg", verticle_lines_img)
        cv2.imwrite("pretemp/" + originalName + "_horizontal_lines.jpg",
                    horizontal_lines_img)
        cv2.imwrite("pretemp/" + originalName +
                    "_combined_lines.jpg", img_final_bin)

    return contours


def createImagesFromImageBoxes(img, originalName, savePreprocessingImages=False):
    contours = getBoxesContours(
        img, originalName, savePreprocessingImages)

    idx = 0
    for c in contours:
        # Returns the location and width,height for every contour
        x, y, w, h = cv2.boundingRect(c)
        ratio = h/w
        if ratio > 0.1:
            idx += 1
            new_img = img[y:y+h, x:x+w]
            cv2.imwrite("temp/" + originalName + "_box_" +
                        str(idx) + '.png', new_img)


# Ordenación de contornos


def sort_contours(cnts, method="left-to-right"):
    # initialize the reverse flag and sort index
    reverse = False
    i = 0
    # handle if we need to sort in reverse
    if method == "right-to-left" or method == "bottom-to-top":
        reverse = True
    # handle if we are sorting against the y-coordinate rather than
    # the x-coordinate of the bounding box
    if method == "top-to-bottom" or method == "bottom-to-top":
        i = 1
    # construct the list of bounding boxes and sort them from top to
    # bottom
    boundingBoxes = [cv2.boundingRect(c) for c in cnts]
    (cnts, boundingBoxes) = zip(*sorted(zip(cnts, boundingBoxes),
                                        key=lambda b: b[1][i], reverse=reverse))
    # return the list of sorted contours and bounding boxes
    return cnts


def getSmallestImagePath(dir, fileNamePrefix):
    directory_in_str = "./" + dir
    directory = os.fsencode(directory_in_str)

    smallest_box = float('inf')
    smallest_box_image_path = ""

    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.startswith(fileNamePrefix):
            img_file = dir + "/" + filename
            image = cv2.imread(img_file)
            imageArea = image.shape[0]*image.shape[1]
            if (imageArea < smallest_box):
                smallest_box = imageArea
                smallest_box_image_path = img_file

    return smallest_box_image_path


def getHeaderConcept(img_file):
    image = cv2.imread(img_file)
    ocr_result = pytesseract.image_to_string(
        image, lang='spa', config='--psm 6')
    ocr_result = ocr_result.replace('\n\x0c', '')
    ocr_result = ocr_result.replace('\n', ' ')
    ocr_result = ocr_result[ocr_result.find(":")+1::].strip()
    return ocr_result


def getHeader():
    image = cv2.imread("temp/header_box_2.png")
    processImage(image=image, rectDimensions=(200, 10),
                 boxWidthTresh=1, boxHeightTresh=1, folder="processing", outputImagePrefix="header_concept_2")

    image = cv2.imread("temp/header_box_1.png")
    processImage(image=image, rectDimensions=(25, 1),
                 boxWidthTresh=1, boxHeightTresh=1, folder="processing", outputImagePrefix="header_concept_1")

    image = cv2.imread("temp/header_box_4.png")
    processImage(image=image, rectDimensions=(50, 5),
                 boxWidthTresh=1, boxHeightTresh=1, folder="processing", outputImagePrefix="header_concept_4")

    header = InvoiceHeader(business_name=getHeaderConcept(
        img_file="processing/header_concept_2_1.png"), business_address=getHeaderConcept(img_file="processing/header_concept_2_2.png"), vat_condition=getHeaderConcept(img_file="processing/header_concept_2_3.png"), document_type=getHeaderConcept(img_file="processing/header_concept_1_1.png"), document_number=getHeaderConcept(img_file="processing/header_concept_1_2.png"), checkout_aisle_number=getHeaderConcept(img_file="processing/header_concept_1_3.png"), issue_date=getHeaderConcept(img_file="processing/header_concept_1_4.png"), seller_cuit=getHeaderConcept(img_file="processing/header_concept_1_5.png"), gross_income=getHeaderConcept(img_file="processing/header_concept_1_6.png"), business_opening_date=getHeaderConcept(img_file="processing/header_concept_1_7.png"), client_cuit=getHeaderConcept(img_file="processing/header_concept_4_2.png"), client_name=getHeaderConcept(img_file="processing/header_concept_4_1.png"), client_address=getHeaderConcept(img_file="processing/header_concept_4_3.png"), client_vat_condition=getHeaderConcept(img_file="processing/header_concept_4_4.png"), sale_method=getHeaderConcept(img_file="processing/header_concept_4_5.png"))

    return header


def getFooterConcept(img_file):
    image = cv2.imread(img_file)
    ocr_result = pytesseract.image_to_string(
        image, lang='spa', config='--psm 6')
    ocr_result = ocr_result.replace('\n\x0c', '')
    ocr_result = ocr_result.replace('\n', ' ')
    return ocr_result


def getFooterCurrency(img_file):
    image = cv2.imread(img_file)
    ocr_result = pytesseract.image_to_string(
        image, lang='spa', config='--psm 6')
    ocr_result = ocr_result.replace('\n\x0c', '')
    ocr_result = ocr_result.replace('\n', ' ')
    ocr_result = ocr_result[ocr_result.find(":")+1::].strip()
    return ocr_result


def getFooter(invoice_type):
    # Esta parte chequea el el pie de la factura no contenga elementos extra innecesarios para traer los datos, de lo contrario, pinta recuadros blancos encima para evitar que molesten en el análisis
    # En caso de que haya datos extra --> should_paint == True
    image = cv2.imread("temp/footer_box_1.png")
    gray = cv2.cvtColor(image, cv2. COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (7, 7), 0)
    thresh = cv2.threshold(
        blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    kernal = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 50))
    dilate = cv2.dilate(thresh, kernal, iterations=1)
    cnts = cv2.findContours(
        dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    cnts = sorted(cnts, key=lambda x: cv2.boundingRect(x)[1])

    should_paint = False

    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        if w == image.shape[1]:
            should_paint = True

    if (should_paint):
        for c in cnts:
            x, y, w, h = cv2.boundingRect(c)
            if w < image.shape[1]:
                cv2.rectangle(image, (x, y), (x+w, y+h), (255, 255, 255), -1)

        cv2.imwrite("temp/footer_box_1.png", image)
        image = cv2.imread("temp/footer_box_1.png", 0)
        contours = getBoxesContours(
            image, "test", False)

        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            if w < image.shape[1]:
                cv2.rectangle(image, (x-5, y-5), (x+w+3, y+h+3),
                              (255, 255, 255), -1)
                cv2.imwrite("temp/footer_box_1.png", image)

    # Separa por un lado las claves y por otro los valores del pie de la factura
    image = cv2.imread("temp/footer_box_1.png")
    processImage(image=image, rectDimensions=(10, 200),
                 boxWidthTresh=1, boxHeightTresh=1, folder="processing", outputImagePrefix="footer_key_value")

    # Divide por partes las claves, de aquí usamos cualquiera (la primera) para obtener la moneda en que se operó en la factura
    image = cv2.imread("processing/footer_key_value_2.png")
    processImage(image=image, rectDimensions=(200, 1),
                 boxWidthTresh=1, boxHeightTresh=1, folder="processing", outputImagePrefix="footer_key")

    # #Divide por partes los valores
    image = cv2.imread("processing/footer_key_value_1.png")
    processImage(image=image, rectDimensions=(10, 10),
                 boxWidthTresh=1, boxHeightTresh=1, folder="processing", outputImagePrefix="footer_value")

    # Creo pie tipo RI o mono
    if (invoice_type == Invoice_type.A):
        footer = AFooter(net_amount_taxed=getFooterConcept(
            img_file="processing/footer_value_1.png"), vat_27=getFooterConcept(
            img_file="processing/footer_value_2.png"), vat_21=getFooterConcept(
            img_file="processing/footer_value_3.png"), vat_10_5=getFooterConcept(
            img_file="processing/footer_value_4.png"), vat_5=getFooterConcept(
            img_file="processing/footer_value_5.png"), vat_2_5=getFooterConcept(
            img_file="processing/footer_value_6.png"), vat_0=getFooterConcept(
            img_file="processing/footer_value_7.png"), other_taxes_ammout=getFooterConcept(
            img_file="processing/footer_value_8.png"), total=getFooterConcept(
            img_file="processing/footer_value_9.png"), currency=getFooterCurrency("processing/footer_key_1.png"))
    else:
        footer = CFooter(sub_total=getFooterConcept(
            img_file="processing/footer_value_1.png"), other_taxes_ammout=getFooterConcept(
            img_file="processing/footer_value_2.png"), total=getFooterConcept(
            img_file="processing/footer_value_3.png"), currency=getFooterCurrency("processing/footer_key_1.png"))
    return footer


# ####### Código principal #######
starting_image_path = "data/page4.png"

# Separación inicial, remueve bordes de los costados
image = cv2.imread(starting_image_path)
processImage(image=image, rectDimensions=(1, 100),
             boxWidthTresh=100,  boxHeightTresh=100, folder="pretemp", outputImagePrefix="invoice_aux")

# Obtiene de encabezado, además tambien remueve los bordes superiores e inferiores
image = cv2.imread("pretemp/invoice_aux_1.png")
processImage(image=image, rectDimensions=(100, 15),
             boxWidthTresh=100, boxHeightTresh=100, folder="pretemp", outputImagePrefix="header")

# Obtiene pie, le remueve todo y conserva el encuadrado
image = cv2.imread("pretemp/invoice_aux_2.png")
processImage(image=image, rectDimensions=(3, 5),
             boxWidthTresh=200, boxHeightTresh=100, folder="pretemp", outputImagePrefix="footer")

# Del pie, se queda con el cuadro importante (sin marco) y desecha los demás
image = cv2.imread("pretemp/footer_1.png", 0)
createImagesFromImageBoxes(
    img=image, savePreprocessingImages=False, originalName="footer")

# Obtiene los items del cuerpo de la factura
image = cv2.imread("pretemp/invoice_aux_1.png")
processImage(image=image, rectDimensions=(500, 5),
             boxWidthTresh=100, boxHeightTresh=50, folder="temp", outputImagePrefix="item", higherThanHeight=False)

# Recorta cada una de las "cajas" del encabezado
image = cv2.imread("pretemp/header_1.png", 0)
createImagesFromImageBoxes(
    img=image, savePreprocessingImages=False, originalName="header")

# Recorte del resto del tipo de factura en los dos cuadros donde estorba en la esquina
image = cv2.imread("temp/header_box_1.png")
processImage(image=image, rectDimensions=(10, 500),
             boxWidthTresh=50, boxHeightTresh=1, folder="temp", outputImagePrefix="header_box")

image = cv2.imread("temp/header_box_2.png")
processImage(image=image, rectDimensions=(500, 34),
             boxWidthTresh=1, boxHeightTresh=100, folder="temp", outputImagePrefix="header_box", startingIndex=2)

# Obtiene el tipo de factura
image = cv2.imread(getSmallestImagePath(
    dir="temp", fileNamePrefix="header_box"))
processImage(image=image, rectDimensions=(1, 1),
             boxWidthTresh=30, boxHeightTresh=30, folder="pretemp", outputImagePrefix="invoice_type_image")

image = cv2.imread("pretemp/invoice_type_image_1.png")
ocr_result = pytesseract.image_to_string(
    image, lang='spa', config='--psm 6')
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


#### GET HEADER CONCEPTS #####
header = getHeader()
print(header)

#### GET ITEMS #####
items = getItems(invoice_type)
print(items)

#### GET FOOTER CONCEPTS #####
footer = getFooter(invoice_type)
print(footer)

# Borramos los archivos generados para el analisis
deleteFilesInFolder('./pretemp')
deleteFilesInFolder('./temp')
deleteFilesInFolder('./processing')
