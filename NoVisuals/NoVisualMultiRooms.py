import sys
sys.path.append("../")
from Filters.ANNGuidedFilter import ann_guided_filter
from Filters.ANNRadialFilter import ann_radial_filter
from Filters.RoundingFilter import rounding_filter
from Utils.WriteToConfig import write_to_config
from Utils.ReadRawLAS import read_raw_las_data
from Utils.SavePointsAsLAS import save_points_as_las
from laspy.file import File

# input/output file names
room2 = "../MantecaRoom2/room2.las"
room3 = "../MantecaRoom3/room3.las"
room4 = "../MantecaRoom4/room4S.las"
room5 = "../MantecaRoom5/room5.las"
room6 = "../MantecaRoom6/room6S.las"
dock = "../MantecaDock/dock.las"
room2out = "../MantecaRoom2/room2F.las"
room3out = "../MantecaRoom3/room3F.las"
room4out = "../MantecaRoom4/room4F.las"
room5out = "../MantecaRoom5/room5F.las"
room6out = "../MantecaRoom6/room6F.las"
dockout = "../MantecaDock/dockF.las"
config_file = "roomsconfig.txt"

with File(room2, mode='r') as f:
    print("Starting Room 2")
    # points = subsample_frac_from_las_data("../MantecaRoom1/room1slice.las", sample_frac=.01)
    points = read_raw_las_data(room2)
    points, kwargs = ann_guided_filter(points, num_neighbors=50, filter_eps=.07, config_file=config_file)
    write_to_config(config_file, room2, ann_guided_filter.__name__, kwargs, include_las_name=True)
    points, kwargs = rounding_filter(points, config_file=config_file)
    write_to_config(config_file, room2, rounding_filter.__name__, kwargs, include_las_name=False)
    points, kwargs = ann_radial_filter(points, sd_cutoff=1.3, config_file=config_file)
    write_to_config(config_file, room2, ann_radial_filter.__name__, kwargs, include_las_name=False)
    write_to_config(config_file, done_message="Written to " + room2out + "\n")
    save_points_as_las(points, room2out, f.header)
    print("Finished Room 2")
    del points

with File(room3, mode='r') as f:
    print("Starting Room 3")
    # points = subsample_frac_from_las_data("../MantecaRoom4/Ceckman.las", sample_frac=.01)
    points = read_raw_las_data(room3)
    points, kwargs = ann_guided_filter(points, num_neighbors=50, filter_eps=.07, config_file=config_file)
    write_to_config(config_file, room3, ann_guided_filter.__name__, kwargs, include_las_name=True)
    points, kwargs = rounding_filter(points, config_file=config_file)
    write_to_config(config_file, room3, rounding_filter.__name__, kwargs, include_las_name=False)
    points, kwargs = ann_radial_filter(points, sd_cutoff=1.3, config_file=config_file)
    write_to_config(config_file, room3, ann_radial_filter.__name__, kwargs, include_las_name=False)
    write_to_config(config_file, done_message="Written to " + room3out + "\n")
    save_points_as_las(points, room3out, f.header)
    print("Finished Room 3")
    del points

with File(room4, mode='r') as f:
    print("Starting Room 3")
    # points = subsample_frac_from_las_data(room2, sample_frac=.01)
    points = read_raw_las_data(room4)
    points, kwargs = ann_guided_filter(points, num_neighbors=50, filter_eps=.07, config_file=config_file)
    write_to_config(config_file, room4, ann_guided_filter.__name__, kwargs, include_las_name=True)
    points, kwargs = rounding_filter(points, config_file=config_file)
    write_to_config(config_file, room4, rounding_filter.__name__, kwargs, include_las_name=False)
    points, kwargs = ann_radial_filter(points, sd_cutoff=1.3, config_file=config_file)
    write_to_config(config_file, room4, ann_radial_filter.__name__, kwargs, include_las_name=False)
    write_to_config(config_file, done_message="Written to " + room4out + "\n")
    save_points_as_las(points, room4out, f.header)
    print("Finished Room 4")
    del points

with File(room5, mode='r') as f:
    print("Starting Room 3")
    # points = subsample_frac_from_las_data(room2, sample_frac=.01)
    points = read_raw_las_data(room5)
    points, kwargs = ann_guided_filter(points, num_neighbors=50, filter_eps=.07, config_file=config_file)
    write_to_config(config_file, room5, ann_guided_filter.__name__, kwargs, include_las_name=True)
    points, kwargs = rounding_filter(points, config_file=config_file)
    write_to_config(config_file, room5, rounding_filter.__name__, kwargs, include_las_name=False)
    points, kwargs = ann_radial_filter(points, sd_cutoff=1.3, config_file=config_file)
    write_to_config(config_file, room5, ann_radial_filter.__name__, kwargs, include_las_name=False)
    write_to_config(config_file, done_message="Written to " + room5out + "\n")
    save_points_as_las(points, room5out, f.header)
    print("Finished Room 5")
    del points

with File(room6, mode='r') as f:
    print("Starting Room 3")
    # points = subsample_frac_from_las_data(room2, sample_frac=.01)
    points = read_raw_las_data(room6)
    points, kwargs = ann_guided_filter(points, num_neighbors=50, filter_eps=.07, config_file=config_file)
    write_to_config(config_file, room6, ann_guided_filter.__name__, kwargs, include_las_name=True)
    points, kwargs = rounding_filter(points, config_file=config_file)
    write_to_config(config_file, room6, rounding_filter.__name__, kwargs, include_las_name=False)
    points, kwargs = ann_radial_filter(points, sd_cutoff=1.3, config_file=config_file)
    write_to_config(config_file, room6, ann_radial_filter.__name__, kwargs, include_las_name=False)
    write_to_config(config_file, done_message="Written to " + room6out + "\n")
    save_points_as_las(points, room6out, f.header)
    print("Finished Room 6")
    del points

with File(dock, mode='r') as f:
    print("Starting Room 3")
    # points = subsample_frac_from_las_data(room2, sample_frac=.01)
    points = read_raw_las_data(dock)
    points, kwargs = ann_guided_filter(points, num_neighbors=50, filter_eps=.07, config_file=config_file)
    write_to_config(config_file, dock, ann_guided_filter.__name__, kwargs, include_las_name=True)
    points, kwargs = rounding_filter(points, config_file=config_file)
    write_to_config(config_file, dock, rounding_filter.__name__, kwargs, include_las_name=False)
    points, kwargs = ann_radial_filter(points, sd_cutoff=1.3, config_file=config_file)
    write_to_config(config_file, dock, ann_radial_filter.__name__, kwargs, include_las_name=False)
    write_to_config(config_file, done_message="Written to " + dockout + "\n")
    save_points_as_las(points, dockout, f.header)
    print("Finished Dock")
    del points
