import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import math

image_file = "../MantecaRoom1/Images/room1sliceCollapseZmeshp05NB.png"
# image_file = "../MantecaRoom1/Images/room1collapseZTp25meshp1_ChrisMessedUp.png"
# image_file = "../MantecaDock/Images/dockCollapseZmeshp05NB.png"
img = cv2.imread(image_file, 0)
height, width = img.shape
print(height, width)
# ret, thresh = cv2.threshold(img, 127, 255, 0)
# contours, hierarchy = cv2.findContours(thresh, 1, 2)
# cnt = contours[0]
# gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#
# gray = np.float32(gray)
edges = cv2.Canny(img, 50, 200, apertureSize=3)
minLineLength = 10
lines = cv2.HoughLinesP(image=edges, rho=1, theta=np.pi / 1800, threshold=50, lines=np.array([]),
                        minLineLength=minLineLength, maxLineGap=25)

# rect = cv2.minAreaRect(img)
# box = cv2.boxPoints(rect)
# box = np.int0(box)
# cv2.drawContours(img,[box],0,(0,0,255),2)
# ref https://docs.opencv.org/3.1.0/dd/d49/tutorial_py_contour_features.html

# corner harris ref https://docs.opencv.org/3.0-beta/doc/py_tutorials/py_feature2d/py_features_harris/py_features_harris.html
r0 = [384, -358]
r1 = [546, -550]
r2 = [567, -294]
r3 = [381, -102]
slope = []
x_zero = []
y_zero = []

a, b, c = lines.shape
for i in range(a):
    # cv2.line(img, (lines[i][0][0], lines[i][0][1]), (lines[i][0][2], lines[i][0][3]), (0, 0, 255), 1, cv2.LINE_AA)
    p0 = (lines[i][0][0], -lines[i][0][1])
    p1 = (lines[i][0][2], -lines[i][0][3])
    # print(p0, p1)
    x0 = p0[0]
    y0 = p0[1]
    x1 = p1[0]
    y1 = p1[1]
    m = (y1 - y0) / (x1 - x0)
    # print(m)
    al = -m
    bl = 1
    cl = m * x0 - y0
    # print(-y0)
    # print(m * x0)
    slope.append(float(m))
    x_zero.append(float(-y0))
    y_zero.append(m * float(x0))
    # print(al * x0 + bl * y0 + cl)
    # print(al * x1 + bl * y1 + cl)

# corners = cv2.cornerHarris(img, 2, 3, .04)
# corners = cv2.dilate(corners, None)
#
# img[corners > 0.01*corners.max()] = [0, 0, 255]

### start Chris' stuff

# start_x = min([int(i) for i in x_zero])
# end_x = max([int(i) for i in x_zero])
# start_y = min([int(i) for i in y_zero])
# end_y = max([int(i) for i in y_zero])
#
# (amt_x, val_x, patches_x) = plt.hist(x_zero, bins=range(start_x, end_x))
# (amt_y, val_y, patches_y) = plt.hist(y_zero, bins=range(start_y, end_y))
#
# coords_aty0 = val_y[np.argmax(amt_y)]
#
# indices = [i for i, y in enumerate(y_zero) if math.floor(y) == coords_aty0]
# slope_list = []
# for indx in indices:
#     slope_list.append(slope[indx])
#
# fig, ax = plt.subplots()
# img = mpimg.imread(image_file)
# print(img.shape)
# ax.imshow(img)
#
# x_vals = np.array(ax.get_xlim())
# y_vals = coords_aty0 + -np.mean(slope_list) * x_vals
#
# ax.plot(x_vals, y_vals, 'r-')
# ax.invert_yaxis()
# # pdb.set_trace()
# plt.show()
## end Chris' method

a, b, c = lines.shape
for i in range(a):
    cv2.line(img, (lines[i][0][0], lines[i][0][1]), (lines[i][0][2], lines[i][0][3]), (0, 0, 255), 1, cv2.LINE_AA)
    p0 = (lines[i][0][0], -lines[i][0][1])
    p1 = (lines[i][0][2], -lines[i][0][3])
    # print(p0, p1)
    x0 = p0[0]
    y0 = p0[1]
    x1 = p1[0]
    y1 = p1[1]
    m = (y1 - y0) / (x1 - x0)
    # print(m)
    al = -m
    bl = 1
    cl = m * x0 - y0
# print(al * x0 + bl * y0 + cl)
# print(al * x1 + bl * y1 + cl)

# rect = cv2.minAreaRect(cnt)
# box = cv2.boxPoints(rect)
# box = np.int0(box)
# cv2.drawContours(img, [box], 0, (0, 0, 255), 2)


# corners = cv2.cornerHarris(img, 2, 3, .04)
# corners = cv2.dilate(corners, None)
#
# img[corners > 0.01*corners.max()] = [0, 0, 255]


cv2.namedWindow(image_file, cv2.WINDOW_NORMAL)
cv2.resizeWindow(image_file, 600, 600)

cv2.imshow(image_file, img)
cv2.waitKey(0)
cv2.destroyAllWindows()
