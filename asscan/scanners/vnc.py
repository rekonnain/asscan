#!/usr/bin/env python2

from vncdotool import api
import sys
with api.connect(sys.argv[1], password=sys.argv[2], timeout=3.0) as cli:
    cli.refreshScreen()
    cli.captureScreen(sys.argv[3])
