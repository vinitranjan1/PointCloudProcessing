import os

# change these files for personal use
if os.environ['HOME'] == '/Users/Vinit':
    base_project_dir = '/Users/Vinit/PycharmProjects/LineageProject/'
else:
    raise Exception("Unspecified base_project_dir, check BaseProjectDirectory.py")
