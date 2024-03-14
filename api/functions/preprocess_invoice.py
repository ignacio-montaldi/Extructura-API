import cv2

from lib.enums.image_type_enum import Image_type

from lib.functions.add_borders import addBorders
from lib.functions.are_header_boxes_inverted import areHeaderMainBoxesInverted
from lib.functions.create_images_from_boxes import createImagesFromImageBoxes
from lib.functions.crop_top_right_header_box import cropHeaderBox2
from lib.functions.edge_cleaning import edgeCleaning
from lib.functions.image_cleaning import imageCleaning
from lib.functions.invert_two_file_names import invertTwoFileNames
from lib.functions.preprocess_image import preprocess_image
from lib.functions.process_image import processImage
from lib.functions.reduce_to_biggest_by_area import reduceToBiggestByArea
from lib.functions.remove_lines_from_image import removeLinesFromImage

def preprocessInvoice(image_type):
    starting_image_path = "data/factura.png"
    image = cv2.imread(starting_image_path)

    # Preprocesamos la imágen según el tipo de imágen
    match image_type:
        case Image_type.pdf:
            image = imageCleaning(image)
        case Image_type.photo:
            image = preprocess_image(image)
            image = edgeCleaning(
                image=image, path="data/page_preprocessed.png", paddingToPaint=10, all=True
            )
        case Image_type.scan:
            image = addBorders(image, size=30, color=[125, 0, 255])
            cv2.imwrite("data/page_preprocessed.png", image)
            image = preprocess_image(image)
            image = edgeCleaning(
                image=image, path="data/page_preprocessed.png", paddingToPaint=10, all=True
            )
            
            from wand.image import Image
            from wand.display import display

            with Image(filename="data/page_preprocessed.png") as img:
                img.deskew(0.4 * img.quantum_range)
                img.save(filename="data/page_preprocessed.png")
            image = cv2.imread("data/page_preprocessed.png", 0)

        case _:
            print("Error")

    # Obtenemos duplicado sin líneas en el cuerpo de la factura
    invoiceWithoutLines = removeLinesFromImage(image)
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
        return height > 70 and height < 240 and width > 80 and height < 1130 and ratio > 0.1 and ratio < 1
       
    image = cv2.imread("pretemp/header_1.png", 0)
    imageWol = cv2.imread("pretemp/header_1_wol.png", 0)
    createImagesFromImageBoxes(
        imageToProcess=image,
        imageWoLines=imageWol,
        savePreprocessingImages=True,
        originalName="header",
        verticalDialationIterations= 9 if image_type == Image_type.scan else 3,horizontalDialationIterations= 9 if image_type == Image_type.scan else 3,
        check_function=check_valid_header_boxes,
    )

    # Chequeamos que el encabezado 1 y 2 están bien ubicados (problema viene de ver cual es primero por ser del mismo tamaño)
    header1 = cv2.imread("temp/header_box_1.png")
    header2 = cv2.imread("temp/header_box_2.png")
    if areHeaderMainBoxesInverted(header1=header1, header2=header2):
        invertTwoFileNames("temp/header_box_1.png", "temp/header_box_2.png")
        invertTwoFileNames("temp/header_box_1_wol.png", "temp/header_box_2_wol.png")

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