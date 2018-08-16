from laspy.file import File
from PlotUtils.CreateVTKPCFromArray import create_vtkpc_from_array
from PlotUtils.PointCloudPlotQt import create_point_cloud_plot_qt
from Filters.ANNGuidedFilter import ann_guided_filter
from SliceFunctions.NaiveSliceFromLAS import naive_slice_from_las
from Utils.AxisAlignedBox3D import AxisAlignedBox3D
from Utils.ReadRawLAS import read_raw_las_data
from SubsampleFunctions.SubsampleFracFromLAS import subsample_frac_from_las_data
from BaseProjectDirectory import base_project_dir


def main():
    input1 = "Data/MantecaFiltered/MantecaRailSlice.las"
    with File(input1, mode='r') as f:
        input_header = f.header
        to_plot = []  # list of VTK Point Clouds to plot

        points = subsample_frac_from_las_data(input1, .01)
        pc = create_vtkpc_from_array(points)
        to_plot.append(pc)

        create_point_cloud_plot_qt(to_plot, input_header=input_header, axes_on=True)


if __name__ == "__main__":
    main()
