import vtk, numpy as np

from ._databuffer import *
from ._animation import *
from ._helpers import *
from ._settings import *
import pdb

class LevelActor(vtk.vtkPropAssembly, vtkLineageSystem):

    """
    LevelActor

    Extends vtk.vtkPropAssembly to represent a level. This includes a beam structure represented as a line grid and the aisle sled.
    """

    def __init__(self, playback_manager=None, data=None, name=None, **kargs):
        super().__init__()
        self.name = name
        self.initialized = False
        self.cart_location = np.array([0, 0, 0])
        self.base_location = np.array([0, 0, 0])
        self.width = 0
        self.width_unit_vector = np.array([0, 1, 0])
        self.stack_depths = [0, 0]
        self.stack_unit_vectors = [np.array([-1, 0, 0]), np.array([1, 0, 0])]
        if kargs: self.initialize(**kargs)

        self.__databuffer = LevelDataFrameBuffer(data, playback_manager, name=name+' BUFFER')
        self.__databuffer.start()

    def initialize(self, base_location=None, width=0, stack_depths=[0, 0], width_unit_vector=np.array([0, 1, 0]), stack_unit_vectors=[np.array([-1, 0, 0]), np.array([1, 0, 0])]):
        if not base_location: return -1

        # pdb.set_trace()
        # update base location
        self.width = int(width)
        self.stack_depths = [float(i) for i in stack_depths]
        self.base_location = [float(i) for i in base_location]

        # path of level cart's main aisle
        # self.__path_line = vtk.vtkLineSource()
        # self.__path_line.SetPoint1(self.base_location)
        # self.__path_line.SetPoint2([float(a + self.width*b*PALLET_SLOT.y) for a, b in zip(self.base_location, width_unit_vector)])
        # self.__path_tubefilter = vtk.vtkTubeFilter()
        # self.__path_tubefilter.SetInputConnection(self.__path_line.GetOutputPort())
        # self.__path_tubefilter.SetRadius(6.0)
        # self.__path_tubefilter.SetNumberOfSides(6)
        # self.__path_tubefilter.CappingOn()
        # self.__path_mapper = vtk.vtkPolyDataMapper()
        # self.__path_mapper.SetInputConnection(self.__path_tubefilter.GetOutputPort())
        # self.__path_actor = vtk.vtkActor()
        # self.__path_actor.SetMapper(self.__path_mapper)
        # self.AddPart(self.__path_actor)

        # level parent cart
        self.__level_parent_cart_source = vtk.vtkCubeSource()
        self.__level_parent_cart_source.SetBounds(
            -0.5 * PALLET_SLOT.x, 0.5 * PALLET_SLOT.x,
            -0.5 * PALLET_SLOT.y, 0.5 * PALLET_SLOT.y,
            -0.1 * PALLET_SLOT.z, 0.1 * PALLET_SLOT.z)
        self.__level_parent_cart_mapper = vtk.vtkPolyDataMapper()
        self.__level_parent_cart_mapper.SetInputConnection(self.__level_parent_cart_source.GetOutputPort())
        self.__level_parent_cart_actor = vtk.vtkActor()
        self.__level_parent_cart_actor.SetMapper(self.__level_parent_cart_mapper)
        self.__level_parent_cart_actor.GetProperty().SetColor(vtk.vtkNamedColors().GetColor3d('white'))
        self.AddPart(self.__level_parent_cart_actor)

        # level child cart (currently unnecessary until logging includes child
        #                   aisle data)

        # self.__level_child_cart_source = vtk.vtkCubeSource()
        # self.__level_child_cart_source.SetBounds(
        #     -0.45 * PALLET_SLOT.x, 0.45 * PALLET_SLOT.x,
        #     -0.45 * PALLET_SLOT.y, 0.45 * PALLET_SLOT.y,
        #     -0.1 * PALLET_SLOT.z, 0.15 * PALLET_SLOT.z)
        # self.__level_child_cart_mapper = vtk.vtkPolyDataMapper()
        # self.__level_child_cart_mapper.SetInputConnection(self.__level_child_cart_source.GetOutputPort())
        # self.__level_child_cart_actor = vtk.vtkActor()
        # self.__level_child_cart_actor.SetMapper(self.__level_child_cart_mapper)
        # self.__level_child_cart_actor.GetProperty().SetColor(vtk.vtkNamedColors().GetColor3d('white'))
        # self.AddPart(self.__level_child_cart_actor)

        # Add rack representation for level
        self.__rack_points = vtk.vtkPoints()
        self.__rack_line_indices = vtk.vtkCellArray()
        for di, d in enumerate([[0, self.stack_depths[0] * PALLET_SLOT.x], [AISLE.x, AISLE.x + self.stack_depths[1] * PALLET_SLOT.x]]):
            self.__rack_points.InsertNextPoint(
                *(self.base_location +                                              # base location
                  np.array([PALLET_SLOT.x*0.5, -PALLET_SLOT.y*0.5, PALLET.z+(PALLET_SLOT.z-PALLET.z)*0.5])+ # add z offset (ceiling of level)
                  d[0]*self.stack_unit_vectors[di]))                                # offset for 'depth'
            self.__rack_points.InsertNextPoint(
                *(self.base_location +                                              # base location
                  np.array([PALLET_SLOT.x*0.5, -PALLET_SLOT.y*0.5, PALLET.z+(PALLET_SLOT.z-PALLET.z)*0.5])+ # add z offset (ceiling of level)
                  (self.width+1)*self.width_unit_vector*PALLET_SLOT.y +             # offset for 'width'
                  d[0]*self.stack_unit_vectors[di]))                                # offset for 'depth'
            self.__rack_line_indices.InsertNextCell(2)
            self.__rack_line_indices.InsertCellPoint(self.__rack_points.GetNumberOfPoints()-2)
            self.__rack_line_indices.InsertCellPoint(self.__rack_points.GetNumberOfPoints()-1)
            self.__rack_points.InsertNextPoint(
                *(self.base_location +                                              # base location
                  np.array([PALLET_SLOT.x*0.5, -PALLET_SLOT.y*0.5, PALLET.z+(PALLET_SLOT.z-PALLET.z)*0.5])+ # add z offset (ceiling of level)
                  d[1]*self.stack_unit_vectors[di]))                                # offset for 'depth'
            self.__rack_points.InsertNextPoint(
                *(self.base_location +                                              # base location
                  np.array([PALLET_SLOT.x*0.5, -PALLET_SLOT.y*0.5, PALLET.z+(PALLET_SLOT.z-PALLET.z)*0.5])+ # add z offset (ceiling of level)
                  (self.width+1)*self.width_unit_vector*PALLET_SLOT.y +                 # offset for 'width'
                  d[1]*self.stack_unit_vectors[di]))                                # offset for 'depth'
            self.__rack_line_indices.InsertNextCell(2)
            self.__rack_line_indices.InsertCellPoint(self.__rack_points.GetNumberOfPoints()-2)
            self.__rack_line_indices.InsertCellPoint(self.__rack_points.GetNumberOfPoints()-1)
            for w in [0, self.width+1]: # range(self.width+1):
                self.__rack_points.InsertNextPoint(
                    *(self.base_location +                                              # base location
                      np.array([PALLET_SLOT.x*0.5, -PALLET_SLOT.y*0.5, -(PALLET_SLOT.z-PALLET.z)*0.5]) +            # add z offset (ceiling of level)
                      w*self.width_unit_vector*PALLET_SLOT.y +                          # offset for 'width'
                      d[0]*self.stack_unit_vectors[di]))                                # offset for 'depth'
                self.__rack_points.InsertNextPoint(
                    *(self.base_location +                                              # base location
                      np.array([PALLET_SLOT.x*0.5, -PALLET_SLOT.y*0.5, PALLET.z+(PALLET_SLOT.z-PALLET.z)*0.5])+ # add z offset (ceiling of level)
                      w*self.width_unit_vector*PALLET_SLOT.y +                          # offset for 'width'
                      d[0]*self.stack_unit_vectors[di]))                                # offset for 'depth'
                self.__rack_points.InsertNextPoint(
                    *(self.base_location +                                              # base location
                      np.array([PALLET_SLOT.x*0.5, -PALLET_SLOT.y*0.5, PALLET.z+(PALLET_SLOT.z-PALLET.z)*0.5])+ # add z offset (ceiling of level)
                      w*self.width_unit_vector*PALLET_SLOT.y +                          # offset for 'width'
                      d[1]*self.stack_unit_vectors[di]))                                # offset for 'depth'
                self.__rack_points.InsertNextPoint(
                    *(self.base_location +                                              # base location
                      np.array([PALLET_SLOT.x*0.5, -PALLET_SLOT.y*0.5, -(PALLET_SLOT.z-PALLET.z)*0.5])+             # add z offset (ceiling of level)
                      w*self.width_unit_vector*PALLET_SLOT.y +                          # offset for 'width'
                      d[1]*self.stack_unit_vectors[di]))                                # offset for 'depth'
                self.__rack_line_indices.InsertNextCell(4)
                self.__rack_line_indices.InsertCellPoint(self.__rack_points.GetNumberOfPoints()-4)
                self.__rack_line_indices.InsertCellPoint(self.__rack_points.GetNumberOfPoints()-3)
                self.__rack_line_indices.InsertCellPoint(self.__rack_points.GetNumberOfPoints()-2)
                self.__rack_line_indices.InsertCellPoint(self.__rack_points.GetNumberOfPoints()-1)

        self.__rack_polydata = vtk.vtkPolyData()
        self.__rack_polydata.SetPoints(self.__rack_points)
        self.__rack_polydata.SetLines(self.__rack_line_indices)
        self.__rack_mapper = vtk.vtkPolyDataMapper()
        self.__rack_mapper.SetInputData(self.__rack_polydata)
        self.__rack_actor = vtk.vtkActor()
        self.__rack_actor.SetMapper(self.__rack_mapper)
        self.__rack_actor.GetProperty().SetColor([0.5, 0.5, 0.5]);
        self.__rack_actor.GetProperty().SetOpacity(0.2);
        self.__rack_actor.GetProperty().SetLineWidth(2);
        self.AddPart(self.__rack_actor)

        self.moveTo([float(i) for i in self.base_location])
        self.initialized = True
        return 1

    def locationFromBuffer(self, time):
        # pdb.set_trace()
        return [self.__databuffer.buffered_keyframes.loc_x(time),
                self.__databuffer.buffered_keyframes.loc_y(time),
                self.__databuffer.buffered_keyframes.loc_z(time)]

    def moveTo(self, location=None, time=datetime.datetime.now()):
        # calculate position from keyframes if a location is not provided
        self.cart_location = location if location else self.locationFromBuffer(time)
        # if this position is invalid, use the base position
        self.cart_location = self.cart_location if self.cart_location and self.cart_location[0] else self.base_location
        self.__level_parent_cart_actor.SetPosition(*self.cart_location)
        # parent cart should be at
        # ((cart_location - base_location) Projected onto width_unit_vector) + base_location
        # self.__level_parent_cart_actor.SetPosition()

    def reload(self, callback=None, callback_args={}):
        self.__databuffer.pause()
        self.__databuffer.update()
        self.__databuffer.resume()

    def update(self, obj, event, time=datetime.datetime.now()):
        self.moveTo(time=time)


class LevelBuffer(DataBuffer):
    """
    LevelBuffer

    Run a recurring threaded process to keep an accurate list of level movement for the buffered dataset.

    Used as a base class for a dataframe buffer and eventually a streaming data buffer
    """

    def __init__(self):
        super().__init__()
        self.name='LEVEL BUFFER'
        self.buffered_keyframes = KeyframeManager() # keyframe manager of keyframes in warehouse during buffered time


class LevelDataFrameBuffer(LevelBuffer):

    """
    LevelDataFrameBuffer

    Run a recurring threaded process to keep an accurate list of level movement for the buffered dataset.

    This class contains processes for explicit data frame data format handling. If the data format being intepretted by the data buffer should ever change, a new class should be constructed extending the parent class to reflect those changes.
    """

    def __init__(self, data, playback_manager, name=None):
        super().__init__()
        if name: self.name = name
        self.dataframe = data
        self.pm = playback_manager
        self.__bufered_dataframe = None

    def update(self):
        if self.dataframe is None: return -1
        elif self.pm is None: return -1

        __update_start_time = datetime.datetime.now()

        buffer_start = self.buffer_start
        buffer_end = self.buffer_end

        try:
            self.__buffered_dataframe = self.dataframe[(self.dataframe['time'] < buffer_end) & \
                                                       (self.dataframe['time'] > buffer_start)]
            if len(self.__buffered_dataframe) == 0:
                self.__buffered_dataframe = self.dataframe.ix[[0]] \
                                            if self.dataframe.iloc[0]['time'] > buffer_start else \
                                            self.dataframe.ix[[len(self.dataframe)-1]]
            self.buffered_keyframes = KeyframeManager(dataframe=self.__buffered_dataframe)
        except Exception as e:
            logging.warning('[{}] Error during databuffer update.\n{}'.format(self.name, str(e)))

        __update_duration = datetime.datetime.now() - __update_start_time

        logging.debug('[{}] Buffering data from {} to {}'.format(self.name, buffer_start, buffer_end))
        logging.debug('[{}] Filtered a {} row dataframe down to {} rows. ({})'.format(self.name,  \
            len(self.dataframe), \
            len(self.__buffered_dataframe), \
            str(__update_duration) ))

        if __update_duration > self.update_interval:
            logging.warning('[{}] Update time exceeded update interval. {}/{}'.format(self.name, __update_duration, self.update_interval))

        return 1
