from glob import glob
import cv2
from analyze import ocr, parse
import multiprocessing
import sys

folder = sys.argv[1]
files = glob(f'{folder}/*.png')

def test(img_file):
    img = cv2.imread(img_file)
    ocr_err, result, img = ocr(img)
    parse_err, _ = parse(result)
    err = ocr_err or parse_err
    print(err, result, img_file)
    return err, result, img_file

if __name__ == '__main__':
    #vals = [test(img_file) for img_file in sorted(files)]
    with multiprocessing.Pool(4) as pool:
        vals = pool.map(test, files)
    vals = sorted(vals, key=lambda x: x[1])
    [print(v) for v in vals]
    print(sum([v[0] for v in vals]))

