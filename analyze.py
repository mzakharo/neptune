import cv2
import numpy as np
import os
#import imutils
import datetime
#from scipy import ndimage
import tempfile
import subprocess
import sys
import shlex

def analyze(img, show=False):
    debug = False

    #img = imutils.resize(img, height=500)

    if debug:
        output = img.copy()

    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    x0 = 33
    y0 = 311

    dynamic = False
    #dynamic = True
    if dynamic:
        import easyocr
        reader = easyocr.Reader(['en'])
        bounds = reader.readtext(img)
        for bound in bounds:
            if bound[1] == '(LPM)':
                x = bound[0][1][0]
                y = bound[0][1][1]
                x0 = x - 387 + 30
                y0 = y - 410 + 315
                print('coords', x0, y0)
                break


    
    # detect circles in the image -> This detects ® in the image.
    gray = img
    rows = gray.shape[0]
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, rows / 8,
                               param1=250, param2=25,
                               minRadius=9, maxRadius=13)


    # ensure at least some circles were found
    if circles is not None:
        # convert the (x, y) coordinates and radius of the circles to integers
        circles = np.round(circles[0, :]).astype("int")
        circles = sorted(list(circles), key=lambda x : x[0]) #always pick the right-most circle
        if debug:
            print('circles', circles)
        # loop over the (x, y) coordinates and radius of the circles
        for (x, y, r) in circles:
            x0 = x - 302 + 31
            y0 = y - 462 + 315

            # draw the circle in the output image, then draw a rectangle
            # corresponding to the center of the circle
            if debug:
                cv2.circle(output, (x, y), r, (0, 255, 0), 4)
                cv2.rectangle(output, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
        # show the output image

    if debug:
        cv2.imshow("output", output)
        cv2.waitKey(0)


    x1 = x0 + 410 - 70
    y1 = y0 + 220 - 160
    #img = cv2.GaussianBlur(img, (1,1), 0)

    #img = cv2.Canny(img, 350, 400)

    #img = ndimage.rotate(img, -0.8)
    img = img[y0:y1,x0:x1]

    #img = cv2.Canny(img, 100, 200)
    #img = cv2.threshold(img, 110, 255, cv2.THRESH_TOZERO)[1]

    #img = cv2.medianBlur(img, 3)
    #img = cv2.bilateralFilter(img, 11, 17 , 17)

    img = cv2.GaussianBlur(img, (9,9), 0)

    #kernel = np.ones((3, 3), np.uint8)
    #img = cv2.dilate(img, kernel, iterations=1) #get rid of noise
    #img = cv2.erode(img, kernel, iterations=1)  #get back original without the noise
 
    img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 71, 11)


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
                cmd = f'./ssocr -d -1 -i 1 -n 2 {_debug} {fname}'
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
