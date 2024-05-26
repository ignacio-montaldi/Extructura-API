import cv2
from lib.enums.image_type_enum import Image_type
from lib.functions.invoice_related.get_header_concept import getHeaderConcept
from lib.functions.invoice_related.get_header_concept_inproved import getHeaderConceptImproved
from lib.functions.invoice_related.get_vat_condition import getVatCondition

from lib.functions.utils.process_image import processImage
from lib.models.invoice_header import InvoiceHeader


def getHeader(invoiceFileName, image_type):
    folder_dir = "images/processing"
    
    processImage(
        imageToProcessPath="images/temp/header_box_2_wol.png",
        rectDimensions=(200, 9 if image_type == Image_type.pdf else 8),
        boxWidthTresh=1,
        boxHeightTresh=1,
        folder=folder_dir,
        outputImagePrefix="header_concept_2"
    )

    processImage(
        imageToProcessPath="images/temp/header_box_1_wol.png",
        rectDimensions=(25, 1),
        boxWidthTresh=1,
        boxHeightTresh=1,
        folder=folder_dir,
        outputImagePrefix="header_concept_1",
    )
    
    image = cv2.imread("images/temp/header_box_4_wol.png", 0)
    h, w = image.shape
    #For test
    f = open("test2.txt", "a")
    f.write('(\''+str(invoiceFileName)+"\',"+str(h)+','+str(w)+")\n")
    f.close()
    #######
    
    
    limit1= round(h/3)-3
    limit2= round(2*h/3)-7
    
    fileName = ("images/temp/header_box_4_1_wol.png")
    cv2.imwrite(fileName, image[0 : limit1, 0 : w])
    
    fileName = ("images/temp/header_box_4_2_wol.png")
    cv2.imwrite(fileName, image[limit1 : limit2, 0 : w])
    
    fileName = ("images/temp/header_box_4_3_wol.png")
    cv2.imwrite(fileName, image[limit2 : h, 0 : w])
    
    subdivided_folder_dir = folder_dir+"/header_concepts/header_concepts_subdivided"

    processImage(
        imageToProcessPath="images/temp/header_box_4_1_wol.png",
        rectDimensions=(50, 200),
        boxWidthTresh=3,
        boxHeightTresh=3,
        folder=subdivided_folder_dir,
        outputImagePrefix="header_concept_4_1"
    )
    
    processImage(
        imageToProcessPath="images/temp/header_box_4_2_wol.png",
        rectDimensions=(50, 200),
        boxWidthTresh=3,
        boxHeightTresh=3,
        folder=subdivided_folder_dir,
        outputImagePrefix="header_concept_4_2",
    )
    
    processImage(
        imageToProcessPath="images/temp/header_box_4_3_wol.png",
        rectDimensions=(50, 200),
        boxWidthTresh=3,
        boxHeightTresh=3,
        folder=subdivided_folder_dir,
        outputImagePrefix="header_concept_4_3",
    )

    header = InvoiceHeader(
        business_name=getHeaderConcept(img_file=folder_dir+"/header_concept_2_1.png"),
        business_address=getHeaderConcept(img_file=folder_dir+"/header_concept_2_2.png"),
        vat_condition=getVatCondition(
            getHeaderConcept(img_file=folder_dir+"/header_concept_2_3.png")
        ),
        document_type=getHeaderConcept(img_file=folder_dir+"/header_concept_1_1.png"),
        document_number=getHeaderConcept(img_file=folder_dir+"/header_concept_1_2.png"),
        checkout_aisle_number=getHeaderConcept(
            img_file=folder_dir+"/header_concept_1_3.png"
        ),
        issue_date=getHeaderConcept(img_file=folder_dir+"/header_concept_1_4.png"),
        seller_cuit=getHeaderConcept(img_file=folder_dir+"/header_concept_1_5.png"),
        gross_income=getHeaderConcept(img_file=folder_dir+"/header_concept_1_6.png"),
        business_opening_date=getHeaderConcept(
            img_file=folder_dir+"/header_concept_1_7.png"
        ),
        
        client_cuit=getHeaderConcept(
            img_file=subdivided_folder_dir+"/header_concept_4_1_2.png"
        ),
        client_name=getHeaderConcept(
            img_file=subdivided_folder_dir+"/header_concept_4_1_1.png"
        ),
        client_address=getHeaderConcept(
            img_file=subdivided_folder_dir+"/header_concept_4_2_1.png"
        ),
        client_vat_condition=getVatCondition(getHeaderConcept(
            img_file=subdivided_folder_dir+"/header_concept_4_2_2.png"),
        ),
        sale_method=getHeaderConceptImproved(
            file_name_prefix="header_concept_4_3", key_to_match="Condición de venta", directory_in_str=subdivided_folder_dir, invoiceFileName= None
        ),
        
    )

    return header