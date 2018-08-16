"""
Vinit Ranjan, Chris Eckman
Lineage Logistics
6/4/18

An implementation of an axis aligned bounding box in 3D

Initialization:
point1, point2 - arrays for two corners of the box, which is sufficient to outline an axis aligned box

If any of the dimensions are equal, then the box degenerates into either an axis aligned rectangle or line segment,
but this is not explicitly handled

Assumes (x,y,z) coordinates
"""
import numpy as np


class AxisAlignedBox3D:

    # initialize by the two points given
    def __init__(self, point1=np.array([0, 0, 0], dtype=np.float32), point2=np.array([0, 0, 0], dtype=np.float32)):
        self.point1 = point1
        self.point2 = point2

    # alternative initialization
    @staticmethod
    def init_box_center(center=np.array([0, 0, 0], dtype=np.float32), x_half=1, y_half=1, z_half=1):
        return AxisAlignedBox3D(np.array([center[0] + x_half, center[1] + y_half, center[2] + z_half], dtype=np.float32),
                                np.array([center[0] - x_half, center[1] - y_half, center[2] - z_half], dtype=np.float32))

    # return the eight corners
    def get_corners(self):
        return [np.array([self.point1[0], self.point1[1], self.point1[2]], dtype=np.float32),
                np.array([self.point1[0], self.point2[1], self.point1[2]], dtype=np.float32),
                np.array([self.point2[0], self.point1[1], self.point1[2]], dtype=np.float32),
                np.array([self.point2[0], self.point2[1], self.point1[2]], dtype=np.float32),
                np.array([self.point1[0], self.point1[1], self.point2[2]], dtype=np.float32),
                np.array([self.point1[0], self.point2[1], self.point2[2]], dtype=np.float32),
                np.array([self.point2[0], self.point1[1], self.point2[2]], dtype=np.float32),
                np.array([self.point2[0], self.point2[1], self.point2[2]], dtype=np.float32)]

    # return the smallest/largest x/y/z coordinate
    def min_x(self):
        return min(self.point1[0], self.point2[0])
        # return self.point1[0] if self.point1[0] < self.point2[0] else self.point2[0]

    def min_y(self):
        return min(self.point1[1], self.point2[1])
        # return self.point1[1] if self.point1[1] < self.point2[1] else self.point2[1]

    def min_z(self):
        return min(self.point1[2], self.point2[2])
        # return self.point1[2] if self.point1[2] < self.point2[2] else self.point2[2]

    def max_x(self):
        return max(self.point1[0], self.point2[0])
        # return self.point1[0] if self.point1[0] > self.point2[0] else self.point2[0]

    def max_y(self):
        return max(self.point1[1], self.point2[1])
        # return self.point1[1] if self.point1[1] > self.point2[1] else self.point2[1]

    def max_z(self):
        return max(self.point1[2], self.point2[2])
        # return self.point1[2] if self.point1[2] > self.point2[2] else self.point2[2]

    def center_x(self):
        return (self.min_x() + self.max_x()) / 2.0

    def center_y(self):
        return (self.min_y() + self.max_y()) / 2.0

    def center_z(self):
        return (self.min_z() + self.max_z()) / 2.0

    # return the coordinates of the box with smallest of each value
    def min_corner(self):
        return np.array([self.min_x(), self.min_y(), self.min_z()], dtype=np.float32)

    def max_corner(self):
        return np.array([self.max_x(), self.max_y(), self.max_z()], dtype=np.float32)

    def get_dimensions(self):
        return self.max_corner() - self.min_corner()

    def get_centroid(self):
        return np.array([self.center_x(), self.center_y(), self.center_z()], dtype=np.float32)

    # returns array of points
    def get_edges(self):
        return [[[self.min_x(), self.min_y(), self.min_z()], [self.max_x(), self.min_y(), self.min_z()]],
                [[self.min_x(), self.min_y(), self.min_z()], [self.min_x(), self.max_y(), self.min_z()]],
                [[self.max_x(), self.min_y(), self.min_z()], [self.max_x(), self.max_y(), self.min_z()]],
                [[self.max_x(), self.max_y(), self.min_z()], [self.min_x(), self.max_y(), self.min_z()]],

                [[self.min_x(), self.min_y(), self.min_z()], [self.min_x(), self.min_y(), self.max_z()]],
                [[self.max_x(), self.min_y(), self.min_z()], [self.max_x(), self.min_y(), self.max_z()]],
                [[self.max_x(), self.max_y(), self.min_z()], [self.max_x(), self.max_y(), self.max_z()]],
                [[self.min_x(), self.max_y(), self.min_z()], [self.min_x(), self.max_y(), self.max_z()]],

                [[self.min_x(), self.min_y(), self.max_z()], [self.max_x(), self.min_y(), self.max_z()]],
                [[self.min_x(), self.min_y(), self.max_z()], [self.min_x(), self.max_y(), self.max_z()]],
                [[self.max_x(), self.min_y(), self.max_z()], [self.max_x(), self.max_y(), self.max_z()]],
                [[self.max_x(), self.max_y(), self.max_z()], [self.min_x(), self.max_y(), self.max_z()]]]

    def contains_point(self, point):
        return self.min_x() <= point[0] <= self.max_x() and self.min_y() <= point[1] <= self.max_y() \
                and self.min_z() <= point[2] <= self.max_z()

    def contains_box(self, other_box):
        return self.min_x() < other_box.min_x() < self.max_x() and self.min_x() < other_box.max_x() < self.max_x() and \
            self.min_y() < other_box.min_y() < self.max_y() and self.min_y() < other_box.max_y() < self.max_y() and \
            self.min_z() < other_box.min_z() < self.max_z() and self.min_z() < other_box.max_z() < self.max_z()

    def contained_in_box(self, other_box):
        return other_box.contains_box(self)

    def intersects_box(self, other_box):
        other_corners = other_box.get_corners()
        return not self.contains_box(other_box) and not self.contained_in_box(other_box) and \
            (self.contains_point(other_corners[0]) or self.contains_point(other_corners[1])
             or self.contains_point(other_corners[2]) or self.contains_point(other_corners[3])
             or self.contains_point(other_corners[4]) or self.contains_point(other_corners[5])
             or self.contains_point(other_corners[6]) or self.contains_point(other_corners[7]))

    def equals_box(self, other_box):
        return np.all(self.max_corner() == other_box.max_corner()) and np.all(self.min_corner() == other_box.min_corner())
