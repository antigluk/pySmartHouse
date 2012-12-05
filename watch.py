import sensors
from time import sleep

WATCH_LIST = ["k8temp", ]
LOG_PATH_FORMAT = "/tmp/smarthouse/sensor_%s"

def api_sensors():
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
    api_sensors()
