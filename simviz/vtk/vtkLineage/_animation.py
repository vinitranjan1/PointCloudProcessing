import logging, datetime, bisect, numpy as np, pandas as pd
from scipy import interpolate

from ._helpers import *

import vtk

class KeyframeManager():

    """
    KeyframeManager

    This class allows for a container for keyframed properties such that properties can be evaluated at a time and interpolated between provided keyframes. For example, pallet location could be accessed by pallet.location(time) and the location will interpolate between location keyframes.
    """


    class TimeInterpWrapper():

        """
        TimeInterpWrapper

        A helper class for wrapping interpolation fucnctions with added functionality for handling time by converting to milliseconds since an initialization time. This is used by passing a function from scipy's interpolation module, initialized with the x and y values to interpolate as well as an initial time of reference. Since scipy does not allow times, the x values have already been converted to floats using milliseconds past a basetime. This same basetime is passed to the function. This allows for the function to be called with a time and automatically internally converted to milliseconds since its stored initial time.
        """

        def __init__(self, func, basetime=None):
            self.basetime = basetime
            self.func = func

        def __call__(self, time=None):
            try:
                return self.func(TimeDeltaToMilliseconds(time-self.basetime))
            except TypeError:
                return self.func


    def __init__(self, keyframes=None, timestamps=None, dataframe=None, start=None, end=None):
        self.__interp_props = {} # initialized in helper functions below
        self.timeFirst = start
        self.timeLast = end

        if keyframes is not None: pass
        elif timestamps is not None: self._initializeFromTimestamps(timestamps)
        elif dataframe is not None: self._initializeFromDataFrame(dataframe)

    def __interp_props_default(self, time):
        """
        Provides a function to return for properties which have not been initialized in __interp_props
        """
        return None

    def _initializeFromKeyframes(self, kfs):
        """
        Currently empty function.
        TODO: Allow for keyframed properties to be passed instead of timestamped properties.
        """
        pass

    def _initializeFromTimestamps(self, tss):
        """
        Takes a list of dictionaries with identical set of keys, including the key 'time'. Each dictionary represents a timestamp of all of those properties at the given time. This dictionary is parsed to build functions which can be called with a given time to interpolate the value of that property at an arbitrary time.

        Args:
            tss: A timestamp series from which the interpolation functions for all keyframes will be constructed
        """

        __basetime = tss[0]['time']

        if not self.timeFirst: self.timeFirst = timestamps[0]['time']
        if not self.timeLast: self.timeLast = timestamps[-1]['time']

        prop_keyframes = {} # { property: { x: [time] * n, y: [value] * n } }
        for idx, ts in enumerate(tss):
            for prop_name, prop_val in ts.items():
                if prop_name != 'time':
                    if prop_name not in prop_keyframes:
                        prop_keyframes[prop_name] = {'x': [], 'y': [], 'basetime': ts['time']}

                    prop_keyframes[prop_name]['x'].append(TimeDeltaToMilliseconds(ts['time'] - __basetime))
                    prop_keyframes[prop_name]['y'].append(prop_val)

        for prop_name, prop_data in prop_keyframes.items():
            self._initializePropertyFromXY(prop_name, **prop_data)

    def _initializeFromDataFrame(self, df):
        """
        Takes a pandas dataframe with columns of properties as well as a column for time and converts each row as a timestamp to an interpolation function.

        Args:
            df: A pandas dataframe with columns of properties to build intpolation functions from
        """

        if len(df) == 0: return -1
        __basetime = df.iloc[0]['time']

        if not self.timeFirst: self.timeFirst = df.iloc[0]['time']
        if not self.timeLast: self.timeLast = df.iloc[-1]['time']

        for c in df.columns:
            if c != 'time':
                self._initializePropertyFromXY(c,
                                               x=(df['time'] - __basetime).apply(TimeDeltaToMilliseconds).values,
                                               y=df[c].values,
                                               basetime=__basetime)

    def _initializePropertyFromXY(self, prop, x, y, basetime):
        """
        Builds a function using scipy.interpolation. Will use a constant value for single value xy pairs, a linear interpolation from any float series, and a latch interpolation from any strings or objects in the y series.

        Args:
            prop:     A string specifying the name of the property. This will also be used as the key when internally building a property dictionary.
            x:        A list or numpy array of values (often a time series of values)
            y:        A list or numpy array of values
            basetime: The time from which the x values are offset from
        """
        x = np.array(x)
        y = np.array(y)

        if len(y) <= 1: # if only one keyframe, use a constant interpolation (zero-order extrapolation)
            func = self.__INTERP_CONSTANT(x, y)
        elif np.issubdtype(y.dtype, int) or np.issubdtype(y.dtype, float): # if numeric, use linear interpolation
            func = self.__INTERP_LINEAR(x, y)
        elif np.issubdtype(y.dtype, str) or np.issubdtype(y.dtype, object): # if it's a string, latch most recent value
            func = self.__INTERP_LATCH(x, y)

        self.__interp_props[prop] = self.TimeInterpWrapper(func, basetime)

    def __INTERP_CONSTANT(self, x, y):
        """
        Args:
            x: A list or numpy series
            y: A list or numpy series

        Returns:
            The first value of the y series to be held constant as its interpolation function
        """
        return y[0]

    def __INTERP_LINEAR(self, x, y):
        """
        Args:
            x: A list or numpy series
            y: A list or numpy series

        Returns:
            A scipy.interpolate.interp1d function built from the x and y series passed. Will hold end values if it is requested to interpolate outside the provided x range.
        """
        return interpolate.interp1d(x, y, bounds_error=False, fill_value=(y[0], y[-1]))

    def __INTERP_LATCH(self, x, y):
        """
        Args:
            x: A list or numpy series
            y: A list or numpy series

        Returns:
            A function that will give the latched string of the given y series.
        """
        return lambda time: y[max(bisect.bisect_left(x, time)-1, 0)]

    def __getattr__(self, attr):
        """
        This function is overridden to allow for handling of properties that are not explicitly defined as attributes. For anything not explicitly defined, this overridden function will try to find that key in the dictionary self.__interp_props. If it does not exist there, it will return the function self.__interp_props_default. This added functionality allows for easy interpolation of any keyframed properties by requesting a property by name and passing a time to interpolate at. (e.g. my_actor.keyframe_manager.my_property(0:00:00))

        Args:
            attr: The attribute to be returned.

        Returns:
            A function that will give the latched string of the given y series.
        """
        try: return self.__getattribute__(attr) # first try to return an attribute if it exists in the keyframe manager
        except AttributeError: # otherwise try to return a property from __interp_props
            return self.__interp_props[attr] if attr in self.__interp_props else self.__interp_props_default


class PlaybackManager():

    """
    A class to expose a communal timestamp for simulation, wrapping functionality for playback speed and time skipping
    """

    def __init__(self, renderer=None, time=datetime.datetime.now(), speed_multiplier=1.0):
        self.basetime = time
        self.playback_speed = speed_multiplier
        self.__paused = False
        self.__loop = {'start': None, 'end': None}

        self._basetime_last_update = datetime.datetime.now()
        self._callbacks = { 'PlaybackChange': {} }

        self.__callbackIDMap = {}
        self.__callbackID = 0

        self.text_actor = None
        self.init_text_output(renderer)

    def init_text_output(self, renderer):
        """
        Creates an actor to display the current playback manager status
        """
        renderer.AddObserver('EndEvent', self.update_text_output)

        self.text_actor = vtk.vtkTextActor()
        self.text_actor.GetTextProperty().SetFontFamilyToCourier()
        self.text_actor.GetTextProperty().SetColor([0.2, 0.2, 0.2])
        self.text_actor.GetTextProperty().SetBackgroundColor([0, 0, 0])
        self.text_actor.GetTextProperty().SetBackgroundOpacity(0)
        self.text_actor.GetTextProperty().SetOpacity(0.5)
        self.text_actor.GetTextProperty().SetLineSpacing(0.0)
        self.text_actor.GetTextProperty().SetBold(1)
        self.text_actor.GetTextProperty().SetFontSize(18)
        self.text_actor.ComputeScaledFont(renderer)

        self.text_actor.__x = vtk.mutable(0)
        self.text_actor.__y = vtk.mutable(1)
        renderer.NormalizedDisplayToDisplay(self.text_actor.__x, self.text_actor.__y)
        self.text_actor.SetDisplayPosition(int(self.text_actor.__x) + 10, int(self.text_actor.__y - self.text_actor.GetHeight() - 30))

        renderer.AddActor2D(self.text_actor)

    def update_text_output(self, obj, event):
        """
        An update function for updating text output every frame
        """
        if self.text_actor:
            self.text_actor.__x.set(0)
            self.text_actor.__y.set(1)
            obj.NormalizedDisplayToDisplay(self.text_actor.__x, self.text_actor.__y)
            self.text_actor.SetDisplayPosition(int(self.text_actor.__x) + 10, int(self.text_actor.__y - self.text_actor.GetHeight() - 30))
            self.text_actor.SetInput('[{}] {}x'.format(self.time.strftime("%Y/%m/%d %H:%M:%S"), self.playback_speed))

    def setTime(self, time=datetime.datetime.now()):
        """
        Sets the time of the playback manager and calls all callbacks of type 'PlaybackChange'
        """
        self.basetime = time
        self._basetime_last_update = datetime.datetime.now()
        self.Callback('PlaybackChange')

    def setPlaybackSpeed(self, speed_multiplier):
        """
        Sets the playback speed of the playback manager and calls all callbacks of the type 'PlaybackChange'
        """
        self.basetime = self.time
        self._basetime_last_update = datetime.datetime.now()
        self.playback_speed = speed_multiplier
        if update_resume_speed: self.__resume_to_speed = self.playback_speed
        self.Callback('PlaybackChange')

    def setPlayback(self, time=datetime.datetime.now(), speed_multiplier=1.0, update_resume_speed=True, trigger_callback=True):
        """
        Sets the playback settings explicitly.

        Args:
            time:                The new time of the playback manager
            speed_multiplier:    Playback speed multiplier
            update_resume_speed: Whether to update the resume-to speed - the
                                 playback speed once resume is called. This might be set to
                                 False if the playback is haulted (speed_multiplier=0).
            trigger_callback:    Whether this function to trigger the 'PlaybackChange'
                                 callback.
        """
        self.basetime = time
        self._basetime_last_update = datetime.datetime.now()
        self.playback_speed = speed_multiplier
        if update_resume_speed: self.__resume_to_speed = self.playback_speed
        if trigger_callback: self.Callback('PlaybackChange')

    def pause(self):
        """
        Pauses playback
        """
        logging.debug('[PLAYBACK] Pausing time at {}.'.format(str(self.time)))
        self.basetime = self.time
        self._basetime_last_update = datetime.datetime.now()
        self.__paused = True

    def resume(self):
        """
        Resumes playback
        """
        logging.debug('[PLAYBACK] Resuming time at {}.'.format(str(self.time)))
        self.basetime = self.time
        self._basetime_last_update = datetime.datetime.now()
        self.__paused = False

    def Callback(self, callback_type):
        """
        Calls all callbacks of a given type
        """
        for id, callback in self._callbacks[callback_type].items():
            callback()

    def AddObserver(self, type, callback_func):
        """
        Attach a callback function to the playback manager

        Args:
            type:          A string identifying the type of events to respond to. This will respond to events of the types:
                              * 'PlaybackChange'
            callback_func: The function to be triggered when the given event occurs

        Returns:
            The id of the observer that is created
        """
        if type in self._callbacks:
            id = self.__nextID()
            self.__callbackIDMap[id] = type
            self._callbacks[type][id] = callback_func
            return id

    def RemoveObserver(self, id):
        """
        Removes an observer by id

        Args:
            id: The id of the observer to be removed
        """
        del self._callbacks[self.__callbackIDMap[id]][id]

    def __nextID(self):
        """
        Returns the next id for newly created observers
        """
        self.__callbackID += 1
        return self.__callbackID

    def realtimeOffset(self, offset):
        """
        Offset playback time by a realworld amount of time, taking into consideration the current playback speed
        """
        return (datetime.datetime.now() + offset - self._basetime_last_update) * self.playback_speed + self.basetime

    @property
    def time(self):
        if self.__paused:
            return self.basetime
        else:
            return (datetime.datetime.now() - self._basetime_last_update) * self.playback_speed + self.basetime
