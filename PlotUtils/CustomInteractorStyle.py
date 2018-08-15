"""
Vinit Ranjan, Chris Eckman
Lineage Logistics

For VTK visualization/interaction with the mouse, it is necessary to override the interactor style for custom movements
Even though VTK has default mouse event observers, if we want to add functionality such as editting display angles,
    we need to use our custom self.left_button_press_event and self.left_button_release_event functions
However, we still want the base functionality as well, such as actually moving the screen, and the trick is to use
    functions such as super.OnMouseMove() which is inherited from the super class vtk.vtkInteractorStyleTrackballCamera

Inputs:
ren - A VTKRenderer object, and strictly speaking this isn't necessary for the interactorstyle, but in visualization,
    a lot of times we need to reference the specific renderer within a renderwindow, so the reference to the renderer
    is left here in self.ren
    For example, in PointCloudPlotQt.py, the main plotting script, if w is the QVTKRenderWindowInteractor for a plot,
    we can get the renderer by w.GetRenderWindow().GetInteractor().GetInteractorStyle().ren
corner - A corner annotation object, used for the display angle on the screen
app - the main QWidget that runs the visualization, also included a reference here, because to only click on a specific
    plot, need to reference the entire application to determine to the focus
"""
import vtk


class CustomInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self, ren=None, corner=None, app=None):
        self.AddObserver("LeftButtonPressEvent", self.left_button_press_event)
        self.AddObserver("LeftButtonReleaseEvent", self.left_button_release_event)
        self.AddObserver("MiddleButtonPressEvent", self.middle_button_press_event)
        self.AddObserver("MiddleButtonReleaseEvent", self.middle_button_release_event)
        self.AddObserver("MouseMoveEvent", self.mouse_button_move_event)
        self.corner = corner
        self.ren = ren
        self.camera = ren.GetActiveCamera()
        self.app = app
        self.culling = False
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

    def left_button_release_event(self, obj, event):
        # print("Left Button released")
        self.edit_display_angle(obj, event)
        self.leftButtonPushed = False
        self.lastLeftButtonClick = event
        self.OnLeftButtonUp()  # make sure that this goes AFTER the previous function call

    def middle_button_press_event(self, obj, event):
        self.middleButtonPushed = True
        # print("pressed")
        if self.culling:
            pass
        self.OnMiddleButtonDown()

    def middle_button_release_event(self, obj, event):
        self.middleButtonPushed = False
        self.OnMiddleButtonUp()

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
