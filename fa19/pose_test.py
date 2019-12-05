from swatbotics.python import apriltag as sb
import cv2
import os
import glob

# detector options for tag36h11 family
options = sb.DetectorOptions(families='tag36h11',
                             border=1,
                             nthreads=4,
                             quad_decimate=1.0,
                             quad_blur=0.0,
                             refine_edges=True,
                             refine_decode=False,
                             refine_pose=False,
                             debug=False,
                             quad_contours=True)

detector = sb.Detector(options)

"""
returns a list of all the files in directory [path] with .png or .jpg extension
assumes: [path] is a string of an absolute path
"""


def getImgsFromDir(path):
    files = []
    for ext in ('*.png', '*.jpg'):
        files.extend(glob.glob(os.path.join(path, ext)))

    return files


"""
captures frames from video of device with device index [device_index] (0 by default)
when space bar is pressed. Saves captured frames to working directory under name
[prefix] + frame count. Press 'q' to stop the stream.

assumes [prefix] is a string
"""


def frames_from_video(prefix, device_index=0):
    video = cv2.VideoCapture(device_index)
    count = 0
    while True:
        check, frame = video.read()
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cv2.imshow('stream', img)

        key = cv2.waitKey(1)
        if key == 32:
            cv2.imwrite(prefix + str(count) + '.jpg', img)
            count += 1

        elif key == ord('q'):
            break


"""
calculates pose from image [image] and prints results from terminal.
assumes: [image] is an image loaded from cv2.imread() or captured from cv2
VideoCapture object. [params] is a tuple of intrinsic camera parameters which
can be calculated from calibrate_camera.py. [tag_size] is the size of the apriltag
in user defined units, used to scale the results (1.0 by default).
"""


def calculate_pose(image, params, tag_size=1.0):
    try:
        detections = detector.detect(image)
        for i, detection in enumerate(detections):
            pose, init_err, final_err = detector.detection_pose(
                detection, params, tag_size)
            coords = [row[3] for row in pose[:-1]]
            print('detection {}'.format(i+1))
            print()
            print('x = {}'.format(coords[0]))
            print('y = {}'.format(coords[1]))
            print('z = {}'.format(coords[2]))
            print()
            print('initial error: {}'.format(init_err))
            print('final error: {}'.format(final_err))
            print()

    except Exception as e:
        # print(e)
        pass


"""
Calculates pose for images in [images] and prints results to terminal, if an image
in [images] doesn't contain an april tag then prints nothing to terminal for that
image.
Assumes: [images] is a list of .png or .jpg files, [params] is a tuple of
intrinsic camera parameters which can be calculated from calibrate_camera.py,
and [tag_size] is the size of the apriltag in user defined units,
used to scale the results (1.0 by default)
"""


def pose_from_imgs(images, params, tag_size=1.0):
    for image in images:
        img = cv2.imread(image)
        calculate_pose(img, params, tag_size)


"""
Calculates pose estimation of all apriltags in frame and prints results to the terminal.
[params] is a tuple of intrinsic camera parameters which can be calculated from
calibrate_camera.py. [tag_size] is the size of the apriltag in user defined units,
used to scale the results (1.0 by default).
[device_index] is the device index of the camera being used
for apriltag detection, is 0 (webcam) by default.

assumes: [tag_size] > 0 and using tag36h11 tag family
Note: press q to stop the video stream
"""


def main(params, tag_size=1.0, device_index=0):
    video = cv2.VideoCapture(device_index)

    while True:
        check, frame = video.read()
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cv2.imshow('test', img)
        calculate_pose(img, params, tag_size)

        key = cv2.waitKey(1)
        if key == ord('q'):
            break

    video.release()
    cv2.destroyAllWindows()


# TODO stopping condition
if __name__ == '__main__':
    main((1059.96973328701, 1069.2489339794608,
          622.030969436662, 362.4945777620182), 6.25)
