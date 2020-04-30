#!/usr/bin/env python

import sys
import site
site.addsitedir('/var/www/html/python-engine/lib/python3.6/site-packages')
sys.path.insert(0, '/var/www/html/python-engine')

from engine import app as application

