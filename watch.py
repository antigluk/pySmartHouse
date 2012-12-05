import sensors
from time import sleep

WATCH_LIST = ["k8temp", ]

def main():
    sensors.init()
    try:
        while True:
            for sensor in sensors.iter_detected_chips():
                if sensor.prefix in WATCH_LIST:
                    #MONGO?
                    for feature in sensor:
                        print "%s: %s=%s" % (sensor.prefix, feature.name, feature.get_value())

            sleep(2)
    finally:
        sensors.cleanup()
        

if __name__ == '__main__':
    main()