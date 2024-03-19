import cv2
from lib.functions.invoice_related.get_header_concept import getHeaderConcept
from lib.functions.invoice_related.get_header_concept_inproved import getHeaderConceptImproved
from lib.functions.invoice_related.get_vat_condition import getVatCondition

from lib.functions.utils.process_image import processImage
from lib.models.invoice_header import InvoiceHeader


def getHeader():
    image = cv2.imread("images/temp/header_box_2_wol.png")
    processImage(
        imageToProcess=image,
        rectDimensions=(200, 9),
        boxWidthTresh=1,
        boxHeightTresh=1,
        folder="images/processing",
        outputImagePrefix="header_concept_2",
    )

    image = cv2.imread("images/temp/header_box_1_wol.png")
    processImage(
        imageToProcess=image,
        rectDimensions=(25, 1),
        boxWidthTresh=1,
        boxHeightTresh=1,
        folder="images/processing",
        outputImagePrefix="header_concept_1",
    )

    image = cv2.imread("images/temp/header_box_4_wol.png")
    processImage(
        imageToProcess=image,
        rectDimensions=(50, 5),
        boxWidthTresh=1,
        boxHeightTresh=1,
        folder="images/processing",
        outputImagePrefix="header_concept_4",
    )

    header = InvoiceHeader(
        business_name=getHeaderConcept(img_file="images/processing/header_concept_2_1.png"),
        business_address=getHeaderConcept(img_file="images/processing/header_concept_2_2.png"),
        vat_condition=getVatCondition(
            getHeaderConcept(img_file="images/processing/header_concept_2_3.png")
        ),
        document_type=getHeaderConcept(img_file="images/processing/header_concept_1_1.png"),
        document_number=getHeaderConcept(img_file="images/processing/header_concept_1_2.png"),
        checkout_aisle_number=getHeaderConcept(
            img_file="images/processing/header_concept_1_3.png"
        ),
        issue_date=getHeaderConcept(img_file="images/processing/header_concept_1_4.png"),
        seller_cuit=getHeaderConcept(img_file="images/processing/header_concept_1_5.png"),
        gross_income=getHeaderConcept(img_file="images/processing/header_concept_1_6.png"),
        business_opening_date=getHeaderConcept(
            img_file="images/processing/header_concept_1_7.png"
        ),
        client_cuit=getHeaderConceptImproved(
            file_name_prefix="header_concept_4", key_to_match="CUIT"
        ),
        client_name=getHeaderConceptImproved(
            file_name_prefix="header_concept_4",
            key_to_match="Apellido y Nombre / Razón Social",
        ),
        client_address=getHeaderConceptImproved(
            file_name_prefix="header_concept_4", key_to_match="Domicilio Comercial"
        ),
        client_vat_condition=getVatCondition(
            getHeaderConceptImproved(
                file_name_prefix="header_concept_4",
                key_to_match="Condición frente al IVA",
            )
        ),
        sale_method=getHeaderConceptImproved(
            file_name_prefix="header_concept_4", key_to_match="Condición de venta"
        ),
    )

    return header