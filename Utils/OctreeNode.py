"""
Vinit Ranjan, Chris Eckman
Lineage Logistics
6/4/18

A class for the nodes to be put into an Octree

https://github.com/jcummings2/pyoctree/blob/master/octree.py
https://www.gamedev.net/articles/programming/general-and-gameplay-programming/introduction-to-octrees-r3529/
"""
from Utils.AxisAlignedBox3D import AxisAlignedBox3D


class OctreeNode:

    def __init__(self, bounding_box=AxisAlignedBox3D(), depth=0, data_points=[]):
        """
        branch: 0 1 2 3 4 5 6 7
        x:      - - - - + + + +
        y:      - - + + - - + +
        z:      - + - + - + - +
        """
        self.bounding_box = bounding_box
        self.depth = depth
        self.data_points = data_points

        #self.bounding_box_center = bounding_box.get_centroid()
        #self.bounding_box_dimensions = bounding_box.get_dimensions()
        self.isLeafNode = True
        self.branches = [None]*8
        self.lower_corner = bounding_box.min_corner()
        self.upper_corner = bounding_box.max_corner()
