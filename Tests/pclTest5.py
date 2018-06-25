#!/usr/bin/env python
import vtk
from vtk.test import Testing
from vtk.util.misc import vtkGetDataRoot
VTK_DATA_ROOT = vtkGetDataRoot()

# Interpolate onto a volume

# Parameters for debugging
NPts = 1000000
math = vtk.vtkMath()

# create pipeline
#
points = vtk.vtkPoints()
points.SetDataTypeToFloat()
points.SetNumberOfPoints(NPts)
scalars = vtk.vtkFloatArray()
scalars.SetNumberOfTuples(NPts)
scalars.SetName("scalars")
for i in range(0,NPts):
    points.SetPoint(i,math.Random(-1,1),math.Random(-1,1),math.Random(-1,1))
    scalars.SetValue(i,math.Random(0,1))

polydata = vtk.vtkPolyData()
polydata.SetPoints(points)
polydata.GetPointData().SetScalars(scalars)

# Create a sphere implicit function
sphere = vtk.vtkSphere()
sphere.SetCenter(0.9,0.1,0.1)
sphere.SetRadius(0.33)

# Extract points within sphere
extract = vtk.vtkFitImplicitFunction()
extract.SetInputData(polydata)
extract.SetImplicitFunction(sphere)
extract.SetThreshold(0.005)

# Time execution
timer = vtk.vtkTimerLog()
timer.StartTimer()
extract.Update()
timer.StopTimer()
time = timer.GetElapsedTime()
print("Time to extract points: {0}".format(time))
print("   Number removed: {0}".format(extract.GetNumberOfPointsRemoved()),
      " (out of: {}".format(NPts))

# First output are the non-outliers
extMapper = vtk.vtkPointGaussianMapper()
extMapper.SetInputConnection(extract.GetOutputPort())
extMapper.EmissiveOff()
extMapper.SetScaleFactor(0.0)

extActor = vtk.vtkActor()
extActor.SetMapper(extMapper)

# Create an outline
outline = vtk.vtkOutlineFilter()
outline.SetInputData(polydata)

outlineMapper = vtk.vtkPolyDataMapper()
outlineMapper.SetInputConnection(outline.GetOutputPort())

outlineActor = vtk.vtkActor()
outlineActor.SetMapper(outlineMapper)

# Create the RenderWindow, Renderer and both Actors
#
ren0 = vtk.vtkRenderer()
ren1 = vtk.vtkRenderer()
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(ren0)
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

# Add the actors to the renderer, set the background and size
#
ren0.AddActor(extActor)
ren0.AddActor(outlineActor)
ren0.SetBackground(0.1, 0.2, 0.4)

renWin.SetSize(250,250)

cam = ren0.GetActiveCamera()
cam.SetFocalPoint(1,1,1)
cam.SetPosition(0,0,0)
ren0.ResetCamera()

ren1.SetActiveCamera(cam)

iren.Initialize()

# render the image
#
renWin.Render()

iren.Start()
