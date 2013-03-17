
"ACPI sensors list"
WATCH_LIST = ["k8temp", "coretemp", "via686a", "msp430"]
LOG_PATH = "/tmp/smarthouse"
LOG_PATH_FORMAT = "%s/sensor_%%s" % LOG_PATH

FUNC_PREFIX = "sensors_watch_process_"


def sensor(f):
    def _sens():
        f()
    _sens.func_name = FUNC_PREFIX + f.func_name
    return _sens
