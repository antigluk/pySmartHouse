import sensors

from time import sleep, time

from watchd import sensor
from watchd import LOG_PATH_FORMAT

from sqlite3dbm import sshelve as sqlite

"""
ACPI sensors (e.g., computer internal temperature)
"""
@sensor
def acpi():
    sensors.init()
    print "ACPI Sensors found: %s" % list(sensors.iter_detected_chips())

    db = dict((sensor.prefix, sqlite.open(LOG_PATH_FORMAT % sensor.prefix)) for sensor 
                                in sensors.iter_detected_chips() )

    try:
        while True:
            for sensor in sensors.iter_detected_chips():
                #MONGO?
                for feature in sensor:
                    print "%s: %s=%s" % (sensor.prefix, feature.name, feature.get_value())

                db[sensor.prefix][time()] = \
                    [(feature.name, feature.get_value()) for feature in sensor]

            sleep(2)
    finally:
        sensors.cleanup()
