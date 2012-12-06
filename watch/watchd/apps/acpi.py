import sensors

from time import sleep

from watchd import sensor
from watchd import LOG_PATH_FORMAT

"""
ACPI sensors (e.g., computer internal temperature)
"""
@sensor
def acpi():
    sensors.init()
    print "ACPI Sensors found: %s" % list(sensors.iter_detected_chips())
    try:
        while True:
            for sensor in sensors.iter_detected_chips():
                wfile = file(LOG_PATH_FORMAT % sensor.prefix, "w")
                #MONGO?
                for feature in sensor:
                    print "%s: %s=%s" % (sensor.prefix, feature.name, feature.get_value())
                    print>>wfile, "%s=%s" % (feature.name, feature.get_value())
                wfile.close()

            sleep(2)
    finally:
        sensors.cleanup()
