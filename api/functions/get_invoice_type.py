import cv2
import pytesseract

from lib.enums.invoice_type_enum import InvoiceType
from lib.functions.utils.add_border import addBorder
from lib.functions.utils.get_smallest_image_path import getSmallestImagePath
from lib.functions.utils.process_image import processImage


def getInvoiceType():
    # Obtiene el tipo de factura
    processImage(
        imageToProcessPath=getSmallestImagePath(
            dir="images/temp", fileNamePrefix="header_box"
        ),
        rectDimensions=(1, 1),
        boxWidthTresh=25,
        boxHeightTresh=25,
        folder="images/pretemp",
        outputImagePrefix="invoice_type_image",
    )

    image = cv2.imread("images/pretemp/invoice_type_image_1.png")
    addBorder(image, "images/pretemp/invoice_type_image_1.png")
    image = cv2.imread("images/pretemp/invoice_type_image_1.png")
    ocr_result = pytesseract.image_to_string(image, lang="spa", config="--psm 6")
    ocr_result = ocr_result.replace("\n\x0c", "")

    match ocr_result[0]:
        case "A":
            invoice_type = InvoiceType.A
        case "B":
            invoice_type = InvoiceType.B
        case "C":
            invoice_type = InvoiceType.C
        case _:
            print("Error")

    return invoice_type
