"""
Vinit Ranjan, Chris Eckman
Lineage Logistics

A function to log filtering to a text file
To see direct usage, look at NoVisuals/NoVisualMultiRooms.py

Inputs:
config_file - text file to append to, and if it doesnt exist, create it
input_las_file - name of las file filtering was done to
called_function - name of filter function called on las file
kwargs - parameters used for that specific filter
include_las_name - flag used if you want to include a message saying what file you did filtering to
                this way, if youre doing multiple levels of filtering, then it won't repeat unnecessary information
done_message - message to write when done with a file
"""
import sys
import os


def write_to_config(config_file, input_las_file=None, called_function=None, kwargs=None,
                    include_las_name=True, done_message=None):
    if not os.path.isfile(config_file):
        with open(config_file, 'w'):
            pass
    with open(config_file, 'a') as f:
        if done_message is not None:
            f.write(done_message+"\n")
        else:
            if include_las_name:
                f.write("Filtering done to %s\n" % input_las_file)
            f.write(called_function + "\n")
            f.write(','.join('{0}={1!r}'.format(k, v) for k, v in kwargs.items()))
            f.write("\n")
