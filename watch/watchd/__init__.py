"ACPI sensors list"
import sys


WATCH_LIST = ["k8temp", "coretemp", "via686a", "msp430"]
LOG_PATH = "/tmp/smarthouse"
LOG_PATH_FORMAT = "%s/sensor_%%s" % LOG_PATH

FUNC_PREFIX = "sensors_watch_process_"


def sensor(f):
    def _sens():
        sys.stdout = open("%s/%s.log" % (LOG_PATH, f.func_name), "a+")
        sys.stderr = open("%s/%s.log" % (LOG_PATH, f.func_name), "a+")
        print "%s started" % f.func_name
        f()

    _sens.func_name = FUNC_PREFIX + f.func_name
    return _sens
