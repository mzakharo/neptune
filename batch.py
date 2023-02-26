from glob import glob
import cv2
from analyze import ocr
import multiprocessing
import sys

folder = sys.argv[1]
files = glob(f'{folder}/*.png')

def test(img_file):
    img = cv2.imread(img_file)
    result, img = ocr(img)
    ret = True
    if len(result) == 9 and result.startswith('00240'):
        try:
            result = int(result)
            ret = False
        except:
            pass
    print(ret, result, img_file)
    return ret

if __name__ == '__main__':
    #for img_file in sorted(files):
    #    test(img_file)
    with multiprocessing.Pool(4) as pool:
        vals = pool.map(test, files)
        print(sum(vals))

