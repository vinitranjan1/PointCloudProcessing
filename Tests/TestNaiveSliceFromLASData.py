import vtk
from tqdm import tqdm
from AxisAlignedBox3D import AxisAlignedBox3D
from SliceFunctions.NaiveSliceFromLAS import naive_slice_from_las
from VtkPointCloud import VtkPointCloud

input_file = "../MantecaRoom1/rack.las"
out_file = "../MantecaDock/smallArea.las"
pointCloud = VtkPointCloud()
filteredPointCloud = VtkPointCloud()


# inFile = File(out_file, mode='r')
# outFile = File(out_file, mode='w', header=inFile.header)

pointCloud = VtkPointCloud()

print("reading from %s" % input_file)
sliced = naive_slice_from_las(input_file, AxisAlignedBox3D([197.5000, -6.7000, -.2000], [209.5000, 1.0600, 8.6000]))
# pdb.set_trace()
# 1975000, 2095000, -67000, 10600, -2000, 86000 minx maxx miny maxy minz maxz
for point in tqdm(sliced, total=len(sliced), desc="Adding"):
    pointCloud.addPoint(point)

print("Number of points: %d" % len(sliced))
print('Plotting')
# Renderer
renderer = vtk.vtkRenderer()
renderer.AddActor(pointCloud.vtkActor)
renderer.SetBackground(.2, .3, .4)
renderer.ResetCamera()

# Render Window
renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(renderer)

# Interactor
renderWindowInteractor = vtk.vtkRenderWindowInteractor()
renderWindowInteractor.SetRenderWindow(renderWindow)

# Begin Interaction
renderWindow.Render()
renderWindowInteractor.Start()
# outFile.close()
