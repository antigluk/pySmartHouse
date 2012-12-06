
"ACPI sensors list"
WATCH_LIST = ["k8temp", "coretemp", "via686a", "msp430"]
LOG_PATH_FORMAT = "/tmp/smarthouse/sensor_%s"

FUNC_PREFIX = "sensors_watch_process_"

def sensor(f):
    def _sens():
        f()
    _sens.func_name = FUNC_PREFIX + f.func_name
    return _sens