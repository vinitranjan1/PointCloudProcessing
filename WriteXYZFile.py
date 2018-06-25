import numpy as np
import pdb
from laspy.file import File
from tqdm import tqdm, trange
from VtkPointCloud import VtkPointCloud
from ReadRawLAS import read_raw_las_data
import vtk


def write_xyz_file(file_name):
    points = read_raw_las_data(file_name)
    pc = VtkPointCloud()
    for point in tqdm(points, total=len(points), desc="Adding"):
        pc.addPoint(point)
    writer = vtk.vtkSimplePointsWriter()
    writer.SetFileName(file_name[:-4]+".xyz")
    writer.SetInputData(pc.vtkPolyData)
    print("Writing to %s" % file_name[:-4]+".xyz")
    writer.Write()

filename = "MantecaDock/fourPallets.las"
write_xyz_file(filename)
