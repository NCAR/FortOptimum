# coding: utf-8
  
from __future__ import unicode_literals, print_function

import sys
import os
import pyloco

def entry():

    from pyloco import entry

    sys.argv.insert(0,  "pyloco")
    sys.argv.insert(1, os.path.join(os.path.dirname(__file__), "main.pyx"))

    return entry.main()
