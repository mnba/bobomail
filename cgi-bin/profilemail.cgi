#!/usr/bin/env python

PUBLISHED_MODULE = 'main'

# You only need to change the following path
INCLUDE_PATHS = ["/usr/local/bobomail"] 

Z_DEBUG_MODE = 1
IIS_HACK = 0

import sys
import profile
sys.path[0:0]=INCLUDE_PATHS
profile.run("import ZCGI", "logs/profile")
