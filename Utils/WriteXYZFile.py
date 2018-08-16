"""
Vinit Ranjan, Chris Eckman
Lineage Logistics

A function to take in a las file and write it in the .xyz format

Inputs:
filename - output xyz file name
"""
from tqdm import tqdm
from PlotUtils.VtkPointCloud import VtkPointCloud
from PlotUtils.CreateVTKPCFromArray import create_vtkpc_from_array
from Utils.ReadRawLAS import read_raw_las_data
import vtk


def write_xyz_file(file_name):
    points = read_raw_las_data(file_name)
    pc = create_vtkpc_from_array(points)
    writer = vtk.vtkSimplePointsWriter()
    writer.SetFileName(file_name[:-4]+".xyz")
    writer.SetInputData(pc.vtkPolyData)
    print("Writing to %s" % file_name[:-4]+".xyz")
    writer.Write()

filename = "MantecaDock/fourPallets.las"
write_xyz_file(filename)
