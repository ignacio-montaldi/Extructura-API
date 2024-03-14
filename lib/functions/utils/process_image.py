import cv2

from lib.functions.utils.save_cropped_images import saveCroppedImages

def processImage(
    imageToProcess,
    rectDimensions,
    boxWidthTresh,
    boxHeightTresh,
    outputImagePrefix,
    folder,
    outPutImageSufix="",
    imageWoLines=None,
    startingIndex=1,
    higherThanHeight=True,
    reverseSorting=False,
    savePreprocessingImages=False,
    isImageGray=False,
):
    # Poner en escala de grises la imágen, nada mas, si es que no viene ya lista
    if not (isImageGray):
        gray = cv2.cvtColor(imageToProcess, cv2.COLOR_BGR2GRAY)
    else:
        gray = imageToProcess

    # Difuminar la imágen, permite agrupar objetos (es decir, hacer menos legible su separacion) en la imágen para el siguiente paso Kernel positivo e impar
    blur = cv2.GaussianBlur(gray, (7, 7), 0)

    # Pone en blanco o negro según si el color del pixel se parece mas a uno u otro
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # En base a las dimensiones de un rectángulo estira los pixeles blancos, para así agrupar objetos
    kernal = cv2.getStructuringElement(cv2.MORPH_RECT, rectDimensions)
    dilate = cv2.dilate(thresh, kernal, iterations=1)

    # Para demostración, se ve paso a paso lo explicado arriba, se puede borrar después
    if savePreprocessingImages:
        cv2.imwrite("pretemp/invoice_gray.png", gray)
        cv2.imwrite("pretemp/invoice_blur.png", blur)
        cv2.imwrite("pretemp/invoice_thresh.png", thresh)
        cv2.imwrite("pretemp/invoice_dialate.png", dilate)

    saveCroppedImages(
        originalImage=imageToProcess,
        imageWoLines=imageWoLines,
        proprocessedImage=dilate,
        startingIndex=startingIndex,
        boxWidthTresh=boxWidthTresh,
        boxHeightTresh=boxHeightTresh,
        outputImagePrefix=outputImagePrefix,
        outPutImageSufix=outPutImageSufix,
        higherThanHeight=higherThanHeight,
        folder=folder,
        reverseSorting=reverseSorting,
    )
