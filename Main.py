import sys
from laspy.file import File
from tqdm import tqdm, trange
from CreateVTKPCFromArray import create_vtkpc_from_array
from PointCloudPlotQt import create_point_cloud_plot_qt
from SubsampleFromLASData import subsample_from_las_data
from SubsampleFracFromLAS import subsample_frac_from_las_data
from Filters.RadiusOutlierFilter import radius_outlier_filter
from Filters.ANNGuidedFilter import ann_guided_filter
from Filters.ANNGuidedFilterPrebuiltTree import ann_guided_filter_prebuilt_tree
from Filters.ANNGuidedFilterMultiEps import ann_guided_filter_multi_eps
from Filters.ANNRadialMultiStdev import ann_radial_filter_multi_stdev
from Filters.GuidedFilterkNN import guided_filter_kNN
from Filters.ANNRadialFilter import ann_radial_filter
from Filters.RoundingFilter import rounding_filter
from Filters.ThresholdFilter import threshold_filter
from NaiveSlice import naive_slice
from NaiveSliceFromLAS import naive_slice_from_las
from AxisAlignedBox3D import AxisAlignedBox3D
from SavePointsAsLAS import save_points_as_las
import pdb
from ReadRawLAS import read_raw_las_data
from VtkPointCloud import VtkPointCloud
import h5py


def main():
    input1 = "MantecaFiltered/MantecaRailSlice.las"
    with File(input1, mode='r') as f:
        input_header = f.header
        to_plot = []

        points = read_raw_las_data(input1)
        pc = create_vtkpc_from_array(points)
        to_plot.append(pc)

        create_point_cloud_plot_qt(to_plot, input_header=input_header, axes_on=True)


if __name__ == "__main__":
    main()
