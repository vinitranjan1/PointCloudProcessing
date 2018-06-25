def TimeDeltaToMilliseconds(td):
    """
    Convert a pandas.TimeDelta to milliseconds
    """
    return (td.days * 24.0 * 60.0 * 60.0 + td.seconds) * 1000.0 + td.microseconds / 1000.0

def TimeDeltaToSeconds(td):
    """
    Convert a pandas.TimeDelta to seconds
    """
    return (td.days * 24.0 * 60.0 * 60.0 + td.seconds) + td.microseconds / 1000000.0

class vtkLineageSystem():

    """
    vtkLineageSystem

    A base class for all Lineage system vtk objects.

    Contains functions that are assumed to exist in all systems such that if they are not overloaded, they do not throw errors.
    """

    def reload(self,time):
        pass

    def update(self, obj, event, time):
        pass
