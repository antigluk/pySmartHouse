"""
Daemon watching for sensors
"""

import sensors
from time import sleep
from multiprocessing import Process

"ACPI sensors list"
WATCH_LIST = ["k8temp", ]
LOG_PATH_FORMAT = "/tmp/smarthouse/sensor_%s"

"""
ACPI sensors (e.g., computer internal temperature)
"""
def sensors_acpi():
    sensors.init()
    try:
        while True:
            for sensor in sensors.iter_detected_chips():
                if sensor.prefix in WATCH_LIST:
                    wfile = file(LOG_PATH_FORMAT % sensor.prefix, "w")
                    #MONGO?
                    for feature in sensor:
                        print "%s: %s=%s" % (sensor.prefix, feature.name, feature.get_value())
                        print>>wfile, "%s=%s" % (feature.name, feature.get_value())

            sleep(2)
    finally:
        sensors.cleanup()
        

if __name__ == '__main__':
    local = locals()
    functions = filter(lambda x: x.startswith("sensors_"), local)
    [Process(target=local[func]).start() for func in functions]

