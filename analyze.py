import cv2
import numpy as np
import os
import imutils
import datetime
from scipy import ndimage
import tempfile
import subprocess
import sys


def analyze(img, show=False):
    # Optimizing the image

    #img = imutils.resize(img, height=500)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #img = cv2.Canny(img, 100, 200)
    #img = cv2.threshold(img, 110, 255, cv2.THRESH_TOZERO)[1]
    #img = cv2.bilateralFilter(img, 17, 11, 11)
    img = cv2.bilateralFilter(img, 11, 17, 17) #orig
    #img = cv2.medianBlur(img, 3)
    img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 31, 15)
    img = cv2.medianBlur(img, 3)
    #img = cv2.Canny(img,1,35)
    #img = cv2.GaussianBlur(img, (1,1), 0)
    #img = cv2.GaussianBlur(img, (5,5), 0)

    #blur   = cv2.GaussianBlur(img, (5,5), 0)
    img = ndimage.rotate(img, 1)
    img = img[150:225, 35:370]
    #img = img[130:183, 42:277]

    #rotation angle in degree

    if show:
        cv2.imshow('image', img)
        cv2.waitKey(0)
    return img


def ocr(img, show=False, debug=False):
    #print('orig.png')
    #cv2.imwrite('orig.png', img)
    img = analyze(img, show=False)
    try:
        with tempfile.NamedTemporaryFile(suffix='.png') as tmp:
            fname = tmp.name
            #fname = 'rec.png'
            #print(fname)
            cv2.imwrite(fname, img)
            try:
                result = subprocess.check_output(
                        ['./ssocr',  '-d',  '-1',  '-i', '1', '-a', '-n', '3','-G', fname])
            except Exception as e:
                print(e)
                return f"undecoded-{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}", img
            result = result.decode().strip()
            if debug:
                print('result', result)
            result = result.replace('.', '')
            return result, img
    finally:
        if show:
            cv2.imshow('image', img)
            cv2.waitKey(0)





if __name__ == '__main__':
    img_file = sys.argv[1]
    print('img_file', img_file)
    img = cv2.imread(img_file)
    result, img = ocr(img, show=True, debug=True)
    print(result)
    #img = analyze(img, show=True)
    cv2.imwrite('proc.png', img)
