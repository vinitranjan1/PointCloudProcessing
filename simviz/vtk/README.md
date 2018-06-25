# VTK Wrapper Used for Rendering of Warehouse Dynamics

## Installing VTK

The latest version of VTK, which introduces Python3 compatibility, is not yet available in the core anaconda repositories. To install this version and maintain a Python3 codebase, use this command to install from the conda-forge repositories.

`conda install -c conda-forge vtk=7.1.0`

Or you can install from the [VTK website](http://www.vtk.org/),

## Running The Visualization

The simulation is run from the file `simviz.py`, taking command line arguments to point to a `.linsim` directory generated from the simulation. Alternatively, individual files for each component of the simulation can be separately specified.

* Using a `.linsim` directory, the simulation can be run with

    `python simviz.py -t simulation_output.linsim`

* For details about alternative parameters, use the command

    `python simviz.py -h`

## Remaining Issues

### 1. Databuffer lapses under heavy load

Currently, data that has to be actively updated during playback is filtered from a dataframe containing all pallets and the paths they will travel from ingestion to exit. This process occurs in a background thread on a set interval (with a bit of leniency built in). However, if it doesn't update before the end of the previously buffered window finishes, it results in a failure to unload old data, leaving some stagnant pallets throughout the warehouse.

##### Potential proposed solutions:
* a dynamic buffer size that responds to the demands of the update thread.
* also calculate a diff of pallets new and removed to the active pallet datastream such that those that should get unloaded are explicitly calculated between each update to the data buffer.
* keep a list of the row indices of active pallets during predetermined windows that readily culls down the full dataframe to a only a subset based on the active windows of all pallets.


### 2. Culling plane specifications

VTK supports culling based on culling planes (allowing specification of up to 6 planes to limit the geometry that is rendered). This could be used to 'cut' the warehouse so that the internals of the pallet rackstore are visible. However, there was a bug in the implementation in 7.1.0. A bug report has been filed and an attempt at a pull request was submitted, but due to issues with their online submission it was not accepted.

**Attempted patch**: https://gitlab.kitware.com/dgkf/vtk/commit/cc0fea060125919f0063f57ea48e05020bf6d34d

**Cause of error detailed in issue submission**:
https://gitlab.kitware.com/vtk/vtk/issues/16908

### 3. Video capture

VTK supports video capture, though the function is not exposed in the python wrapper.
