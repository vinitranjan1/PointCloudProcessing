from SavePointsAsLAS import save_points_as_las
from SubsampleFrac import subsample_frac
from ReadRawLAS import read_raw_las_data
from laspy.file import File

input1 = "MantecaRoom1/room1.las"
out = "MantecaRoom1/room1p5samp.las"
with File(input1, mode='r') as file:
    points = read_raw_las_data(input1)
    samp = subsample_frac(points, .5)
    save_points_as_las(samp, out, file.header)
