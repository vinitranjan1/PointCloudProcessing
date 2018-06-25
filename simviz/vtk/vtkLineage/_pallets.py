import vtk, logging, threading, datetime, tqdm, numpy as np, pandas as pd

from ._settings import *
from ._animation import *
from ._helpers import *
from ._databuffer import *

class Pallet():

    """
    Pallet

    Will contain the necessary information to be represented by the pallet mapper, providing a more readable description of each Pallet for manipulation in the pallet mapper.
    """

    def __init__(self, PID=None, SKU=None, timestamps=[], start=None, end=None):
        self._PID = PID
        self._SKU = SKU
        self.__km = KeyframeManager(timestamps=timestamps, start=start, end=end)

    def inUse(self, time=None):
        """
        Return True if the time provided is during the time for which the pallet is within the warehouse. This may be stationarily within the rackstore or actively migrating throughout the warehouse.
        """
        return time >= self.timeFirst and time < self.timeLast

    def getLocationAt(self, time=None):
        """
        A quality-of-life function to return an array of x, y, z coordinates instead of having to compile this list and handle edge cases separately.
        """
        return [self.loc_x(time), self.loc_y(time), self.loc_z(time)] if self.inUse(time) else [float('nan'), float('nan'), float('nan')]

    def __getattr__(self, attr):
        """
        The __getattr__ method is overridden to allow properties to be accessed from the keyframe manager when those properties are not explicitly given

        For example, to get a pallet's location along the x axis at a given time, one may call self.loc_x(time), returning the keyframe manager's function for "loc_x"
        """
        # if the attribute isn't found in the pallet properties, see if it's been assigned as a keyframed property
        return self.__km.__getattr__(attr)

    @property
    def pid(self):
        return self._PID

    @property
    def sku(self):
        return self._SKU

    def __str__(self):
        return 'Pallet (PID: {}, SKU: {})'.format(self.pid, self.sku)


class PalletsActor(vtk.vtkActor):

    """
    PalletsActor

    A wrapper for the vtk.vtkActor class specificially in the context of defining a Pallet Mapper object to simplify scene construction.

    Creates its own mapper object to map a data stream to a Glyph3DMapper
    """

    def __init__(self, playback_manager=None, pallet_data=None):
        super().__init__()
        self._mapper = PalletsMapper(playback_manager=playback_manager)
        self.SetMapper(self._mapper)
        self.bindPalletBuffer(PalletsDataFrameBuffer(pallet_data, playback_manager))
        # self.ClipToPalletsAt(120.0)

        self.GetProperty().SetDiffuse(1)
        self.GetProperty().SetAmbient(0.05)
        self.GetProperty().SetSpecular(0)
        self.GetProperty().SetSpecularPower(0)

    def reload(self, time=datetime.datetime.now()):
        """
        Reloads buffered data at a specified time and pass any calls to the actor class to the underlying mapper class
        """
        self._mapper.reload(time)

    def update(self, obj, event, time=datetime.datetime.now()):
        """
        Updates the active dataset to represent a specific time. Subsequently update underlying mapper class

        Since this does not issue a complete reloading of data, data which is not actively being updated will not get triggered with an update. Only use this if you believe the active pallets in the data buffer represents all pallets that need to be updated. Otherwise, issue a call to PalletsActor.reload() instead.
        """
        self._mapper.update(obj, event, time)

    def setColorRepresentation(self, name):
        """
        Pass any calls to the actor class to the underlying mapper class
        """
        self._mapper.setColorRepresentation(name)

    def bindPalletBuffer(self, pallet_buffer):
        """
        Pass any calls to the actor class to the underlying mapper class
        """
        self._mapper.bindPalletBuffer(pallet_buffer)

    def ClipToPalletsAt(self, z):
        """
        Set clip planes (current a single xy plane) to cull the mapper geometry
        """
        #
        #  NOTE: THIS CAUSES A VTK ERROR DUE TO IMPROPER SHADER CONSTRUCTION
        #        An error report has been reported to the vtk development issues page:
        #        https://gitlab.kitware.com/vtk/vtk/issues/16908
        #

        # self.ClearAllClippingPlanes()
        plane_lower = vtk.vtkPlane()
        plane_lower.SetNormal(0, 0, 1)
        plane_lower.SetOrigin(0, 0, z)
        self._mapper.AddClippingPlane(plane_lower)
        plane_upper = vtk.vtkPlane()
        plane_upper.SetNormal(0, 0, -1)
        plane_upper.SetOrigin(0, 0, z + PALLET_SLOT.height)
        self._mapper.AddClippingPlane(plane_upper)

    def ClearAllClippingPlanes(self):
        self._mapper.RemoveAllClippingPlanes()

    def addPallet(self, pid, sku, keyframeData):
        return self._mapper.initializePallet(pid, sku, keyframeData)


class PalletsMapper(vtk.vtkGlyph3DMapper):

    """
    PalletsMapper

    Maps an array of locations and skus/statuses to a 'point-cloud' type display or pallets, using pallet geometry (the 'Glyph') to render each pallet. This seemingly roundabout method of rendering pallets improves performance drastically because the single pallet geometry is referenced for the entire point array.

    Additional attributes are defined to describe pallets and abstract addition of new pallets and reuse of the points as pallets by pallet ID are needed or not.
    """

    # eventually this should have a low frequency thread for buffering pallets that will soon need to be actively moving so that it doesn't need to happen on a per-frame basis, culling the vast majority of pallets from the update loop

    def __init__(self, playback_manager=None, max_pallet_count=20000):
        vtk.vtkGlyph3DMapper.__init__(self)

        # playback manager
        self.__pm = playback_manager

        # data
        self.__databuffer = None # Needs a PalletBuffer bound to it

        # pallet information
        self._max_pallet_count = max_pallet_count
        self._pid_to_idx = {}
        self._pallet_glyphs = [None] * self._max_pallet_count
        self.__idxs_available = [i for i in range(self._max_pallet_count)]
        self.__update_all = False

        self.__sku_color_res = 6 # testing
        # self.__sku_color_res = 10 ** 8 # real

        # vtk data
        # behind-the-scenes vtk stuff
        # LookupTable for Pallet Coloring
        self._lut = vtk.vtkLookupTable()
        # Data container for pallet locations and colors
        self.__locations = vtk.vtkPoints()
        self.__locations.SetNumberOfPoints(self._max_pallet_count)
        self.__skus = vtk.vtkFloatArray()
        self.__skus.SetNumberOfValues(self._max_pallet_count)
        self.__skus.SetLookupTable(self._lut)
        self.__action = vtk.vtkFloatArray()
        self.__action.SetNumberOfValues(self._max_pallet_count)
        self.__action.SetLookupTable(self._lut)
        self.__state = vtk.vtkFloatArray()
        self.__state.SetNumberOfValues(self._max_pallet_count)
        self.__state.SetLookupTable(self._lut)
        self.__polydata = vtk.vtkPolyData()
        self.__polydata.SetPoints(self.__locations)
        self.__polydata.GetPointData().SetScalars(self.__skus)

        # Geometry to use as Glyph
        self.__source = vtk.vtkCubeSource()
        self.__source.SetBounds(-0.5 * PALLET.x, 0.5 * PALLET.x,
                                -0.5 * PALLET.y, 0.5 * PALLET.y,
                                 0.0,            1.0 * PALLET.z )
        # Link mapper to data
        self.SetSourceConnection(self.__source.GetOutputPort())
        self.SetInputData(self.__polydata)
        self.SetScaleModeToNoDataScaling()

        self.initializeLookupTable(self.__skus)
        self.resetPallets()

    def setColorRepresentation(self, name):
        """
        Choose what information the color of the glyphs should represent

        Args:
            name: string of parameter to be represented ('sku', 'action', or 'state')
        """
        if name is 'sku': self.__polydata.GetPointData().SetScalars(self.__skus)
        elif name is 'action': self.__polydata.GetPointData().SetScalars(self.__action)
        elif name is 'state': self.__polydata.GetPointData().SetScalars(self.__state)

    def bindPalletBuffer(self, pallet_buffer):
        """
        Binds a data buffer to the mapper to stream data from

        Args:
            pallet_buffer: The buffer to be bound
        """
        self.__databuffer = pallet_buffer

    def initializePallet(self, pallet=None, pid=None, sku=None, keyframes=None, start=None, end=None, time=datetime.datetime.now()):
        """
        Initialize a pallets data for internal storage in the _pallet_glyphs object and representation in the mapper

        Args:
            pallet:    A Pallet object to be stored
            time:      The time to initialize the pallet object at

            (only used if pallet kwarg is not provided)
            pid:       pid of the pallet object to be created
            sku:       sku of the pallet object to be created
            keyframes: The information to be passed to a keyframe manager to generate interpolation functions
            start:     The starting timestamp of the pallet's use
            end:       The ending timestamp of the pallet's use

        Returns:
            The numeric key of the object in the internal _pallet_glyphs dictionary or -1 if there was an error inserting it into the mapper.
        """
        try:
            idx = self.__idxs_available.pop(0)
            self._pallet_glyphs[idx] = pallet if pallet else Pallet(pid, sku, keyframes, start, end)
            self._pid_to_idx[self._pallet_glyphs[idx].pid] = idx
            self.updatePallet(idx, time)
            return idx
        # This error gets thrown if there are no indexes available for representing this pallet
        except IndexError as e:
            logging.warning('Failed to load pallet {}'.format(pid))
            return -1

    def updatePallet(self, idx, time=datetime.datetime.now()):
        """
        Update a pallet by index in the _pallet_glyphs internal dictionary to represent that pallet at a specific time.

        Args:
            idx:  The index in the internal _pallet_glyphs dictionary to update
            time: The time to update the pallet to
        """
        self.__locations.InsertPoint(idx, *self._pallet_glyphs[idx].getLocationAt(time))
        self.__skus.InsertValue(idx, self._skuToScalar(self._pallet_glyphs[idx].sku))
        self.__action.InsertValue(idx, self._actionToScalar(self._pallet_glyphs[idx].action(time)))
        self.__state.InsertValue(idx, self._stateToScalar(self._pallet_glyphs[idx].state(time)))

    def resetPallets(self):
        """
        Resets all pallets to a default value
        """
        for idx in range(self._max_pallet_count):
            self.resetPallet(idx)

    def resetPallet(self, idx):
        """
        Resets a single pallet by index in the internal _pallet_glyphs dictionary to a default value
        """
        self.__locations.InsertPoint(idx, float('nan'), float('nan'), float('nan'))
        self.__skus.InsertValue(idx, float('nan'))

    def releasePallets(self):
        """
        Releases all pallets
        """
        for idx in range(self._max_pallet_count):
            if self._pallet_glyphs[idx] is not None:
                self.releasePallet(idx)

    def releasePallet(self, idx):
        """
        Releases a pallet by index in the internal _pallet_glyphs dictionary

        Deletes the pallet object contained at the given index, resets the glyph that was representing it to a default value and adds that index back to a list of available indices.
        """
        if self._pallet_glyphs[idx]:           # Remove mapping
            del self._pid_to_idx[self._pallet_glyphs[idx].pid]
            self._pallet_glyphs[idx] = None    # Remove object from data list
            self.resetPallet(idx)              # Reset Glyph Representation
            self.__idxs_available.append(idx)  # Add to list of available glyph points

    def reload(self, time=None):
        """
        Pauses the databuffer and reloads all pallets in the warehouse at a given time, whether they currently need to be actively updated or not. This is useful for initializing the warehouse (when all pallets need to be updated regardless of whether they're being actively used), or when the playback of the visualization jumps outside the buffered time range.
        """

        logging.info("[PALLETS] Reloading pallet stores at current timestamp.")
        self.__databuffer.pause()

        self.releasePallets()
        if self.__databuffer:
            self.__databuffer.update()
            stores = self.__databuffer.getStoredDataFrame()
            load_at_time = time if time else self.__databuffer.pm.time
            for pid, rowdata in tqdm.tqdm(stores.iterrows(), desc='Loading Timestamp', unit='pallets', total=len(stores)):
                self.initializePallet(pid=pid,
                                      sku=rowdata['sku'],
                                      keyframes=rowdata['keyframes'],
                                      start=rowdata['activity start'],
                                      end=rowdata['activity end'],
                                      time=load_at_time)

            self.__locations.Modified()
            self.__skus.Modified()

        self.__databuffer.resume()

    def update(self, obj, event, time=datetime.datetime.now()):
        """
        update

        This function is the central backbone of the frame-wise updating of the pallet object. To make everything run smoothly, as much as possible is computed outside of this function and minimizing the amount of pallets that need to be updated is a priority.

        To accommodate this, a background thread is constantly running to keep a running buffer of pallets that need to be actively considered. Likewise, the buffer creates pallet objects in the background to avoid the added computation of interpretting keyframe dictionaries and producing functional representations of the pallet properties. This mitigates the amount of computation needed during the update call immensely.
        """

        for pid, data in self.__databuffer:
            # TODO: There may be issues loading pallets in edge cases where the
            # pallet is not found in the buffer of upcoming pallets but is stored
            # in the active pallets dataframe. I haven't encountered this event
            # yet, but it's a possible unhandled failure point.

            # if an index is assigned for this pallet, update it
            if self.pidHasIndex(pid):
                # if it's still in use, update pallet data
                if data['activity end'] >= time: self.updatePallet(self._pid_to_idx[pid], time)
                # otherwise release it
                else: self.releasePallet(self._pid_to_idx[pid])

            # if no index is assigned yet and it's in the pallet buffer
            elif self.__databuffer.hasUpcomingID(pid):
                # load it from buffered, preconstructed pallet objects
                self.initializePallet(pallet=self.__databuffer.upcomingPalletByID(pid), time=time)

        self.__locations.Modified()
        self.__skus.Modified()

    def initializeLookupTable(self, scalars_array):
        """
        helper function to initialize a color table for color representation of scalar values
        """

        self._lut.SetNumberOfColors(128)
        self._lut.SetTableRange([0, 1])
        self._lut.SetRange([0, 1])
        self._lut.SetRampToLinear()

        self._lut.SetHueRange(0.667, 0.0)  # blue to red gradient mapping
        # self._lut.SetHueRange(0.0, 1.0)  # rainbow!

        self._lut.SetSaturationRange(0.5, 0.5)
        self._lut.SetValueRange(0.95, 0.95)
        self._lut.SetNanColor(0.0, 0.0, 0.0, 0.0)

        self._lut.Build()

    def getIndex(self, pid):
        """
        Get an index by a pallet id
        """
        return self._pid_to_idx[pid] if pid in self._pid_to_idx else None

    def pidHasIndex(self, pid):
        """
        Check whether a pallet with a given pallet id is currently stored in the glyph mapper
        """
        return pid in self._pid_to_idx

    def _skuToScalar(self, sku):
        """
        Helper function for converting skus to scalar values
        """
        # For some reason, vtkIntArray isn't working for coloring by sku, instead I have to convert to a float of range [0,1]
        return (float(sku if sku.isnumeric() else hash(sku)) % (self.__sku_color_res + 1)) / self.__sku_color_res

    def _actionToScalar(self, action):
        """
        Helper function for converting action strings to scalar values
        """
        return ACTION_LOOKUP[action] / len(ACTION_LOOKUP) if action in ACTION_LOOKUP else -1

    def _stateToScalar(self, state):
        """
        Helper function for converting state strings to scalar values
        """
        return STATE_LOOKUP[state] / len(STATE_LOOKUP) if state in STATE_LOOKUP else -1


class PalletsBuffer(DataBuffer):

    """
    Pallets Buffer

    Run a recurring threaded process to keep an accurate list of pallets that need to be actively updated.

    Used as a base class for a dataframe buffer and eventually a streaming data buffer
    """

    def __init__(self):
        super().__init__()
        self.name='PALLETS BUFFER'
        self.stored_pallet_data = None # pallets in warehouse during buffered time
        self.active_pallet_data = None # pallets needing active updates during the buffered time
        self._stored_pallet_pids = []
        self._active_pallet_pids = []
        self.upcoming_pallets = {} # {pid: pallet object}, allows for initialization of upcoming pallets in a background thread instead of in the glyph update call

    def hasPalletsUpcoming(self):
        """
        Returns True if the buffered data contains new pallets that will require initialization
        """
        return len(self.upcoming_pallets) > 0

    def hasUpcomingID(self, pid):
        """
        Returns True if a specific pallet id is in a dictionary of upcoming pallets
        """
        return pid in self.upcoming_pallets

    def upcomingPalletByID(self, pid):
        """
        Returns a specific upcoming pallet object by its pallet id
        """
        return self.upcoming_pallets.pop(pid)

    def getStoredDataFrame(self):
        """
        Returns A dataframe containing information for all pallets currently in the warehouse
        """
        return self.stored_pallet_data

    def getStoredPIDs(self):
        """
        Returns a list of all pallet ids for pallets currently stored in the warehouse
        """
        return self._stored_pallet_pids

    def getActiveDataFrame(self):
        """
        Returns a dataframe containing information for all pallets currently actively migrating throughout the warehouse
        """
        return self.active_pallet_data

    def getActivePIDs(self):
        """
        Returns a list of all pallet ids for pallets currently actively migrating throughout the warheouse
        """
        return self._active_pallet_pids

    def __iter__(self):
        """
        Allows for calling buffer in a loop to iterate through active dataframe as a shorthand for iterating through active pallet data rows.

        "for pid, data in PalletsBuffer.getActiveDataFrame().iterrows():"
        ... becomes ...
        "for pid, data in PalletsBuffer:"

        -just makes it easier to read without all the extra helper functions
        """
        return self.active_pallet_data.iterrows()


class PalletsDataFrameBuffer(PalletsBuffer):

    """
    PalletsDataFrameBuffer

    Inherits from PalletsBuffer to take a very large dataframe which can't be reliably processed on a per-frame basis and cull it down to only rows that need to be considered for active updates
    """

    def __init__(self, dataframe=None, playbackManager=None):
        super().__init__()
        self.dataframe = dataframe
        self.pm = playbackManager
        self.start()

    def setDataFrame(self, dataframe):
        """
        Set the source dataframe from which the data will be culled
        """
        self.dataframe = dataframe
        self.start()

    def getDataFrame(self):
        """
        Returns the source data dataframe
        """
        return self.dataframe

    def setPlaybackManager(self, playbackManager):
        """
        Sets the playback manager to govern the timespan to buffer
        """
        self.pm = playbackManager
        self.start()

    def updateStoredDataFrame(self, buffer_start=None, buffer_end=None):
        """
        Updates and returns the dataframe of all pallets currently stored within the warehouse
        """
        if not buffer_start: buffer_start = self.buffer_start
        if not buffer_end: buffer_end = self.buffer_end

        # filter by pid's that are in the warehouse
        # TODO: This can be made faster by quickly iterating through rows in a binary tree type search
        #       to first slice the array to a more manageable size, assuming the dataframe is already sorted
        # TODO: Only compute on difference between last update and append to last update
        self.stored_pallet_data = self.dataframe[(self.dataframe['activity start'] < buffer_end) & \
                                                 (self.dataframe['activity end'] > buffer_start)]
        self._stored_pallet_pids = self.stored_pallet_data.index.values

        return self.stored_pallet_data

    def updateActiveDataFrame(self, buffer_start=None, buffer_end=None):
        """
        Updates and returns the dataframe containing all pallets currently actively migrating throughout the warehouse
        """
        if not buffer_start: buffer_start = self.buffer_start
        if not buffer_end: buffer_end = self.buffer_end

        active_idxs = np.zeros(len(self.stored_pallet_data), dtype=bool)
        for idx, row in enumerate(self.stored_pallet_data.iterrows()) :
            pid, data = row # tuple unpack row data

            # TODO: Like above, this could be improved for pallets which have many windows of activity
            #       Since pallets typically do not move more than a handful of times, it's not a priority
            for window in data['activity windows']:
                # if the pallet has a window which will be active during the buffered timespan, \
                # include it in active dataframe

                if ('start' not in window or window['start'] < buffer_end) and \
                   ('end' not in window or window['end'] > buffer_start):

                    # mark this index as active during the buffered timespan
                    active_idxs[idx] = True

                    # if the pallet is yet to be actively used, add it to a dictionary of upcoming pallets
                    # to compute keyframed values from data ahead of use
                    if ('start' not in window or window['start'] > self.time) and pid not in self.upcoming_pallets:
                        self.upcoming_pallets[pid] = Pallet(PID=pid,
                                                            SKU=data['sku'],
                                                            timestamps=data['keyframes'],
                                                            start=data['activity start'],
                                                            end=data['activity end'])

                    # no need to continue looping through pallet if we already know it has an active window
                    break

        # apply filtering list to limit to only those that are in an active window during the buffering time
        self.active_pallet_data = self.stored_pallet_data[active_idxs]
        self._active_pallet_pids = self.active_pallet_data.index.values
        return self.active_pallet_data

    def update(self):
        """
        Update the internal dataframes of culled data
        """

        if self.dataframe is None: return -1
        elif self.pm is None: return -1

        if self.buffer_start and self.buffer_end and (self.time < self.buffer_start or self.time > self.buffer_end):
            pass # eventually have a trigger that's called to rebuild entire pallet rackstores if pulledi outside of buffered dataset

        __update_start_time = datetime.datetime.now()

        buffer_start = self.buffer_start
        buffer_end = self.buffer_end

        try:
            self.updateStoredDataFrame(buffer_start, buffer_end)
            self.updateActiveDataFrame(buffer_start, buffer_end)
        except Exception as e:
            logging.warning('[{}] Error during databuffer update.\n{}'.format(self.name, str(e)))

        __update_duration = datetime.datetime.now() - __update_start_time

        logging.debug('[{}] Buffering data from {} to {}'.format(self.name, buffer_start, buffer_end))
        logging.debug('[{}] Filtered {} pallets in dataframe to {} in warehouse to {} in buffer. ({})'.format(self.name,  \
            len(self.dataframe), \
            len(self.stored_pallet_data), \
            len(self.active_pallet_data), \
            str(__update_duration) ))

        if __update_duration > self.update_interval:
            logging.warning('[{}] Update time exceeded update interval. {}/{}'.format(self.name, __update_duration, self.update_interval))

        return 1
