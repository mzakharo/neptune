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

    #img = cv2.medianBlur(img, 3)
    img = cv2.bilateralFilter(img, 11, 17 , 17)
    img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 53, 13)

    '''
    import easyocr
    reader = easyocr.Reader(['en'])
    bounds = reader.readtext(img)
    for bound in bounds:
        if bound[1] == 'LPM':
            print(bound[0][1])
            x = bound[0][1][0] #383
            y = bound[0][1][1] #244
            x1 = x + 7
            x0 = x1 - (390-50)
            y1 = y - 24
            y0 = y1 - (220-160)
            print(y0, y1, x0 , x1)
            break
    '''
    y0 = 160
    y1 = 220
    x0 = 70
    x1 = 410

    #kernel = np.ones((2, 2), np.uint8)
    #img = cv2.erode(img, kernel, iterations=1)
    #img = cv2.Canny(img,1,35)
    #img = cv2.GaussianBlur(img, (1,1), 0)

    img = ndimage.rotate(img, -0.8)
    img = img[y0:y1,x0:x1]

    if show:
        cv2.imshow('image', img)
        cv2.waitKey(0)
    return img

def parse(result):
    err = True
    if len(result) == 9:
        try:
            result = int(result)
            err = False
        except:
            pass
    return err, result


def ocr(img, show=False, debug=False):
    img = analyze(img, show=False)

    '''
    bounds = reader.readtext(img , allowlist ='0123456789')
    print(bounds)
    '''

    #'''
    if debug:
        import pytesseract as pyt
        os.environ['TESSDATA_PREFIX'] = 'tessdata'
        ocr_result = pyt.image_to_string(img,  lang='lets', config='--psm 7 -c tessedit_char_whitelist=.0123456789')
        print('letsg', ocr_result.strip().replace(' ', '').replace('.', ''))
    #ocr_result = pyt.image_to_string(img,  lang='letsgodigital', config='--psm 7 -c tessedit_char_whitelist=.0123456789')
    #print('digial', ocr_result)
    #'''

    try:
        with tempfile.NamedTemporaryFile(suffix='.png') as tmp:
            fname = tmp.name
            #fname = 'rec.png'
            #print(fname)
            cv2.imwrite(fname, img)
            err = False
            try:
                _debug = '-Dfoo.png' if debug else ''
                cmd = f'./ssocr -d -1 -i 0 -n 3 {_debug} {fname}'
                result = subprocess.check_output(shlex.split(cmd))
            except subprocess.CalledProcessError as exc:                                                                                                   
                err = True
                result = exc.output
            result = result.decode().strip()
            if debug:
                print('ssocr', result)
            result = result.replace('.', '')
            return err, result, img
    finally:
        if show:
            cv2.imshow('image', img)
            cv2.waitKey(0)





if __name__ == '__main__':
    img_file = sys.argv[1]
    print('img_file', img_file)
    img = cv2.imread(img_file)
    err, result, img = ocr(img, show=True, debug=True)
    print('err:', err,'result:', result)
    #img = analyze(img, show=True)
    cv2.imwrite('proc.png', img)
