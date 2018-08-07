from ConfigSection import ConfigSection

import os
from BaseProjectDirectory import base_project_dir

BASE_PROJECT_DIR = base_project_dir

filters = ConfigSection("filters")
filters.dir = "%s/%s" % (BASE_PROJECT_DIR, "Filters")
