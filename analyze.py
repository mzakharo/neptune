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

def find_circles(img):
    gray = img
    rows = gray.shape[0]
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, rows / 8,
                                param1=50, param2=25,
                                minRadius=5, maxRadius=15)
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        circles = sorted(list(circles), key=lambda x : x[0], reverse=True) #always pick the right-most circle
    return circles

def simplify(circles, img):
    angle = 2.7
    row,col = img.shape[0:2]
    center=list(np.array([row,col])/2)
    rot_mat = cv2.getRotationMatrix2D(center,angle,1.0)
    new_image = cv2.warpAffine(img, rot_mat, (col,row))
    #new_image = img
    x0 = circles[0][0] - 580
    y0 = circles[0][1]
    x1 = x0 + 460
    y1 = y0 + 85
    
    img2 = new_image[y0:y1,x0:x1]
    img2 = cv2.GaussianBlur(img2, (5,5), 0) 
    img2 = cv2.adaptiveThreshold(img2, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 21, 5)
    return img2

def parse(result):
    err = True
    if len(result) == 9:
        try:
            result = int(result)
            err = True if result in[888888888, 88888888, 8888888] else False # when LCD is booting up
            err = True if result >= 100000000 else err  #when the screen switches to another mode
        except:
            pass
    return err, result


def ocr(img, show=False, debug=False):
    circles = find_circles(img)
    if circles is None:
        return (True, 'ref_error', img)
    img = simplify(circles, img)


    tmp = tempfile.NamedTemporaryFile(suffix='.png', delete=False)    
    fname = tmp.name
    fname = fname.replace('\\', '\\\\')
    tmp.close()    
    #fname = 'rec.png'
    try:        
        #print(fname)
        cv2.imwrite(fname, img)
        err = False
        try:
            _debug = '-Dfoo.png -P' if debug else ''
            cmd = f'./ssocr -d -1 -i 1 -n 2 {_debug} {fname}'
            result = subprocess.check_output(shlex.split(cmd))
        except subprocess.CalledProcessError as exc:                                                                                                   
            err = True
            result = b'ocr_error'
        result = result.decode().strip()
        if debug:
            print('ssocr', result)
        result = result.replace('.', '')
        if len(result) == 0:
            result = 'res_error'
        return err, result, img
    finally:
        os.remove(fname)
        if show:
            cv2.imshow('image', img)
            cv2.waitKey(0)





if __name__ == '__main__':
    img_file = sys.argv[1]
    print('img_file', img_file)
    img_orig = cv2.imread(img_file)
    img_orig = cv2.rotate(img_orig, cv2.ROTATE_180)
    img = cv2.cvtColor(img_orig, cv2.COLOR_BGR2GRAY)
    err, result, img = ocr(img, show=True, debug=True)
    print('err:', err,'result:', result)
    #img = analyze(img, show=True)
    cv2.imwrite('proc.png', img)
