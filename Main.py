from laspy.file import File
from PlotUtils.CreateVTKPCFromArray import create_vtkpc_from_array
from PlotUtils.PointCloudPlotQt import create_point_cloud_plot_qt
from SubsampleFunctions.SubsampleFracFromLAS import subsample_frac_from_las_data


def main():
    input1 = "Data/MantecaFiltered/MantecaRailSlice.las"
    input2 = "Data/MantecaFiltered/RailDockPallet.las"
    with File(input1, mode='r') as f:
        input_header = f.header
        to_plot = []  # list of VTK Point Clouds to plot

        points = subsample_frac_from_las_data(input1, .01)
        pc = create_vtkpc_from_array(points)
        to_plot.append(pc)

        # points2 = subsample_frac_from_las_data(input2, .1)
        # pc2 = create_vtkpc_from_array(points2)
        # to_plot.append(pc2)

        create_point_cloud_plot_qt(to_plot, input_header=input_header, axes_on=True)


if __name__ == "__main__":
    main()
