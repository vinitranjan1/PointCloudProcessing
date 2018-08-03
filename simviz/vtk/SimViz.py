import os, argparse, logging, datetime, configobj, pandas as pd
from pathlib import Path
import pdb
from vtk import *
import vtkLineage

# def frameRefresh(obj, event):
#     obj.GetRenderWindow().Render()

def main(path=None, config_path=None, init_path=None, logs_path=None, vis_save_pickle=None, overwrite=False):

    ## Temporary place to set up some simulation variables
    sim = configobj.ConfigObj(os.path.join(path, 'simulation', 'simulation.ini'))

    ### vtk Setup ###
    # Initialize renderer, window and interactor

    # disable warning messages
    vtkObject.GlobalWarningDisplayOff()
    om = vtkOutputWindow()
    try: om.SendToStdErrOn() # only works on windows
    except: pass

    def frame(obj, event, w2i=None, wavi=None):
        obj.GetRenderWindow().Render()
        if w2i and wavi:
            w2i.Modified()
            wavi.Write()

    # create window
    renderer = vtkRenderer()
    renderer.GradientBackgroundOn()
    renderer.SetBackground(0.75, 0.75, 0.75)
    renderer.SetBackground2(0.95, 0.95, 0.95)
    renderWindow = vtkRenderWindow()
    renderWindow.SetSize(800, 600)
    renderWindow.AddRenderer(renderer)

    # window capture
    # TODO: window capture classes not ported to python wrapper, this is adapted
    # code from Cxx examples on how it might be implemented, once it's included
    # window_to_image = vtk.vtkWindowToImageFilter()
    # window_to_image.SetInput(renderWindow)
    # window_avi = vtk.vtkMPEG2Writer()
    # window_avi.SetFileName('/path/to/file/test.avi')
    # window_avi.SetInputConnection(window_to_image.GetOutputPort())
    # window_avi.Start()
    window_to_image = None
    window_avi = None

    # add in window interaction
    interactor = vtkRenderWindowInteractor()
    interactor.SetRenderWindow(renderWindow)
    interactor.Initialize()
    interactor.SetInteractorStyle(vtk.vtkInteractorStyleTerrain())
    updateTimerID = interactor.CreateRepeatingTimer(int(1000/60)) # 1s/fps (ms)
    interactor.AddObserver('TimerEvent', \
        lambda obj, event: frame(obj, event, window_to_image, window_avi))


    ### vtk Extras ###
    # Some extra elements not needed for the simulation visualization

    # add a skybox ooo pretty clouds
    skybox = vtkLineage.vtkSkybox(renderer, os.path.join(os.path.dirname(__file__), 'assets', 'skyboxes', 'skybox_daylight_bright.png'), ground_plane=False)

    # add coordinate axes to bottom left corner of window
    axes = vtk.vtkAxesActor()
    orientationWidget = vtk.vtkOrientationMarkerWidget()
    orientationWidget.SetOrientationMarker(axes)
    orientationWidget.SetInteractor(interactor)
    orientationWidget.SetViewport(0, 0, 0.2, 0.2)
    orientationWidget.SetEnabled(1)
    orientationWidget.InteractiveOff()
    # add a logging handler to display logging messages to render window
    vtkStreamHandler = vtkLineage.vtkStreamHandler(renderer, interactor, level=logging.INFO)
    # add a floor
    gridFloor = vtkLineage.vtkGridFloorActor(renderer, x=3500, y=3000, size=7200, grid_size=300, feather=1600, color_axes=False)


    ### Simulation visualization ###
    # This small section is everything for the visualization. Everything else is
    # simply in place to build the vtk scene

    # add playback manager to sync simulation visualization playback
    # playback = vtkLineage.PlaybackManager(renderer, time=pd.Timestamp(sim['global']['simulation_start_time']), speed_multiplier=50.0)
    playback = vtkLineage.PlaybackManager(renderer, time=datetime.datetime(2016, 1, 1, 0, 0), speed_multiplier=100.0)

    # build warehouse - a container object for all systems in the warehouse simulation
    warehouse = vtkLineage.Warehouse(renderer, interactor, playback)
    warehouse.initializeFromSimDir(path, overwrite)
    # warehouse.initializeFromFiles(config_path, init_path, logs_path, vis_save_pickle, overwrite_pickle)


    # start scene
    renderer.GetActiveCamera().SetViewUp(0.0, 0.0, 1.0)
    renderer.GetActiveCamera().SetPosition(4000, -4000, 2000)
    renderer.GetActiveCamera().SetFocalPoint(2000, 1000, 1000)
    renderer.GetActiveCamera().SetClippingRange(1, 10**6)
    # renderer.ResetCamera()
    renderWindow.Render()
    renderWindow.SetWindowName("Lineage Simulation Visualization") # Must be called after vtkRenderWindow.Render()
    interactor.Start()
    if window_avi: window_avi.End()

if __name__ == '__main__':

    # initialize logger
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
    consoleHandler.setLevel(logging.DEBUG)
    logging.getLogger().addHandler(consoleHandler)
    logging.getLogger().setLevel(logging.INFO)

    #$:python3 ./simviz/vtk/dev/simviz.py -t ./datafiles/MaraLoma.linsim

    # parse command line arguments
    parser = argparse.ArgumentParser(description='Visualize Simulation Logs')
    parser.add_argument('-c', '--config-file', dest='config_path', default='',
        help="Path from which to load warehouse initialization files.")
    parser.add_argument('-i', '--init-file', dest='init_path', default='',
        help="Path from which to load pallet rackstore initialization files.")
    parser.add_argument('-l', '--logs-dir', dest='logs_path', default='',
        help="Path of directory from which to load log data.")
    parser.add_argument('-v', '--vis-save', dest='vis_save_pickle', default='.',
        help="Path to which the visualization initialization is saved.")
    parser.add_argument('-t', '--linsim-dir', dest='linsim', default='~/PycharmProjects/LineageProject/simviz/vtk/datafiles/MaraLoma.linsim',
        help="Path to which the visualization initialization is saved.")
    parser.add_argument('-o', '--overwrite-pallet', dest='overwrite', action='store_true',
        help="Overwrite saved pallet file if it exists.")
    args = parser.parse_args()

    print("\n --  Arguments  -- " + \
          "\nData Loading" + \
          "\n +- From Simulation Files"
          "\n    +- Config File : " + str(Path(args.config_path).resolve()) + \
          "\n    +- Init File   : " + str(Path(args.init_path).resolve()) + \
          "\n    +- Logs Dir    : " + str(Path(args.logs_path).resolve()) + \
          "\n +- From Previous Visualization Save" + \
          "\n    +- Load File   : " + args.vis_save_pickle + \
          "\nData Saving" + \
          "\n +- Save File   : " + args.vis_save_pickle + \
          "\n +- Overwrite   : " + str(args.overwrite))
    print('\nStarting Visualization...')

    # run visualization

    main(path=args.linsim, overwrite=args.overwrite)
