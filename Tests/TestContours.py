import cv2
import numpy as np

# read and scale down image
image_file = "../MantecaDock/Images/dockCollapseZmeshp05NB.png"
image_file = "../MantecaRoom1/Images/room1collapseZTp25meshp1_ChrisMessedUp.png"
# read and scale down image
img = cv2.pyrDown(cv2.imread(image_file, 0))
img = cv2.imread(image_file, cv2.IMREAD_UNCHANGED)

# threshold image
ret, threshed_img = cv2.threshold(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY),
                                  127, 255, cv2.THRESH_BINARY)
# find contours and get the external one
image, contours, hier = cv2.findContours(threshed_img, cv2.RETR_TREE,
                                         cv2.CHAIN_APPROX_SIMPLE)

# with each contour, draw boundingRect in green
# a minAreaRect in red and
# a minEnclosingCircle in blue
# for cnt in contours:
#     # calculate epsilon base on contour's perimeter
#     # contour's perimeter is returned by cv2.arcLength
#     epsilon = 0.01 * cv2.arcLength(cnt, True)
#     # get approx polygons
#     approx = cv2.approxPolyDP(cnt, epsilon, True)
#     # draw approx polygons
#     cv2.drawContours(img, [approx], -1, (0, 255, 0), 1)
#
#     # hull is convex shape as a polygon
#     hull = cv2.convexHull(cnt)
#     cv2.drawContours(img, [hull], -1, (0, 0, 255))

for c in contours:
    # get the bounding rect
    x, y, w, h = cv2.boundingRect(c)
    # draw a green rectangle to visualize the bounding rect
    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # get the min area rect
    rect = cv2.minAreaRect(c)
    box = cv2.boxPoints(rect)
    # convert all coordinates floating point values to int
    box = np.int0(box)
    # draw a red 'nghien' rectangle
    cv2.drawContours(img, [box], 0, (0, 0, 255))

print(len(contours))
cv2.drawContours(img, contours, -1, (255, 255, 0), 1)

window_name = "contours"
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
cv2.resizeWindow(window_name, 600, 600)
cv2.imshow(window_name, img)
cv2.waitKey(0)
cv2.destroyAllWindows()