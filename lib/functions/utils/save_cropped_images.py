import cv2


def saveCroppedImages(
    originalImage,
    imageWoLines,
    proprocessedImage,
    startingIndex,
    boxWidthTresh,
    boxHeightTresh,
    outputImagePrefix,
    outPutImageSufix,
    higherThanHeight,
    folder,
    reverseSorting,
    printDimensions,
):
    # Encuentra los contornos
    cnts = cv2.findContours(
        proprocessedImage, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
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
            if printDimensions:
                print(h)
            if w > boxWidthTresh and h > boxHeightTresh:
                roi = originalImage[y : y + h, x : x + w]
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
                if imageWoLines is not None:
                    roi = imageWoLines[y : y + h, x : x + w]
                    fileName = (
                        folder
                        + "/"
                        + outputImagePrefix
                        + "_"
                        + str(index)
                        + "_wol"
                        + outPutImageSufix
                        + ".png"
                    )
                    cv2.imwrite(fileName, roi)
                index += 1
        else:
            if w > boxWidthTresh and h < boxHeightTresh:
                roi = originalImage[y : y + h, x : x + w]
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
                if imageWoLines is not None:
                    roi = imageWoLines[y : y + h, x : x + w]
                    fileName = (
                        folder
                        + "/"
                        + outputImagePrefix
                        + "_"
                        + str(index)
                        + "_wol"
                        + outPutImageSufix
                        + ".png"
                    )
                    cv2.imwrite(fileName, roi)
                index += 1
