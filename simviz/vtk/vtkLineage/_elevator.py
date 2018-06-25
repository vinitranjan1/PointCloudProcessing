import vtk

from ._databuffer import *
from ._animation import *
from ._helpers import *
from ._settings import *
import pdb


class ElevatorActor(vtk.vtkPropAssembly, vtkLineageSystem):

    """
    BayDoorActor

    Extends vtk.vtkPropAssembly to build a 3D representation of an elevator from minimal information
    """

    def __init__(self, playback_manager=None, data=None, name=None, **kargs):

        super().__init__()
        self.name = name
        self.initialized = False
        self.lift_location = [0, 0, 0]
        self.base_location = [0, 0, 0]
        if kargs: self.initialize(**kargs)
        self.__databuffer = ElevatorDataFrameBuffer(data, playback_manager, name=name+' BUFFER')
        self.__databuffer.start()
        self.base_location

    def initialize(self, start=None, end=None):
        if not start or not end or start == end: return -1

        # update base location
        self.base_location = [float(i) for i in start]

        # path of elevators's travel
        self.__path_line = vtk.vtkLineSource()
        self.__path_line.SetPoint1([float(i) for i in start])
        self.__path_line.SetPoint2([float(i) for i in end])
        self.__path_tubefilter = vtk.vtkTubeFilter()
        self.__path_tubefilter.SetInputConnection(self.__path_line.GetOutputPort())
        self.__path_tubefilter.SetRadius(6.0)
        self.__path_tubefilter.SetNumberOfSides(6)
        self.__path_tubefilter.CappingOn()
        self.__path_mapper = vtk.vtkPolyDataMapper()
        self.__path_mapper.SetInputConnection(self.__path_tubefilter.GetOutputPort())
        self.__path_actor = vtk.vtkActor()
        self.__path_actor.SetMapper(self.__path_mapper)
        self.AddPart(self.__path_actor)

        # elevator position
        self.__lift_source = vtk.vtkCubeSource()
        self.__lift_source.SetBounds(-0.5 * PALLET_SLOT.x, 0.5 * PALLET_SLOT.x,
                                     -0.5 * PALLET_SLOT.y, 0.5 * PALLET_SLOT.y,
                                     -0.1 * PALLET_SLOT.z, 0.1 * PALLET_SLOT.z)
        self.__lift_mapper = vtk.vtkPolyDataMapper()
        self.__lift_mapper.SetInputConnection(self.__lift_source.GetOutputPort())
        self.__lift_actor = vtk.vtkActor()
        self.__lift_actor.SetMapper(self.__lift_mapper)
        self.__lift_actor.GetProperty().SetColor(vtk.vtkNamedColors().GetColor3d('white'))
        self.moveLift([float(i) for i in start])
        self.AddPart(self.__lift_actor)

        self.initialized = True
        return 1

    def locationFromBuffer(self, time):
        return [self.__databuffer.buffered_keyframes.loc_x(time),
                self.__databuffer.buffered_keyframes.loc_y(time),
                self.__databuffer.buffered_keyframes.loc_z(time)]

    def moveLift(self, location=None, time=datetime.datetime.now()):
        # calculate position from keyframes if a location is not provided
        self.lift_location = location if location else self.locationFromBuffer(time)
        # if this position is invalid, use the base position
        self.lift_location = self.lift_location if self.lift_location and self.lift_location[0] else self.base_location
        self.__lift_actor.SetPosition(*self.lift_location)

    def reload(self, callback=None, callback_args={}):
        self.__databuffer.pause()
        self.__databuffer.update()
        self.__databuffer.resume()

    def update(self, obj, event, time=datetime.datetime.now()):
        self.moveLift(time=time)


class ElevatorBuffer(DataBuffer):
    """
    Elevator Buffer

    Run a recurring threaded process to keep an accurate list of elevator movement for the buffered dataset.

    Used as a base class for a dataframe buffer and eventually a streaming data buffer
    """

    def __init__(self):
        super().__init__()
        self.name='ELEVATOR BUFFER'
        self.buffered_keyframes = KeyframeManager() # keyframe manager of keyframes in warehouse during buffered time


class ElevatorDataFrameBuffer(ElevatorBuffer):

    """
    ElevatorDataFrameBuffer

    Run a recurring threaded process to keep an accurate list of elevator movement for the buffered dataset.

    This class contains processes for explicit data frame data format handling. If the data format being intepretted by the data buffer should ever change, a new class should be constructed extending the parent class to reflect those changes. 
    """

    def __init__(self, data, playback_manager, name=None):
        super().__init__()
        if name: self.name = name
        self.dataframe = data
        self.pm = playback_manager
        self.__bufered_dataframe = None

    def update(self):
        """
        The function called each time the DataBuffer thread makes a call.
        """

        if self.dataframe is None: return -1
        elif self.pm is None: return -1

        __update_start_time = datetime.datetime.now()

        buffer_start = self.buffer_start
        buffer_end = self.buffer_end

        try:
            self.__buffered_dataframe = self.dataframe[((self.dataframe['time']) < buffer_end) & ((self.dataframe['time']) > buffer_start)]
            if len(self.__buffered_dataframe) == 0:
                self.__buffered_dataframe = self.dataframe.ix[[0]] \
                                            if self.dataframe.iloc[0]['time'] > buffer_start else \
                                            self.dataframe.ix[[len(self.dataframe)-1]]
            self.buffered_keyframes = KeyframeManager(dataframe=self.__buffered_dataframe)
            # pdb.set_trace()
        except Exception as e:
            logging.warning('[{}] Error during databuffer update.\n{}'.format(self.name, str(e)))

        __update_duration = datetime.datetime.now() - __update_start_time

        logging.debug('[{}] Buffering data from {} to {}'.format(self.name, buffer_start, buffer_end))
        # pdb.set_trace()
        logging.debug('[{}] Filtered a {} row dataframe down to {} rows. ({})'.format(self.name,  \
            len(self.dataframe), \
            len(self.__buffered_dataframe), \
            str(__update_duration) ))

        if __update_duration > self.update_interval:
            logging.warning('[{}] Update time exceeded update interval. {}/{}'.format(self.name, __update_duration, self.update_interval))

        return 1
