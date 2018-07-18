import vtk
from math import cos, sin


class CustomInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self, parent=None, ren=None, corner=None, app=None):
        self.AddObserver("LeftButtonPressEvent", self.left_button_press_event)
        self.AddObserver("LeftButtonReleaseEvent", self.left_button_release_event)
        self.AddObserver("MouseMoveEvent", self.mouse_button_move_event)
        self.corner = corner
        self.ren = ren
        self.camera = ren.GetActiveCamera()
        self.app = app
        self.lastLeftButtonClick = None
        self.leftButtonPushed = False
        self.rightButtonPushed = False
        self.middleButtonPushed = False
        self.coordinateButtonPushed = False

    def left_button_press_event(self, obj, event):
        # print("Left Button pressed")
        w = self.app.focusWidget()
        self.edit_display_angle(obj, event)
        self.leftButtonPushed = True
        self.OnLeftButtonDown()
        return

    def left_button_release_event(self, obj, event):
        # print("Left Button released")
        self.edit_display_angle(obj, event)
        self.leftButtonPushed = False
        self.lastLeftButtonClick = event
        self.OnLeftButtonUp()  # make sure that this goes AFTER the previous function call
        return

    def mouse_button_move_event(self, obj, event):
        super().OnMouseMove()  # keep old movement capability but add more
        if self.leftButtonPushed:
            self.edit_display_angle(obj, event)
        return

    def edit_display_angle(self, obj=None, event=None):
        if self.camera is not None:
            new_orientation = self.camera.GetOrientation()
            self.corner.SetText(0, "(x, y, z) = (%.3f, %.3f, %.3f)" %
                                (new_orientation[0], new_orientation[1], new_orientation[2]))

    def set_camera_orientation(self, position, focus, viewup):
        self.ren.ResetCamera()
        self.camera.SetPosition(position)
        self.camera.SetViewUp(viewup)
        self.camera.SetFocalPoint(focus)
