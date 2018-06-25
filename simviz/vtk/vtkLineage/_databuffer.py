import threading, datetime, logging

from ._helpers import *

class DataBuffer(threading.Thread):

    """
    DataBuffer

    Run a recurring threaded process to keep an accurate list of pallets that need to be actively updated.

    Used as a base class for specific applications such as buffering the pallet data object or various system behaviors from collective data.
    """

    def __init__(self):
        super().__init__()
        self.name=None
        self.update_event = threading.Event()
        self.daemon = True # End thread when parent thread ends
        self.pm = None

        # Setting the buffer size too low might cause issues with data frame sizes being inconsistent. Need to address.
        # This occurs when it has not fully updated before the next iteration
        self.buffer_size = datetime.timedelta(0, 20, 0) # default to 10s of buffer time (playback time, not simulation time)
        self.__setDefaultUpdateInterval()
        self.start()

    def __setDefaultUpdateInterval(self):
        # default to 3 times per buffer interval
        self.update_interval = self.buffer_size / 2.0

    def start(self, update_immediately=False):
        """
        Begin the thread to compute the buffered data
        """
        if update_immediately: self.update()
        if not self.is_alive(): super().start()

    def pause(self):
        """
        Pause the thread for computing the buffered data
        """
        logging.debug('[BUFFER] Pausing.')
        self.update_event.set()
        self.update_event.clear()

    def resume(self, callback=None, callback_args={}):
        """
        Resume the thread for computing buffered data
        """
        logging.debug('[BUFFER] Resuming.')
        self.update()
        if callback: callback(**callback_args)
        self.update_event.set()

    def update(self):
        """
        method to be overloaded by inheriting classes, called at a frequency defined by update_interval
        """
        pass

    def run(self):
        self.update_event.set()
        # outer loop serves to handle pausing and resuming
        while self.update_event.wait():
            self.update_event.clear()
            # inner loop handles looping calls to update event
            while not self.update_event.wait(timeout=TimeDeltaToSeconds(self.update_interval)):
                self.update()

    @property
    def time(self):
        return self.pm.time

    @property
    def buffer_start(self):
        return self.pm.realtimeOffset(self.buffer_size * -0.1)

    @property
    def buffer_end(self):
        return self.pm.realtimeOffset(self.buffer_size * 1.0)
