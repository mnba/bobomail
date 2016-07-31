# -*- coding: utf-8 -*-
"""Here are settings which normally don't need to be changed"""
import os, sys; pathjoin = os.path.join

__version__ = "0.6pre1"
__author__ = "Henning Schröder <ich@henning-schroeder.de>"
bobomail_version = __version__

true = 1
false = not true


connection_timeout = 120  # in seconds
max_session_length = 3600 # in seconds


default_signature = "" #Posted with BoboMail -- http://bobomail.sourceforge.net"


httpd_port = 9673


system = os.uname()
XMailer = "BoboMail/%s (%s-%s %s)" % (
    __version__, system[0], system[4], system[2])
