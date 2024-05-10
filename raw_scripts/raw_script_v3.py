#### Script para capturas del pdf, fotos de facturas tomadas con un celular e imágenes capturadas por un escáner ####
import sys
import os
import cv2
import pytesseract
import time

 
# getting the name of the directory
# where the this file is present.
current = os.path.dirname(os.path.realpath(__file__))
 
# Getting the parent directory name
# where the current directory is present.
parent = os.path.dirname(current)
 
# adding the parent directory to 
# the sys.path.
sys.path.append(parent)

from lib.functions.utils.delete_file import delete_file
from lib.models.invoice_model import Invoice

from api.functions.get_footer import getFooter
from api.functions.get_header import getHeader
from api.functions.get_items import getItems
from lib.enums.image_type_enum import Image_type
from lib.enums.invoice_type_enum import InvoiceType
from lib.functions.invoice_related.are_header_boxes_inverted import areHeaderMainBoxesInverted
from lib.functions.invoice_related.paint_header_box_2_title_and_box import paintHeaderBox2TitleAndBox
from lib.functions.testing.test_result import testResult
from lib.functions.utils.add_border import addBorder
from lib.functions.utils.add_borders import addBorders
from lib.functions.utils.check_if_image_has_lines import checkIfImageHasLines
from lib.functions.utils.create_images_from_boxes import createImagesFromImageBoxes
from lib.functions.utils.delete_files_in_folder import deleteFilesInFolder
from lib.functions.utils.edge_cleaning import edgeCleaning
from lib.functions.utils.get_smallest_image_path import getSmallestImagePath
from lib.functions.utils.image_cleaning import imageCleaning
from lib.functions.utils.invert_two_file_names import invertTwoFileNames
from lib.functions.utils.preprocess_image import preprocess_image
from lib.functions.utils.process_image import processImage
from lib.functions.utils.reduce_to_biggest_by_area import reduceToBiggestByArea
from lib.functions.utils.remove_lines_from_image import removeLinesFromImage

###### Código principal ###########################################################################################################################################

# Borramos los archivos en las carpetas, por si quedó basura
deleteFilesInFolder("images/data")
deleteFilesInFolder("images/pretemp")
deleteFilesInFolder("images/temp")
deleteFilesInFolder("images/processing")

start_time = time.time()

starting_image_path = "raw_scripts/testing/30.png"
image_type = Image_type.pdf
image = cv2.imread(starting_image_path)

# Preprocesamos la imágen según el tipo de imágen
match image_type:
    case Image_type.pdf:
        image = imageCleaning(image)
        cv2.imwrite("images/data/page_preprocessed.png", image)
    case Image_type.photo:
        image = preprocess_image(image)
        image = edgeCleaning(
            image=image, path="images/data/page_preprocessed.png", paddingToPaint=10, all=True
        )
        cv2.imwrite("images/data/page_preprocessed.png", image)
    case Image_type.scan:
        image = addBorders(image, size=30, color=[125, 0, 255])
        cv2.imwrite("images/data/page_preprocessed.png", image)
        image = preprocess_image(image)
        image = edgeCleaning(
            image=image, path="images/data/page_preprocessed.png", paddingToPaint=10, all=True
        )

        from wand.image import Image

        with Image(filename="images/data/page_preprocessed.png") as img:
            img.deskew(0.4 * img.quantum_range)
            img.save(filename="images/data/page_preprocessed.png")

    case _:
        print("Error")

# Obtenemos duplicado sin líneas en el cuerpo de la factura
image = cv2.imread("images/data/page_preprocessed.png")
invoiceWithoutLines = removeLinesFromImage(image)
cv2.imwrite("images/data/page_without_lines.png", invoiceWithoutLines)

# Separación inicial, remueve bordes de los costados
processImage(
    imageToProcessPath="images/data/page_preprocessed.png",
    imageWoLines=invoiceWithoutLines,
    rectDimensions=(1, 100),
    boxWidthTresh=100,
    boxHeightTresh=100,
    folder="images/pretemp",
    outputImagePrefix="invoice_aux",
    savePreprocessingImages=False,
)

# Obtiene de encabezado, además tambien remueve los bordes superiores e inferiores
imageWol = cv2.imread("images/pretemp/invoice_aux_1_wol.png")
processImage(
    imageToProcessPath="images/pretemp/invoice_aux_1.png",
    imageWoLines=imageWol,
    rectDimensions=(100, 15),
    boxWidthTresh=100,
    boxHeightTresh=100,
    folder="images/pretemp",
    outputImagePrefix="header",
)

# Obtiene pie, le remueve todo y conserva el encuadrado
imageWol = cv2.imread("images/pretemp/invoice_aux_2_wol.png")
processImage(
    imageToProcessPath="images/pretemp/invoice_aux_2.png",
    imageWoLines=imageWol,
    rectDimensions=(3, 5),
    boxWidthTresh=200,
    boxHeightTresh=100,
    folder="images/pretemp",
    outputImagePrefix="footer",
)

# Del pie, se queda con el cuadro importante (sin marco) y desecha los demás

def check_valid_footer_box(height, width):
    ratio = height / width
    return ratio > 0.15 and ratio < 0.35

image = cv2.imread("images/pretemp/footer_1.png", 0)
imageWol = cv2.imread("images/pretemp/footer_1_wol.png", 0)
createImagesFromImageBoxes(
    imageToProcess=image,
    imageWoLines=imageWol,
    savePreprocessingImages=False,
    originalName="footer",
    check_function=check_valid_footer_box,
)

reduceToBiggestByArea(folder="images/temp", file_name_prefix="footer_box")

# Se divide la imágen que tiene los items...
processImage(
    imageToProcessPath="images/pretemp/invoice_aux_1.png",
    rectDimensions=(500, 6),
    boxWidthTresh=100,
    boxHeightTresh=2000, #No importa este valor
    folder="images/temp",
    outputImagePrefix="item",
    higherThanHeight=False,
)

#... para luego eliminar los recortes que no sean
directory_in_str = "images/temp"
directory = os.fsencode(directory_in_str)
for file in os.listdir(directory):
    filename = os.fsdecode(file)
    if filename.startswith("item"):
        img_file_path = "images/temp/" + filename
        image = cv2.imread(img_file_path)
        if checkIfImageHasLines(image):
           delete_file(img_file_path)

# Recorta cada una de las "cajas" del encabezado

def check_valid_header_boxes(height, width):
    ratio = height / width
    return height > 70 and height < 240 and width > 80 and height < 1130 and ratio > 0.1 and ratio < 1

image = cv2.imread("images/pretemp/header_1.png", 0)
imageWol = cv2.imread("images/pretemp/header_1_wol.png", 0)
createImagesFromImageBoxes(
    imageToProcess=image,
    imageWoLines=imageWol,
    savePreprocessingImages=False,
    originalName="header",
    verticalDialationIterations=9 if image_type == Image_type.scan else 3,
    horizontalDialationIterations=9 if image_type == Image_type.scan else 3,
    check_function=check_valid_header_boxes,
)

# Chequeamos que el encabezado 1 y 2 están bien ubicados (problema viene de ver cual es primero por ser del mismo tamaño)
header1 = cv2.imread("images/temp/header_box_1.png")
header2 = cv2.imread("images/temp/header_box_2.png")
if areHeaderMainBoxesInverted(header1=header1, header2=header2):
    invertTwoFileNames("images/temp/header_box_1.png",
                        "images/temp/header_box_2.png")
    invertTwoFileNames("images/temp/header_box_1_wol.png",
                        "images/temp/header_box_2_wol.png")

# Recorte del resto del tipo de factura en los dos cuadros donde estorba en la esquina
processImage(
    imageToProcessPath="images/temp/header_box_1_wol.png",
    rectDimensions=(10, 500),
    boxWidthTresh=50,
    boxHeightTresh=1,
    folder="images/temp",
    outputImagePrefix="header_box",
    outPutImageSufix="_wol",
)

image = cv2.imread("images/temp/header_box_2.png")
imageWol = cv2.imread("images/temp/header_box_2_wol.png")
paintHeaderBox2TitleAndBox(image, imageWol)

# Obtiene el tipo de factura
processImage(
    imageToProcessPath=getSmallestImagePath(
        dir="images/temp", fileNamePrefix="header_box"),
    rectDimensions=(1, 1),
    boxWidthTresh=25,
    boxHeightTresh=25,
    folder="images/pretemp",
    outputImagePrefix="invoice_type_image",
)

image = cv2.imread("images/pretemp/invoice_type_image_1.png")
addBorder(image, "images/pretemp/invoice_type_image_1.png")
image = cv2.imread("images/pretemp/invoice_type_image_1.png")
ocr_result = pytesseract.image_to_string(
    image, lang="spa", config="--psm 6")
ocr_result = ocr_result.replace("\n\x0c", "")

match ocr_result:
    case "A":
        invoice_type = InvoiceType.A
    case "B":
        invoice_type = InvoiceType.B
    case "C":
        invoice_type = InvoiceType.C
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
deleteFilesInFolder("images/data")
deleteFilesInFolder("images/pretemp")
deleteFilesInFolder("images/temp")
deleteFilesInFolder("images/processing")

print("Process finished --- %s seconds ---" % (time.time() - start_time))

# Prueba de eficacia del resultado: cambiar el numero para comparar con un json distinto (verificar que exista antes) 

perfectInvoiceJsonFileName = '01'
analizedInvoice = Invoice(type=invoice_type.name, header=header, items=items, footer=footer)

# testResult(analizedInvoice, jsonPath = 'json/' + perfectInvoiceJsonFileName + '.json') #, perfectInvoice)

#Para generar el json que se modificará para ser el perfecto, eliminar después
import json
print(json.dumps(analizedInvoice, default=lambda analizedInvoice: analizedInvoice.__dict__))

