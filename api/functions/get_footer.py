import os
import cv2
import pytesseract

from lib.enums.invoice_type_enum import InvoiceType

from lib.models.invoice_type_a_footer import AFooter
from lib.models.invoice_type_c_footer import CFooter

from lib.functions.invoice_related.get_footer_concept import getFooterConcept
from lib.functions.invoice_related.get_footer_currency import getFooterCurrency
from lib.functions.utils.process_image import processImage


def getFooter(invoice_type):
    # Esta parte chequea el el pie de la factura no contenga elementos extra innecesarios para traer los datos, de lo contrario, pinta recuadros blancos encima para evitar que molesten en el análisis
    # En caso de que haya datos extra --> should_paint == True
    image = cv2.imread("images/temp/footer_box_1_wol.png")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (7, 7), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    kernal = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 50))
    dilate = cv2.dilate(thresh, kernal, iterations=1)
    cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    cnts = sorted(cnts, key=lambda x: cv2.boundingRect(x)[1])

    has_exchange_box = False

    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        if (x > 30 and x < 60) and (w > 915 and w < 960):
            has_exchange_box = True
        if (not isBoxAFooterConceptKey(x, y, w, h)) and (
            not isBoxAFooterConceptValue(x, y, w, h)
        ):
            cv2.rectangle(image, (x, y), (x + w, y + h), (255, 255, 255), -1)

    cv2.imwrite("images/temp/footer_box_1_wol.png", image)

    # Si es A USD
    if has_exchange_box:
        image = cv2.imread("images/temp/footer_box_1_wol.png")
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (7, 7), 0)
        thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        kernal = cv2.getStructuringElement(cv2.MORPH_RECT, (200, 10))
        dilate = cv2.dilate(thresh, kernal, iterations=1)
        cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]
        cnts = sorted(cnts, key=lambda x: cv2.boundingRect(x)[1])

        for c in cnts:
            x, y, w, h = cv2.boundingRect(c)
            if w == image.shape[1]:
                new_img = image[y : y + h, x : x + w]
                cv2.imwrite("images/temp/footer_box_2_wol.png", new_img)
                cv2.rectangle(image, (x, y), (x + w, y + h), (255, 255, 255), -1)
                cv2.imwrite("images/temp/footer_box_1_wol.png", image)

    if os.path.isfile("images/temp/footer_box_2_wol.png"):
        image = cv2.imread("images/temp/footer_box_2_wol.png")
        ocr_result = pytesseract.image_to_string(image, lang="spa", config="--psm 6")
        ocr_result = ocr_result[
            ocr_result.find("consignado de")
            + len("consignado de") : ocr_result.find("asciende")
            - 1 :
        ].strip()
        exchange_rate = ocr_result
    else:
        exchange_rate = "1"

    # Separa por un lado las claves y por otro los valores del pie de la factura
    processImage(
        imageToProcessPath="images/temp/footer_box_1_wol.png",
        rectDimensions=(10, 200),
        boxWidthTresh=1,
        boxHeightTresh=1,
        folder="images/processing",
        outputImagePrefix="footer_key_value",
    )

    # Divide por partes las claves, de aquí usamos cualquiera (la primera) para obtener la moneda en que se operó en la factura
    processImage(
        imageToProcessPath="images/processing/footer_key_value_2.png",
        rectDimensions=(200, 1),
        boxWidthTresh=1,
        boxHeightTresh=1,
        folder="images/processing",
        outputImagePrefix="footer_key",
    )

    # Divide por partes los valores
    processImage(
        imageToProcessPath="images/processing/footer_key_value_1.png",
        rectDimensions=(10, 5),
        boxWidthTresh=1,
        boxHeightTresh=1,
        folder="images/processing",
        outputImagePrefix="footer_value",
    )

    # Creo pie tipo RI o mono
    if invoice_type == InvoiceType.A:
        values = 0

        for file in os.listdir("images/processing/"):
            filename = os.fsdecode(file)
            if filename.startswith("footer_value_"):
                values = values + 1

        if values == 10:
            starting_value = 1
        else:
            starting_value = 0

        footer = AFooter(
            net_amount_untaxed=getFooterConcept(
                img_file="images/processing/footer_value_"
                + str(starting_value)
                + ".png"
            ),
            net_amount_taxed=getFooterConcept(
                img_file="images/processing/footer_value_"
                + str(starting_value + 1)
                + ".png"
            ),
            vat_27=getFooterConcept(
                img_file="images/processing/footer_value_"
                + str(starting_value + 2)
                + ".png"
            ),
            vat_21=getFooterConcept(
                img_file="images/processing/footer_value_"
                + str(starting_value + 3)
                + ".png"
            ),
            vat_10_5=getFooterConcept(
                img_file="images/processing/footer_value_"
                + str(starting_value + 4)
                + ".png"
            ),
            vat_5=getFooterConcept(
                img_file="images/processing/footer_value_"
                + str(starting_value + 5)
                + ".png"
            ),
            vat_2_5=getFooterConcept(
                img_file="images/processing/footer_value_"
                + str(starting_value + 6)
                + ".png"
            ),
            vat_0=getFooterConcept(
                img_file="images/processing/footer_value_"
                + str(starting_value + 7)
                + ".png"
            ),
            other_taxes_ammout=getFooterConcept(
                img_file="images/processing/footer_value_"
                + str(starting_value + 8)
                + ".png"
            ),
            total=getFooterConcept(
                img_file="images/processing/footer_value_"
                + str(starting_value + 9)
                + ".png"
            ),
            currency=getFooterCurrency("images/processing/footer_key_1.png"),
            exchange_rate=exchange_rate,
        )
    else:
        footer = CFooter(
            sub_total=getFooterConcept(img_file="images/processing/footer_value_1.png"),
            other_taxes_ammout=getFooterConcept(
                img_file="images/processing/footer_value_2.png"
            ),
            total=getFooterConcept(img_file="images/processing/footer_value_3.png"),
            currency=getFooterCurrency("images/processing/footer_key_1.png"),
            exchange_rate=exchange_rate,
        )
    return footer


def isBoxAFooterConceptKey(x, y, w, h):
    return ((x > 610 and x < 760) or (x > 30 and x < 60)) and (
        (w > 200 and w < 270) or (w > 915 and w < 960)
    )


def isBoxAFooterConceptValue(x, y, w, h):
    return x > 900 and (w > 70 and w < 150)
