import cv2

def checkIfImageIsGray(
    imageToProcess
):
    
    # Poner en escala de grises la imágen, nada mas, si es que no viene ya lista
    if len(imageToProcess.shape) < 3:
        gray = imageToProcess
    else:
        gray = cv2.cvtColor(imageToProcess, cv2.COLOR_BGR2GRAY)
        
    return gray