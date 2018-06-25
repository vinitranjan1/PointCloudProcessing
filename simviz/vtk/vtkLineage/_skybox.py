import vtk, numpy as np, os

class vtkSkybox(vtk.vtkAssembly):

    __plane_data = [ \
            {'orientation': np.array([0, 0, 0]),    # -z
             'position': np.array([1/2, 1, -1/2])},
            {'orientation': np.array([180, 0, 0]),  # +z
             'position': np.array([1/2, 1, 1/2])},
            {'orientation': np.array([90, 0, 0]),   # +y
             'position': np.array([1/2, 1/2, 0])},
            {'orientation': np.array([90, 0, 180]), # -y
             'position': np.array([3/2, -1/2, 0])},
            {'orientation': np.array([90, 0, -90]),   # +x
             'position': np.array([1/2, 1/2, 0])},
            {'orientation': np.array([90, 0, 90]), # -x
             'position': np.array([-1/2, 3/2, 0])}
        ]

    def __init__(self, renderer=None, texture_path=None, origin=vtk.vtkVector3d(0, 0, 0), scale=10**5, ground_plane=True):
        super().__init__()

        # Potentially make it such that it tracks to the active camera and is always rendered at the back of the depth buffer... more sophisticated than I'm concerned about sorting out at the moment.
        # renderer.AddObserver('EndEvent', self.update)

        self._texture_path = texture_path
        self._origin = origin
        self._scale = scale

        filename, file_ext = os.path.splitext(texture_path)
        if file_ext == '.png':
            self.__image_reader = vtk.vtkPNGReader()
        elif file_ext == '.jpg':
            self.__image_reader = vtk.vtkJPEGReader()
        self.__image_reader.SetFileName(self._texture_path)
        self.__texture = vtk.vtkTexture()
        self.__texture.SetInputConnection(self.__image_reader.GetOutputPort())

        self.__planes = [vtk.vtkPlaneSource() for i in range(7)]
        self.__mappers = [vtk.vtkPolyDataMapper() for i in range(7)]
        self.__textured_planes = [vtk.vtkActor() for i in range(7)]

        for i in range(6):
            self.__planes[i].SetCenter(0, 0, 0)
            self.__planes[i].SetNormal(0, 0, 1)

            self.__mappers[i].SetInputConnection(self.__planes[i].GetOutputPort())
            self.__textured_planes[i].SetMapper(self.__mappers[i])
            self.__textured_planes[i].SetTexture(self.__texture)

            self.__textured_planes[i].GetProperty().SetLighting(False)
            self.__textured_planes[i].SetScale(self._scale * 4, self._scale * 3, 1)
            self.__textured_planes[i].SetOrientation(self.__plane_data[i]['orientation'])
            self.__textured_planes[i].SetPosition(self.__plane_data[i]['position'] * scale)

            self.AddPart(self.__textured_planes[i])

        if ground_plane:
            self.__planes[6].SetCenter(0, 0, 0)
            self.__planes[6].SetNormal(0, 0, 1)
            self.__mappers[6].SetInputConnection(self.__planes[6].GetOutputPort())
            self.__textured_planes[6].SetMapper(self.__mappers[6])

            self.__textured_planes[6].GetProperty().SetLighting(False)
            self.__textured_planes[6].SetScale(self._scale)
            self.__textured_planes[6].SetPosition(0, 0, -0.1)
            self.__textured_planes[6].GetProperty().SetColor(0.9, 0.9, 0.9)

            self.AddPart(self.__textured_planes[6])

        renderer.AddActor(self)

    def update(self, obj, event):
        self.SetPosition(obj.GetActiveCamera().GetPosition())
