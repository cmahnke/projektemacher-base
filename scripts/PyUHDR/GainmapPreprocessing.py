import cv2 as cv

class GainmapPreprocessing:
    def normalize(img):
        #cvAr = greyscale(pilImg)
        norm = cv.normalize(src=img, dst=None, beta=0, alpha=255, norm_type=cv.NORM_MINMAX)
        return norm

    def grayscale(img):
        return cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    def denoise(img):
        return cv.fastNlMeansDenoising(img)

    def smoothen(img):
        return cv.bilateralFilter(cvAr, 25, 75, 75)

    def white_balance(img, balancer="simple"):
        if balancer == "simple":
            wb = cv.xphoto.createSimpleWB()
        elif balencer == "grayworld":
            wb = cv.xphoto.createGrayworldWB()
        return wb.balanceWhite(img)

    def invert(img):
        return cv.bitwise_not(img)
