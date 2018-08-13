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
