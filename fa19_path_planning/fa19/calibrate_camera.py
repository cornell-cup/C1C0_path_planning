import numpy as np
import cv2
import argparse
import os
import glob

"""
returns [file_path] if string [file_path] is a directory
else raises NotADirectoryError
"""
def dir_path(file_path):
    if os.path.isdir(file_path):
        return file_path
    else:
        raise NotADirectoryError(file_path)


"""
Calculates intrinsic camera parameters of camera and prints results to terminal.
Requires command line arguments [--path], [--rows / -r], [--cols / -c]

[--path]: directory containing pictures of a black and white checkerboard.
Files should be in jpg or png format. It typically takes at least 10 pictures
taken in different orientations to get a good estimate of intrinsic camera parameters

[--rows / -r]: The number of rows of the checkerboard - 1

[--cols / -c]: The number of columns of the checkerboard - 1
"""
def main():
    parser = argparse.ArgumentParser(
        description='calibrate camera intrinsics using OpenCV')

    parser.add_argument('--path', type=dir_path,
                        required=True,
                        help='input image files')

    parser.add_argument('-r', '--rows', metavar='N', type=int,
                        required=True,
                        help='# of chessboard corners in vertical direction')

    parser.add_argument('-c', '--cols', metavar='N', type=int,
                        required=True,
                        help='# of chessboard corners in horizontal direction')

    options = parser.parse_args()

    files = []
    for ext in ('*.png', '*.jpg'):
        files.extend(glob.glob(os.path.join(options.path, ext)))

    rows = options.rows
    cols = options.cols

    # termination criteria
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
    objp = np.zeros((rows * cols, 3), np.float32)
    objp[:, :2] = np.mgrid[0:cols, 0:rows].T.reshape(-1, 2)

    # Arrays to store object points and image points from all the images.
    objpoints = []  # 3d point in real world space
    imgpoints = []  # 2d points in image plane.

    for file in files:
        img = cv2.imread(file)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        ret, corners = cv2.findChessboardCorners(gray, (cols, rows), None)

        if ret:
            objpoints.append(objp)

            corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
            imgpoints.append(corners2)

    retval, K, dcoeffs, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

    fx = K[0, 0]
    fy = K[1, 1]
    cx = K[0, 2]
    cy = K[1, 2]

    params = (fx, fy, cx, cy)

    print()
    print('all units below measured in pixels:')
    print('  fx = {}'.format(K[0, 0]))
    print('  fy = {}'.format(K[1, 1]))
    print('  cx = {}'.format(K[0, 2]))
    print('  cy = {}'.format(K[1, 2]))

    print(params)

"""
driver
"""
if __name__ == '__main__':
    main()
