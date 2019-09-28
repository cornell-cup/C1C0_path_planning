import cv2
import apriltag
from matplotlib import pyplot as plt
import matplotlib.image as mpimg

# img = cv2.imread('apriltag_test_0.jpg', cv2.IMREAD_GRAYSCALE)
img = cv2.imread('image125.jpg', cv2.IMREAD_GRAYSCALE)
detector = apriltag.Detector()
result = detector.detect(img)

for i in range(len(result)):
  # print(result[i].center)
  print(
    # detector.detection_pose(result[i], [315.5, 312.724, 335.013, 229.881]))
    detector.detection_pose(result[i], [18571/8, 18571/8, 1218/8, 562.5/8]))

# img2 = mpimg.imread('apriltag_test_0.jpg')
#print(img)

