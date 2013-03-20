"""
Daemon watching for sensors
"""

from multiprocessing import Process

SENSORS = ["acpi", "msp430", "camera"]

import os
import sys


currDir = os.path.dirname(os.path.realpath(__file__))
rootDir = os.path.abspath(os.path.join(currDir, '..'))
if rootDir not in sys.path:  # add parent dir to paths
    sys.path.append(rootDir)

import watchd

externals = {}

import apps
for s in SENSORS:
    try:
        externals.update(__import__("watchd.apps.%s" % s, fromlist=["apps"]).__dict__)
    except ImportError, e:
        print "%s ImportError: %s" % (s, e.message)

if __name__ == '__main__':
    # local = locals()
    functions = filter(lambda x: hasattr(x[1], 'func_name'), externals.iteritems())
    f_sensors = filter(lambda x: x[1].func_name.startswith(watchd.FUNC_PREFIX), functions)
    [Process(target=func[1]).start() for func in f_sensors]
