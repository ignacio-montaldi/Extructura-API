#### Script para capturas del pdf y para fotos de facturas tomadas con un celular ####

import shutil
import os
import sys
import cv2
import imutils
from skimage.filters import threshold_local

import pytesseract
from PIL import Image
import numpy as np

from matplotlib import pyplot as plt
from enum import Enum

from fuzzywuzzy import fuzz
import re
import time
start_time = time.time()


# ####### Modelos #######


class Invoice:
    def __init__(self, type, header, items, footer):
        self.type = type
        self.header = header
        self.items = items
        self.footer = footer


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
    def __init__(self, currency, net_amount_taxed, vat_27, vat_21, vat_10_5, vat_5, vat_2_5, vat_0, other_taxes_ammout, total, exchange_rate):
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
        self.exchange_rate = exchange_rate


class CFooter:
    def __init__(self, currency, sub_total, other_taxes_ammout, total, exchange_rate):
        self.currency = currency
        self.sub_total = sub_total
        self.other_taxes_ammout = other_taxes_ammout
        self.total = total
        self.exchange_rate = exchange_rate


####### Funciones #######


def saveCroppedImages(originalImage, imageWoLines, proprocessedImage, startingIndex, boxWidthTresh, boxHeightTresh, outputImagePrefix, outPutImageSufix, higherThanHeight, folder, reverseSorting):
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
                    "_" + str(index) + outPutImageSufix + ".png"
                cv2.imwrite(fileName, roi)
                if (imageWoLines is not None):
                    roi = imageWoLines[y:y+h, x:x+w]
                    fileName = folder + "/" + outputImagePrefix + \
                        "_" + str(index) + "_wol" + outPutImageSufix + ".png"
                    cv2.imwrite(fileName, roi)
                index += 1
        else:
            if w > boxWidthTresh and h < boxHeightTresh:
                roi = originalImage[y:y+h, x:x+w]
                fileName = folder + "/" + outputImagePrefix + \
                    "_" + str(index) + outPutImageSufix + ".png"
                cv2.imwrite(fileName, roi)
                if (imageWoLines is not None):
                    roi = imageWoLines[y:y+h, x:x+w]
                    fileName = folder + "/" + outputImagePrefix + \
                        "_" + str(index) + "_wol" + outPutImageSufix + ".png"
                    cv2.imwrite(fileName, roi)
                index += 1


def processImage(imageToProcess, rectDimensions, boxWidthTresh, boxHeightTresh, outputImagePrefix, folder, outPutImageSufix="", imageWoLines=None, startingIndex=1, higherThanHeight=True, reverseSorting=False, savePreprocessingImages=False, isImageGray=False):
    # Poner en escala de grises la imágen, nada mas, si es que no viene ya lista
    if not (isImageGray):
        gray = cv2.cvtColor(imageToProcess, cv2.COLOR_BGR2GRAY)
    else:
        gray = imageToProcess

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

    saveCroppedImages(originalImage=imageToProcess,
                      imageWoLines=imageWoLines,
                      proprocessedImage=dilate, startingIndex=startingIndex, boxWidthTresh=boxWidthTresh, boxHeightTresh=boxHeightTresh, outputImagePrefix=outputImagePrefix, outPutImageSufix=outPutImageSufix, higherThanHeight=higherThanHeight, folder=folder, reverseSorting=reverseSorting)


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
            processImage(imageToProcess=image, rectDimensions=(10, 100),
                         startingIndex=1,  boxWidthTresh=14, boxHeightTresh=0, folder="temp", outputImagePrefix="value", savePreprocessingImages=False, reverseSorting=True)

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

# Borra los archivos temporales, si


def deleteFilesInFolder(folderPath, fileNamePrefix=None):
    folder = folderPath
    for filename in os.listdir(folder):
        if fileNamePrefix is None or filename.startswith(fileNamePrefix):
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


def createImagesFromImageBoxes(imageToProcess, originalName, imageWoLines=None, check_function=None, savePreprocessingImages=False):
    contours = getBoxesContours(
        imageToProcess, originalName, savePreprocessingImages)

    idx = 0
    for c in contours:
        # Returns the location and width,height for every contour
        x, y, w, h = cv2.boundingRect(c)
        if callable(check_function) and check_function(h, w):
            idx += 1
            new_img = imageToProcess[y:y+h, x:x+w]
            cv2.imwrite("temp/" + originalName + "_box_" +
                        str(idx) + '.png', new_img)
            if (imageWoLines is not None):
                new_img = imageWoLines[y:y+h, x:x+w]
                cv2.imwrite("temp/" + originalName + "_box_" +
                            str(idx) + '_wol.png', new_img)


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
    substrings = [':', ';', ',']
    ocr_result = ocr_result[find_first_character_of(
        ocr_result, *substrings)+1::].strip()
    return ocr_result


def find_first_character_of(instring, *substrings):
    pat = re.compile('|'.join([re.escape(s) for s in substrings]))
    match = pat.search(instring)
    if match is None:
        return -1
    else:
        return match.start()


def getHeaderConceptImproved(key_to_match, file_name_prefix):
    directory_in_str = "./processing"
    directory = os.fsencode(directory_in_str)

    image_path_containing_key = ""
    max_ratio = 0

    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.startswith(file_name_prefix):

            img_file_path = "processing/" + filename
            image = cv2.imread(img_file_path)
            ocr_result = pytesseract.image_to_string(
                image, lang='spa', config='--psm 6')
            ocr_result = ocr_result.replace('\n\x0c', '')
            ocr_result = ocr_result.replace('\n', ' ')
            substrings = [':', ';', ',']
            ocr_result = ocr_result[:find_first_character_of(
                ocr_result, *substrings):].strip()
            ratio = fuzz.ratio(ocr_result, key_to_match)
            if (ratio > max_ratio):
                max_ratio = ratio
                image_path_containing_key = img_file_path

    image = cv2.imread(image_path_containing_key)
    ocr_result = pytesseract.image_to_string(
        image, lang='spa', config='--psm 6')
    ocr_result = ocr_result.replace('\n\x0c', '')
    ocr_result = ocr_result.replace('\n', ' ')
    substrings = [':', ';', ',']
    ocr_result = ocr_result[find_first_character_of(
        ocr_result, *substrings)+1::].strip()
    return ocr_result


def getHeader():
    image = cv2.imread("temp/header_box_2_wol.png")
    processImage(imageToProcess=image, rectDimensions=(200, 9),
                 boxWidthTresh=1, boxHeightTresh=1, folder="processing", outputImagePrefix="header_concept_2")

    image = cv2.imread("temp/header_box_1_wol.png")
    processImage(imageToProcess=image, rectDimensions=(25, 1),
                 boxWidthTresh=1, boxHeightTresh=1, folder="processing", outputImagePrefix="header_concept_1")

    image = cv2.imread("temp/header_box_4_wol.png")
    processImage(imageToProcess=image, rectDimensions=(50, 5),
                 boxWidthTresh=1, boxHeightTresh=1, folder="processing", outputImagePrefix="header_concept_4")

    header = InvoiceHeader(business_name=getHeaderConcept(
        img_file="processing/header_concept_2_1.png"), business_address=getHeaderConcept(img_file="processing/header_concept_2_2.png"), vat_condition=getHeaderConcept(img_file="processing/header_concept_2_3.png"), document_type=getHeaderConcept(img_file="processing/header_concept_1_1.png"), document_number=getHeaderConcept(img_file="processing/header_concept_1_2.png"), checkout_aisle_number=getHeaderConcept(img_file="processing/header_concept_1_3.png"), issue_date=getHeaderConcept(img_file="processing/header_concept_1_4.png"), seller_cuit=getHeaderConcept(img_file="processing/header_concept_1_5.png"), gross_income=getHeaderConcept(img_file="processing/header_concept_1_6.png"), business_opening_date=getHeaderConcept(img_file="processing/header_concept_1_7.png"), client_cuit=getHeaderConceptImproved(file_name_prefix="header_concept_4", key_to_match="CUIT"), client_name=getHeaderConceptImproved(file_name_prefix="header_concept_4", key_to_match="Apellido y Nombre / Razón Social"), client_address=getHeaderConceptImproved(file_name_prefix="header_concept_4", key_to_match="Domicilio Comercial"), client_vat_condition=getHeaderConceptImproved(file_name_prefix="header_concept_4", key_to_match="Condición frente al IVA"), sale_method=getHeaderConceptImproved(file_name_prefix="header_concept_4", key_to_match="Condición de venta"))

    return header


def cropHeaderBox2(image):
    gray = cv2.cvtColor(image, cv2. COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (7, 7), 0)
    thresh = cv2.threshold(
        blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    kernal = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 14))
    dilate = cv2.dilate(thresh, kernal, iterations=1)
    cnts = cv2.findContours(
        dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    cnts = sorted(cnts, key=lambda x: cv2.boundingRect(x)[1])

    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        if (h/w) > 1 or h > 80:
            cv2.rectangle(image, (x, y), (x+w, y+h), (255, 255, 255), -1)

    cv2.imwrite("temp/header_box_2_wol.png", image)


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


def key(x, y, w, h):
    return ((x > 700 and x < 760) or (x > 30 and x < 60)) and ((w > 230 and w < 260) or (w > 915 and w < 960))


def value(x, y, w, h):
    return x > 950 and (w > 90 and w < 120)


def getFooter(invoice_type):
    # Esta parte chequea el el pie de la factura no contenga elementos extra innecesarios para traer los datos, de lo contrario, pinta recuadros blancos encima para evitar que molesten en el análisis
    # En caso de que haya datos extra --> should_paint == True
    image = cv2.imread("temp/footer_box_1_wol.png")
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

    has_exchange_box = False

    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        if ((x > 30 and x < 60) and (w > 915 and w < 960)):
            has_exchange_box = True
        if ((not key(x, y, w, h)) and (not value(x, y, w, h))):
            cv2.rectangle(image, (x, y), (x+w, y+h), (255, 255, 255), -1)

    cv2.imwrite("temp/footer_box_1_wol.png", image)

    # Si es A USD
    if (has_exchange_box):
        image = cv2.imread("temp/footer_box_1_wol.png")
        gray = cv2.cvtColor(image, cv2. COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (7, 7), 0)
        thresh = cv2.threshold(
            blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        kernal = cv2.getStructuringElement(cv2.MORPH_RECT, (200, 10))
        dilate = cv2.dilate(thresh, kernal, iterations=1)
        cnts = cv2.findContours(
            dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]
        cnts = sorted(cnts, key=lambda x: cv2.boundingRect(x)[1])

        for c in cnts:
            x, y, w, h = cv2.boundingRect(c)
            if w == image.shape[1]:
                new_img = image[y:y+h, x:x+w]
                cv2.imwrite("temp/footer_box_2_wol.png", new_img)
                cv2.rectangle(image, (x, y), (x+w, y+h),
                              (255, 255, 255), -1)
                cv2.imwrite("temp/footer_box_1_wol.png", image)

    try:
        image = cv2.imread("temp/footer_box_2_wol.png")
        ocr_result = pytesseract.image_to_string(
            image, lang='spa', config='--psm 6')
        ocr_result = ocr_result[ocr_result.find(
            "consignado de")+len("consignado de"):ocr_result.find("asciende")-1:].strip()
        exchange_rate = ocr_result
    except:
        exchange_rate = "1"

    # Separa por un lado las claves y por otro los valores del pie de la factura
    image = cv2.imread("temp/footer_box_1_wol.png")
    processImage(imageToProcess=image, rectDimensions=(10, 200),
                 boxWidthTresh=1, boxHeightTresh=1, folder="processing", outputImagePrefix="footer_key_value")

    # Divide por partes las claves, de aquí usamos cualquiera (la primera) para obtener la moneda en que se operó en la factura
    image = cv2.imread("processing/footer_key_value_2.png")
    processImage(imageToProcess=image, rectDimensions=(200, 1),
                 boxWidthTresh=1, boxHeightTresh=1, folder="processing", outputImagePrefix="footer_key")

    # Divide por partes los valores
    image = cv2.imread("processing/footer_key_value_1.png")
    processImage(imageToProcess=image, rectDimensions=(10, 5),
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
            img_file="processing/footer_value_9.png"), currency=getFooterCurrency("processing/footer_key_1.png"), exchange_rate=exchange_rate)
    else:
        footer = CFooter(sub_total=getFooterConcept(
            img_file="processing/footer_value_1.png"), other_taxes_ammout=getFooterConcept(
            img_file="processing/footer_value_2.png"), total=getFooterConcept(
            img_file="processing/footer_value_3.png"), currency=getFooterCurrency("processing/footer_key_1.png"), exchange_rate=exchange_rate)
    return footer

# Agrega bordes blancos a imagen


def addBorder(image, path):
    color = [255, 255, 255]
    top, bottom, left, right = [20]*4
    image_with_border = cv2.copyMakeBorder(
        image, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)
    cv2.imwrite(path, image_with_border)


def order_points(pts):
    # initializing the list of coordinates to be ordered
    rect = np.zeros((4, 2), dtype="float32")

    s = pts.sum(axis=1)
    # top-left point will have the smallest sum
    rect[0] = pts[np.argmin(s)]
    # bottom-right point will have the largest sum
    rect[2] = pts[np.argmax(s)]

    '''computing the difference between the points, the
	top-right point will have the smallest difference,
	whereas the bottom-left will have the largest difference'''
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]

    # returns ordered coordinates
    return rect


def perspective_transform(image, pts):
    # unpack the ordered coordinates individually
    rect = order_points(pts)
    (tl, tr, br, bl) = rect

    '''compute the width of the new image, which will be the
	maximum distance between bottom-right and bottom-left
	x-coordiates or the top-right and top-left x-coordinates'''
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))

    '''compute the height of the new image, which will be the
	maximum distance between the top-left and bottom-left y-coordinates'''
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))

    '''construct the set of destination points to obtain an overhead shot'''
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype="float32")

    # compute the perspective transform matrix
    transform_matrix = cv2.getPerspectiveTransform(rect, dst)
    # Apply the transform matrix
    warped = cv2.warpPerspective(
        image, transform_matrix, (maxWidth, maxHeight))

    # return the warped image
    return warped


def imageCleaning(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    T = threshold_local(gray, 15, offset=6, method="gaussian")
    warped = (gray > T).astype("uint8") * 255
    cv2.imwrite('./data/'+'page_preprocessed'+'.png', warped)
    resizedFinalResult = imutils.resize(warped, height=1684)
    return resizedFinalResult


def preprocess_image(original_img):
    copy = original_img.copy()

    # The resized height in hundreds
    ratio = original_img.shape[0] / 1684.0
    img_resize = imutils.resize(original_img, height=1684)

    gray_image = cv2.cvtColor(img_resize, cv2.COLOR_BGR2GRAY)

    blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 0)
    edged_img = cv2.Canny(blurred_image, 75, 200)
    cnts, _ = cv2.findContours(
        edged_img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:5]

    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)

        if len(approx) == 4:
            doc = approx
            break

    warped_image = perspective_transform(copy, doc.reshape(4, 2) * ratio)

    finalResult = imageCleaning(warped_image)

    cv2.imwrite('./data/'+'page_preprocessed'+'.png', finalResult)
    return finalResult


def edgeCleaning(image, path, paddingToPaint=10, top=False, left=False, right=False, bottom=False, all=False):
    if (left or all):
        cv2.rectangle(image, (0, 0), (paddingToPaint,
                      image.shape[0]), (255, 255, 255), -1)
    if (top or all):
        cv2.rectangle(
            image, (0, 0), (image.shape[1], paddingToPaint), (255, 255, 255), -1)
    if (right or all):
        cv2.rectangle(image, (image.shape[1]-paddingToPaint, 0),
                      (image.shape[1], image.shape[0]), (255, 255, 255), -1)
    if (bottom or all):
        cv2.rectangle(image, (0, image.shape[0]-paddingToPaint),
                      (image.shape[1], image.shape[0]), (255, 255, 255), -1)
    cv2.imwrite(path, image)
    return image


def remove_lines_from_image(image):
    result = image.copy()
    thresh = cv2.threshold(
        image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    # Remove horizontal lines
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 1))
    remove_horizontal = cv2.morphologyEx(
        thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
    cnts = cv2.findContours(
        remove_horizontal, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
        cv2.drawContours(result, [c], -1, (255, 255, 255), 5)
    # Remove vertical lines
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 20))
    remove_vertical = cv2.morphologyEx(
        thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=2)
    cnts = cv2.findContours(
        remove_vertical, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
        cv2.drawContours(result, [c], -1, (255, 255, 255), 5)
    return result


def getVerticalLinePosition(image):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(
        gray_image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 20))
    remove_vertical = cv2.morphologyEx(
        thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=2)
    cnts = cv2.findContours(
        remove_vertical, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    sum = 0

    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        sum += x

    return sum


def areHeaderMainBoxesInverted(header1, header2):

    header1Sum = getVerticalLinePosition(header1)
    header2Sum = getVerticalLinePosition(header2)

    if (header1Sum > header2Sum):
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
            if (image.shape[0]*image.shape[1] > biggestArea):
                biggestArea = image.shape[0]*image.shape[1]
                imageToSave = image

    deleteFilesInFolder("./"+folder, fileNamePrefix=file_name_prefix)
    cv2.imwrite(os.path.join(folder, file_name_prefix) + "_1.png", imageToSave)
    gray_image = cv2.cvtColor(imageToSave, cv2.COLOR_BGR2GRAY)
    invoiceWithoutLines = remove_lines_from_image(gray_image)
    cv2.imwrite(os.path.join(folder, file_name_prefix) +
                "_1_wol.png", invoiceWithoutLines)


###### Código principal ###########################################################################################################################################
starting_image_path = "raw_scripts/data/page1.png"
isPerfectImage = True
original_img = cv2.imread(starting_image_path)

if (isPerfectImage):
    image = imageCleaning(original_img)
else:
    image = preprocess_image(original_img)
    image = edgeCleaning(
        image=image, path='data/page_preprocessed.png', paddingToPaint=10, all=True)

# Obtenemos duplicado sin líneas en el cuerpo de la factura
invoiceWithoutLines = remove_lines_from_image(image)
cv2.imwrite('data/page_without_lines.png', invoiceWithoutLines)


# Separación inicial, remueve bordes de los costados
processImage(imageToProcess=image, imageWoLines=invoiceWithoutLines, rectDimensions=(1, 100),
             boxWidthTresh=100,  boxHeightTresh=100, folder="pretemp", outputImagePrefix="invoice_aux", savePreprocessingImages=False, isImageGray=True)

# Obtiene de encabezado, además tambien remueve los bordes superiores e inferiores
image = cv2.imread("pretemp/invoice_aux_1.png")
imageWol = cv2.imread("pretemp/invoice_aux_1_wol.png")
processImage(imageToProcess=image, imageWoLines=imageWol, rectDimensions=(100, 15),
             boxWidthTresh=100, boxHeightTresh=100, folder="pretemp", outputImagePrefix="header")

# Obtiene pie, le remueve todo y conserva el encuadrado
image = cv2.imread("pretemp/invoice_aux_2.png")
imageWol = cv2.imread("pretemp/invoice_aux_2_wol.png")
processImage(imageToProcess=image, imageWoLines=imageWol, rectDimensions=(3, 5),
             boxWidthTresh=200, boxHeightTresh=100, folder="pretemp", outputImagePrefix="footer")

# Del pie, se queda con el cuadro importante (sin marco) y desecha los demás


def check_valid_footer_box(height, width):
    ratio = height/width
    return ratio > 0.15 and ratio < 0.35


image = cv2.imread("pretemp/footer_1.png", 0)
imageWol = cv2.imread("pretemp/footer_1_wol.png", 0)
createImagesFromImageBoxes(
    imageToProcess=image, imageWoLines=imageWol, savePreprocessingImages=False, originalName="footer", check_function=check_valid_footer_box)

reduceToBiggestByArea("temp", "footer_box")

# Obtiene los items del cuerpo de la factura
image = cv2.imread("pretemp/invoice_aux_1.png")
processImage(imageToProcess=image, rectDimensions=(500, 5),
             boxWidthTresh=100, boxHeightTresh=150, folder="temp", outputImagePrefix="item", higherThanHeight=False)

# Recorta cada una de las "cajas" del encabezado


def check_valid_header_boxes(height, width):
    ratio = height/width
    return ratio > 0.1 and ratio < 1 and height*width > 6000


image = cv2.imread("pretemp/header_1.png", 0)
imageWol = cv2.imread("pretemp/header_1_wol.png", 0)
createImagesFromImageBoxes(
    imageToProcess=image, imageWoLines=imageWol, savePreprocessingImages=False, originalName="header", check_function=check_valid_header_boxes)

# Chequeamos que el encabezado 1 y 2 están bien ubicados (problema viene de ver cual es primero por ser del mismo tamaño)
header1 = cv2.imread("temp/header_box_1.png")
header2 = cv2.imread("temp/header_box_2.png")
if (areHeaderMainBoxesInverted(header1=header1, header2=header2)):
    invertFileNames("temp/header_box_1.png", "temp/header_box_2.png")
    invertFileNames("temp/header_box_1_wol.png", "temp/header_box_2_wol.png")

# Recorte del resto del tipo de factura en los dos cuadros donde estorba en la esquina
image = cv2.imread("temp/header_box_1_wol.png")
processImage(imageToProcess=image, rectDimensions=(10, 500),
             boxWidthTresh=50, boxHeightTresh=1, folder="temp", outputImagePrefix="header_box", outPutImageSufix="_wol", savePreprocessingImages=False)

image = cv2.imread("temp/header_box_2_wol.png")
cropHeaderBox2(image)

image = cv2.imread("temp/header_box_2_wol.png")
processImage(imageToProcess=image, rectDimensions=(500, 34),
             boxWidthTresh=1, boxHeightTresh=100, folder="temp", outputImagePrefix="header_box", outPutImageSufix="_wol", startingIndex=2, savePreprocessingImages=False)

# Obtiene el tipo de factura
image = cv2.imread(getSmallestImagePath(
    dir="temp", fileNamePrefix="header_box"))
processImage(imageToProcess=image, rectDimensions=(1, 1),
             boxWidthTresh=25, boxHeightTresh=25, folder="pretemp", outputImagePrefix="invoice_type_image")

image = cv2.imread("pretemp/invoice_type_image_1.png")
addBorder(image, "pretemp/invoice_type_image_1.png")
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


##### GET HEADER CONCEPTS #####
header = getHeader()
print(header)

##### GET ITEMS #####
items = getItems(invoice_type)
print(items)

##### GET FOOTER CONCEPTS #####
footer = getFooter(invoice_type)
print(footer)

# Borramos los archivos generados para el analisis
deleteFilesInFolder('./pretemp')
deleteFilesInFolder('./temp')
deleteFilesInFolder('./processing')

print("Process finished --- %s seconds ---" % (time.time() - start_time))
