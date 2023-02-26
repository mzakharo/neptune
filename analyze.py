import cv2
import numpy as np
import os
import imutils
import datetime
from scipy import ndimage
import tempfile
import subprocess
import sys
import shlex


def analyze(img, show=False):
    # Optimizing the image

    #img = imutils.resize(img, height=500)

    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    #img = cv2.Canny(img, 100, 200)
    #img = cv2.threshold(img, 110, 255, cv2.THRESH_TOZERO)[1]

    img = cv2.bilateralFilter(img, 27, 24 , 24)
    img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 55, 21)
    #img = cv2.medianBlur(img, 3)

    #kernel = np.ones((2, 2), np.uint8)
    #img = cv2.erode(img, kernel, iterations=1)
    #img = cv2.Canny(img,1,35)
    #img = cv2.GaussianBlur(img, (1,1), 0)

    img = ndimage.rotate(img, 0.35)
    img = img[156:216, 35:375]

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
                _debug = '-Dfoo.png' if debug else ''
                cmd = f'./ssocr -d -1 -i 0 -n 2 {_debug} {fname}'
                result = subprocess.check_output(shlex.split(cmd))
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
