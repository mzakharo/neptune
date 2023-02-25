import cv2
import numpy as np
import os
#import imutils
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
    img = cv2.bilateralFilter(img, 17, 31, 31)
    #img = cv2.medianBlur(img, 3)
    img = cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY,31, 11)
    img = cv2.medianBlur(img, 3)
    #img = cv2.GaussianBlur(img, (1,1), 0)
    #img = cv2.GaussianBlur(img, (5,5), 0)

    #blur   = cv2.GaussianBlur(img, (5,5), 0)
    #img = cv2.Canny(blur,1,35)
    img = ndimage.rotate(img, -1.5)
    img = img[175:255, 43:389]

    #rotation angle in degree

    if show:
        cv2.imshow('image', img)
        cv2.waitKey(0)
    return img


def ocr(img, show=False):
    #print('orig.png')
    #cv2.imwrite('orig.png', img)
    img = analyze(img, show=show)
    with tempfile.NamedTemporaryFile(suffix='.png') as tmp:
        fname = tmp.name
        #fname = 'rec.png'
        #print(fname)
        cv2.imwrite(fname, img)
        try:
            result = subprocess.check_output(['./ssocr',  '-d',  '-1',  '-i', '2', fname])
        except Exception as e:
            print(e)
            return f"undecoded-{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}", img
        result = result.decode().strip()
        result = result.replace('.', '')
        return result, img



if __name__ == '__main__':
    img_file = 'data/002e103124.jpg'
    img_file = sys.argv[1]
    print('img_file', img_file)
    img = cv2.imread(img_file)
    result, img = ocr(img, show=True)
    print(result)
    #img = analyze(img, show=True)
    cv2.imwrite('proc.png', img)
