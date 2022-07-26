
import os
import sys
import cv2
import numpy as np
from numpy.core.numeric import outer
import yaml
from progress.bar import Bar

def read_calibration_yaml(file):
    with open(file, 'r') as stream:
        try:
            calib = yaml.safe_load(stream)
            #print(calib)
            return {
                'camera_matrix': np.array(calib["camera_matrix"]['data']).reshape(3,3),
                'distortion_coefficients': np.array(calib['distortion_coefficients']['data'])
            }
        except yaml.YAMLError as exc:
            print(exc)
            return null

def rectify_image(calib, filein, fileout):
    img = cv2.imread(filein)
    undist = cv2.undistort(img, calib["camera_matrix"], calib["distortion_coefficients"])
    cv2.imwrite(fileout, undist)

def color_infrared_image(filein, fileout):
    im_gray = cv2.imread(filein, cv2.IMREAD_GRAYSCALE)
    im_color = cv2.applyColorMap(im_gray, cv2.COLORMAP_JET)
    cv2.imwrite(fileout, im_color)


def rectify_folder(calib_file, in_folder, out_folder):
    print('recitify folder: ', calib_file, in_folder, out_folder)
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)
    
    #print(calib_file, in_folder, out_folder)
    calib = read_calibration_yaml(calib_file)

    files = os.listdir(in_folder)
    files.sort()
    with Bar('Processing', max=len(files)) as bar:
        for f in files:
            if os.path.isfile( os.path.join(in_folder, f)):
                rectify_image(calib, os.path.join(in_folder, f), os.path.join(out_folder, f))
            else:
                print("ignore", os.path.join(in_folder, f))
            bar.next()

def color_folder(in_folder, out_folder):
    print('color folder: ', in_folder, out_folder)
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)
    
    files = os.listdir(in_folder)
    files.sort()
    with Bar('Processing', max=len(files)) as bar:
        for f in files:
            if os.path.isfile( os.path.join(in_folder, f)):
                color_infrared_image(os.path.join(in_folder, f), os.path.join(out_folder, f))
            else:
                print("ignore", os.path.join(in_folder, f))
            bar.next()


if __name__=="__main__":
    if len(sys.argv) != 4:
        print("rectify.py yaml in out")
    
    _, calib_file, in_folder, out_folder = sys.argv
    rectify_folder(calib_file, in_folder, out_folder)

    
