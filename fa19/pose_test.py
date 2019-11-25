from swatbotics.python import apriltag as sb
import os
import cv2
import collections

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
    video = cv2.VideoCapture(0)

    while True:
        check, frame = video.read()
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cv2.imshow('test', img)

        try:
            detections = detector.detect(img)
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

        key = cv2.waitKey(1)

        if key == ord('q'):
            break

    video.release()
    cv2.destroyAllWindows()


# TODO stopping condition
if __name__ == '__main__':
    main((1059.96973328701, 1069.2489339794608,
          622.030969436662, 362.4945777620182))
