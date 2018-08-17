# PointCloudLineage

Most of how to do things are in the specific documentation for the respective functions, but a couple of things to note here

## **Before Running**
Check the [BaseProjectDirectory.py](~/BaseProjectDirectory.py) file and change the check to your home directory
as well as the base project directory.

## Using LASTools
This section describes how to use functionality such as zipping/unzipping files or merging
1. Download the LAStools package from [their website](https://rapidlasso.com/lastools/)
2. When you unzip the LAStools folder, there is a makfile, so you can use it to build the necessary binaries
3. After you make the binaries, you have funcitonality such as laszip, lasmerge, las2txt, etc. from their bin
4. For example, the syntax for converting between .laz and .las is as follows:
    /path/to/LAStools/bin/laszip -i /path/to/input_file.laz -o /path/to/output_file.las


## Using AWS
The code is written in such a way that any of the computation is modularized out, so you can quite easily spin up
an AWS server and send over the filters + data (with something like scp) and just run

There's no need to send over the visuals because you can send up a .las file, run the filter you want, and save the result
as another las file and then scp the resultant file back

Look at NoVisuals/NoVisualMultiRooms.py for the specific script I ran on the AWS
