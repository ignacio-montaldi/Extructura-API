import cv2

from lib.enums.invoice_type_enum import InvoiceType
from lib.functions.utils.check_if_image_is_gray import checkIfImageIsGray
from lib.functions.utils.delete_file import delete_file

def processItemImage(
    imageToProcessPath: str,
    rectDimensions,
    boxWidthTresh,
    boxHeightTresh,
    outputImagePrefix,
    folder,
    outPutImageSufix="",
    reverseSorting=False,
    savePreprocessingImages=False,
    invoice_type=InvoiceType.C
):
    
    imageToProcess = cv2.imread(imageToProcessPath)
    
    # Poner en escala de grises la imágen, nada mas, si es que no viene ya lista
    gray = checkIfImageIsGray(imageToProcess)
            

    # Difuminar la imágen, permite agrupar objetos (es decir, hacer menos legible su separacion) en la imágen para el siguiente paso Kernel positivo e impar
    blur = cv2.GaussianBlur(gray, (7, 7), 0)

    # Pone en blanco o negro según si el color del pixel se parece mas a uno u otro
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # En base a las dimensiones de un rectángulo estira los pixeles blancos, para así agrupar objetos
    kernal = cv2.getStructuringElement(cv2.MORPH_RECT, rectDimensions)
    dilate = cv2.dilate(thresh, kernal, iterations=1)

    # Para demostración, se ve paso a paso lo explicado arriba, se puede borrar después
    if savePreprocessingImages:
        cv2.imwrite("images/pretemp/invoice_gray.png", gray)
        cv2.imwrite("images/pretemp/invoice_blur.png", blur)
        cv2.imwrite("images/pretemp/invoice_thresh.png", thresh)
        cv2.imwrite("images/pretemp/invoice_dialate.png", dilate)

        
    # Encuentra los contornos
    cnts = cv2.findContours(
        dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    # Ordena los contornos, más grandes primero
    cnts = sorted(cnts, key=lambda x: cv2.boundingRect(x)[1])

    index = 0
    if reverseSorting:
        cnts.reverse()

    # Guarda las imágenes recortadas según sus contornos, si sus ancho/alto son mayores o menores a unos valorores por parámetro
    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        print(x)
        if w > boxWidthTresh and h > boxHeightTresh:
            roi = gray[y : y + h, x : x + w]
            if invoice_type == InvoiceType.A:
                if x<=76: #Pixeles de Cod.
                    index = 1
                elif x > 76 and x<=477: #Pixeles de Producto
                    index = 2
                elif x > 477 and x<=539: #Pixeles de Cantidad
                    index = 3
                elif x > 539 and x<=649: #Pixeles de U. medida.
                    index = 4
                elif x > 649 and x<=758: #Pixeles de Precio Unit.
                    index = 5
                elif x > 758 and x<=837: #Pixeles de % Bonif.
                    index = 6
                elif x > 837 and x<=937: #Pixeles de subtotal.
                    index = 7
                elif x > 937 and x<=1036: #Pixeles de alicuota iva.
                    index = 8
                elif x > 1036: #Pixeles de subtotal c/iva.
                    index = 9         
                else:
                    raise("Error")
            else: 
                if x <= 71: #Pixeles de Cod.
                    index = 1
                elif x > 71 and x<=423: #Pixeles de Producto
                    index = 2
                elif x > 423 and x<=469: #Pixeles de Cantidad
                    index = 3
                elif x > 469 and x<=628: #Pixeles de U. medida.
                    index = 4
                elif x > 628 and x<=701: #Pixeles de Precio Unit.
                    index = 5
                elif x > 701 and x<=850: #Pixeles de % Bonif.
                    index = 6
                elif x > 850 and x<=999: #Pixeles de imp. bonif.
                    index = 7
                elif x > 999: #Pixeles de subtotal.
                    index = 8         
                else:
                    raise("Error")
            
            fileName = (
                folder
                + "/"
                + outputImagePrefix
                + "_"
                + str(index)
                + outPutImageSufix
                + ".png"
            )
            cv2.imwrite(fileName, roi)
            
    
        
