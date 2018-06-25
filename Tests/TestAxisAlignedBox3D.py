import numpy as np
from AxisAlignedBox3D import AxisAlignedBox3D

x = AxisAlignedBox3D(np.array([0, 0, 0], dtype=np.float32), np.array([1, 1, 1], dtype=np.float32))
y = AxisAlignedBox3D.init_box_center(np.array([.5, .5, .5], dtype=np.float32), .5, .5, .5)

print(x.get_corners())
print(y.get_corners())

assert x.equals_box(y), "fail equality"
