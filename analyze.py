import cv2
import numpy as np
import os
import math
#import imutils
import datetime
#from scipy import ndimage
import tempfile
import subprocess
import sys
import shlex

def calculate_rotation_angle(circle1, circle2):
    """
    Calculate the rotation angle needed to align two circles horizontally.
    
    Args:
        circle1, circle2: Tuples of (x, y, radius) for each circle
    
    Returns:
        angle: Rotation angle in degrees to make the line between circles horizontal
    """
    x1, y1 = circle1[0], circle1[1]
    x2, y2 = circle2[0], circle2[1]
    
    # Handle edge case where circles are vertically aligned
    if abs(x2 - x1) < 1e-6:
        return 0.0  # No rotation needed if already vertical
    
    # Calculate slope and convert to angle
    slope = (y2 - y1) / (x2 - x1)
    angle_rad = math.atan(slope)
    angle_deg = math.degrees(angle_rad)
    
    # Return negative angle to rotate in opposite direction to make horizontal
    return -angle_deg

def find_circles(img):
    gray = img
    rows = gray.shape[0]
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, rows / 24,
                                param1=30, param2=20,
                                minRadius=10, maxRadius=14)
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        circles = sorted(list(circles), key=lambda x : x[0], reverse=True) #always pick the right-most circle
    return circles

def find_circles_enhanced(img):
    """
    Enhanced circle detection that ensures we get exactly 2 circles for alignment.
    Filters out circles below the last circle's y-coordinate.
    
    Returns:
        circles: List of circles or None if not exactly 2 circles found
    """
    circles = find_circles(img)
    
    if circles is None or len(circles) < 2:
        return None
    
    cutoff = circles[0][1]

    # Filter out any circles below the last circle's y-coordinate
    filtered_circles = [circle for circle in circles if circle[1] <= cutoff]
    
    if len(filtered_circles) < 2:
        return None
    
    # Take only the first 2 circles (already sorted by x-coordinate)
    return filtered_circles[:2]

def simplify(circles, img):
    angle = 5.9
    row,col = img.shape[0:2]
    center=list(np.array([row,col])/2)
    rot_mat = cv2.getRotationMatrix2D(center,angle,1.0)
    new_image = cv2.warpAffine(img, rot_mat, (col,row))
    #new_image = img
    x0 = circles[0][0] - 590
    y0 = circles[0][1] - 25
    x1 = x0 + 460
    y1 = y0 + 85
    
    img2 = new_image[y0:y1,x0:x1]
    img2 = cv2.GaussianBlur(img2, (5,5), 0) 
    img2 = cv2.adaptiveThreshold(img2, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 21, 5)
    return img2

def simplify_dynamic(circles, img, debug=False):
    """
    Dynamic version of simplify that calculates rotation angle based on circle positions.
    
    Args:
        circles: List of detected circles
        img: Input grayscale image
        debug: Print debug information
    
    Returns:
        Processed image ready for OCR
    """
    # Use dynamic angle calculation if we have at least 2 circles
    angle = 22
    if len(circles) >= 2:
        angle  += calculate_rotation_angle(circles[0], circles[1])
        if debug:
            print(f"Calculated rotation angle: {angle:.2f} degrees")
    else:
        print(f"Using fallback angle: {angle} degrees (only {len(circles)} circles found)")
    
    row, col = img.shape[0:2]
    center = list(np.array([row, col]) / 2)
    rot_mat = cv2.getRotationMatrix2D(center, angle, 1.0)
    new_image = cv2.warpAffine(img, rot_mat, (col, row))
    
    # Use the first circle for cropping coordinates
    x0 = circles[0][0] - 560
    y0 = circles[0][1] + 55
    x1 = x0 + 460
    y1 = y0 + 80
    
    img2 = new_image[y0:y1, x0:x1]
    img2 = cv2.GaussianBlur(img2, (5, 5), 0)
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
    circles = find_circles_enhanced(img)
    if circles is None:
        return (True, 'ref_error', img)
    
    # Use dynamic rotation if we have at least 2 circles, otherwise fallback to original
    if len(circles) >= 2:
        print(f"Found {len(circles)} circles, using dynamic rotation")
        for i, (x, y, r) in enumerate(circles[:2]):
            print(f"Circle {i+1}: center=({x}, {y}), radius={r}")
        img = simplify_dynamic(circles, img, debug)
    else:
        print(f"Only found {len(circles)} circles, using original rotation")
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
