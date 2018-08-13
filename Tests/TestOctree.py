import numpy as np
import time
from Utils.Octree import Octree
from Utils.AxisAlignedBox3D import AxisAlignedBox3D


class TestObject:
    def __init__(self, name, position):
        self.name = name
        self.position = position

    @property
    def __str__(self):
        return u"name: {0} position: {1}".format(self.name, self.position)

NUM_TEST_OBJECTS = 20000
NUM_LOOKUPS = 20000

enclosure = AxisAlignedBox3D(np.asarray([0., 0., 0.]), np.asarray([128., 128., 128.]))
center = enclosure.get_centroid()

testObjects = []
for x in range(NUM_TEST_OBJECTS):
    name = "Node__" + str(x)
    pos = np.array(center + np.random.uniform(0., 64., 3))
    testObjects.append(TestObject(name, pos))

tree = Octree(enclosure)
Start = time.time()
for test in testObjects:
    tree.insert_node(test.position)
End = time.time() - Start
print("%d node tree generated in %f seconds" % (NUM_TEST_OBJECTS, End))
