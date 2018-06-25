"""
Vinit Ranjan, Chris Eckman
Lineage Logistics
6/4/18

A class to handle the Octree construction, insertion of OctreeNodes

https://github.com/jcummings2/pyoctree/blob/master/octree.py
https://www.gamedev.net/articles/programming/general-and-gameplay-programming/introduction-to-octrees-r3529/
"""
import numpy as np
import copy
from AxisAlignedBox3D import AxisAlignedBox3D
from OctreeNode import OctreeNode


class Octree:

    def __init__(self, bounding_box=AxisAlignedBox3D(np.asarray([0., 0., 0.]), np.asarray([2048., 2048., 2048.]))):
        self.MAX_OBJECTS_PER_CUBE = 1000
        self.root = OctreeNode(bounding_box, 0, [])

    @staticmethod
    def create_node(bounding_box, depth, data_points):
        return OctreeNode(bounding_box, depth, data_points)

    def insert_node(self, data_point):
        if np.any(data_point < self.root.lower_corner):
            return None
        if np.any(data_point > self.root.upper_corner):
            return None
        return self.__insert_node(self.root, self.root.bounding_box.get_dimensions(), self.root, data_point)

    def __insert_node(self, root, dim, parent, data_point):  # TODO implement recursive insertion
        if root is None:
            pos = parent.bounding_box.get_centroid()
            x_offset = dim[0] / 2.0
            y_offset = dim[1] / 2.0
            z_offset = dim[2] / 2.0
            branch = self.__find_branch(parent, data_point)
            if branch == 0:
                new_box = AxisAlignedBox3D.init_box_center(
                    np.asarray([pos[0] - x_offset, pos[1] - y_offset, pos[2] - z_offset]), x_offset, y_offset, z_offset)
            if branch == 1:
                new_box = AxisAlignedBox3D.init_box_center(
                    np.asarray([pos[0] - x_offset, pos[1] - y_offset, pos[2] + z_offset]), x_offset, y_offset, z_offset)
            if branch == 2:
                new_box = AxisAlignedBox3D.init_box_center(
                    np.asarray([pos[0] - x_offset, pos[1] + y_offset, pos[2] - z_offset]), x_offset, y_offset, z_offset)
            if branch == 3:
                new_box = AxisAlignedBox3D.init_box_center(
                    np.asarray([pos[0] - x_offset, pos[1] + y_offset, pos[2] + z_offset]), x_offset, y_offset, z_offset)
            if branch == 4:
                new_box = AxisAlignedBox3D.init_box_center(
                    np.asarray([pos[0] + x_offset, pos[1] - y_offset, pos[2] - z_offset]), x_offset, y_offset, z_offset)
            if branch == 5:
                new_box = AxisAlignedBox3D.init_box_center(
                    np.asarray([pos[0] + x_offset, pos[1] - y_offset, pos[2] + z_offset]), x_offset, y_offset, z_offset)
            if branch == 6:
                new_box = AxisAlignedBox3D.init_box_center(
                    np.asarray([pos[0] + x_offset, pos[1] + y_offset, pos[2] - z_offset]), x_offset, y_offset, z_offset)
            if branch == 7:
                new_box = AxisAlignedBox3D.init_box_center(
                    np.asarray([pos[0] + x_offset, pos[1] + y_offset, pos[2] + z_offset]), x_offset, y_offset, z_offset)

            return OctreeNode(new_box, parent.depth + 1, [data_point])

        elif not root.isLeafNode and (np.any(root.bounding_box.get_centroid() != data_point)
                                      or root.bounding_box.get_centroid() != data_point):
            branch = self.__find_branch(root, data_point)
            new_dim = root.bounding_box.get_dimensions() / 2.0
            root.branches[branch] = self.__insert_node(root.branches[branch], new_dim, root, data_point)
        elif root.isLeafNode:
            if len(root.data_points) < self.MAX_OBJECTS_PER_CUBE:
                root.data_points.append(data_point)
                # print(len(root.data_points))
                # try:
                #     root.data_points.append(data_point)
                # except AttributeError:
                #     print(root.data_points)
                #     print(type(root.data_points))
                #     exit(1)
            else:
                root.data_points.append(data_point)
                objects = copy.deepcopy(root.data_points)  # TODO do we need deepcopy here?
                root.data_points = []
                root.isLeafNode = False
                new_dim = root.bounding_box.get_dimensions() / 2.0
                for k in objects:
                    branch = self.__find_branch(root, k)
                    root.branches[branch] = self.__insert_node(root.branches[branch], new_dim, root, k)
        return root

    @staticmethod
    def __find_branch(root, data):
        """
        branch: 0 1 2 3 4 5 6 7
        x:      - - - - + + + +
        y:      - - + + - - + +
        z:      - + - + - + - +
        """
        index = 0
        root_center = root.bounding_box.get_centroid()
        if data[0] >= root_center[0]:
            index |= 4
        if data[1] >= root_center[1]:
            index |= 2
        if data[2] >= root_center[2]:
            index |= 1
        return index

    def iterate_dfs(self):
        gen = self.__iterate_dfs(self.root)
        for k in gen:
            yield k

    @staticmethod
    def __iterate_dfs(root):
        for branch in root.branches:
            if branch is None: continue
            for n in Octree.__iterate_dfs(branch):
                yield n
            if branch.isLeafNode:
                yield branch
