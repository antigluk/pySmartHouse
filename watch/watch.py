"""
Daemon watching for sensors
"""

import sensors
from time import sleep
from multiprocessing import Process

import serial

"ACPI sensors list"
WATCH_LIST = ["k8temp", "coretemp", "via686a", ]
LOG_PATH_FORMAT = "/tmp/smarthouse/sensor_%s"

"""
ACPI sensors (e.g., computer internal temperature)
"""
def sensors_acpi():
    sensors.init()
    print list(sensors.iter_detected_chips())
    try:
        while True:
            for sensor in sensors.iter_detected_chips():
                if sensor.prefix in WATCH_LIST:
                    wfile = file(LOG_PATH_FORMAT % sensor.prefix, "w")
                    #MONGO?
                    for feature in sensor:
                        print "%s: %s=%s" % (sensor.prefix, feature.name, feature.get_value())
                        print>>wfile, "%s=%s" % (feature.name, feature.get_value())
                    wfile.close()

            sleep(2)
    finally:
        sensors.cleanup()
    
def sensors_msp430():
    prefix = "msp430"
    while True:
        ser = serial.Serial(port='/dev/ttyACM0', baudrate=9600)  # open first serial port
        try:
            while True:
                ser.write("1")
                line = ser.readline().strip()
                # print line
                wfile = file(LOG_PATH_FORMAT % prefix, "w")
                for sensor in line.split(';'):
                    name, value = sensor.split('\t')
                    print>>wfile, "%s=%s" % (name, value)
                    print "%s: %s=%s" % (prefix, name, value)
                wfile.close()
                sleep(2)
        finally:
            ser.close()
    

if __name__ == '__main__':
    local = locals()
    functions = filter(lambda x: x.startswith("sensors_"), local)
    [Process(target=local[func]).start() for func in functions]

