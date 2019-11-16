from swatbotics.python import apriltag as sb
import argparse
import os
import cv2
import collections


def get_pose(options):
    det = sb.Detector(options, searchpath=[os.path.join(os.path.dirname(__file__), 'swatbotics/build/lib')])

    use_gui = not options.no_gui
    for filename in options.filenames:
        orig = cv2.imread(filename)
        if len(orig.shape) == 3:
            gray = cv2.cvtColor(orig, cv2.COLOR_RGB2GRAY)
        else:
            gray = orig

        detections, dimg = det.detect(gray, return_image=True)

        if len(orig.shape) == 3:
            overlay = orig // 2 + dimg[:, :, None] // 2
        else:
            overlay = gray // 2 + dimg // 2

        num_detections = len(detections)
        print('Detected {} tags in {}\n'.format(
            num_detections, os.path.split(filename)[1]))

        for i, detection in enumerate(detections):
            print('Detection {} of {}:'.format(i + 1, num_detections))
            print()
            print(detection.tostring(indent=2))

            if options.camera_params is not None:
                pose, e0, e1 = det.detection_pose(detection,
                                                  options.camera_params,
                                                  options.tag_size)

                sb._draw_pose(overlay,
                              options.camera_params,
                              options.tag_size,
                              pose)

                print(detection.tostring(
                    collections.OrderedDict([('Pose', pose),
                                             ('InitError', e0),
                                             ('FinalError', e1)]),
                    indent=2))

            print()

        if options.debug_images:
            cv2.imwrite('detections.png', overlay)

        if use_gui:
            cv2.imshow('win', overlay)
            while cv2.waitKey(5) < 0:
                pass


def get_args():
    parser = argparse.ArgumentParser(description='pose estimate')
    parser.add_argument('filenames', metavar='IMAGE', nargs='+',
                        help='files to scan')

    parser.add_argument('-n', '--no-gui', action='store_true',
                        help='suppress OpenCV gui')

    parser.add_argument('-d', '--debug-images', action='store_true',
                        help='output debug detection image')

    parser.add_argument('-k', '--camera-params', type=sb._camera_params,
                        default=None,
                        help='intrinsic parameters for camera (in the form fx,fy,cx,cy)')

    parser.add_argument('-s', '--tag-size', type=float,
                        default=1.0,
                        help='tag size in user-specified units (default=1.0)')

    sb.add_arguments(parser)
    options = parser.parse_args()
    return options


def main():
    options = get_args()
    get_pose(options)


if __name__ == '__main__':
    main()
