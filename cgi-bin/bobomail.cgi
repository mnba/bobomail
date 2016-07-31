#!/usr/bin/python

PUBLISHED_MODULE = 'main'

# You only need to change the following path
INCLUDE_PATHS = ["/var/www/bobomail"] 

Z_DEBUG_MODE = 1
IIS_HACK = 0

import sys
sys.path[0:0]=INCLUDE_PATHS


#XXX: Hack until new ZPublisher and DocumentTemplates are integrated
import warnings 
warnings.filterwarnings("ignore", ".* regex .*", DeprecationWarning, "", append=1)
warnings.filterwarnings("ignore", ".* regsub .*", DeprecationWarning, "", append=1)
warnings.filterwarnings("ignore", "", SyntaxWarning, "", append=1)
import ZCGI
