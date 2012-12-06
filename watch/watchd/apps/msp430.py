import serial

from time import sleep

from watchd import sensor
from watchd import LOG_PATH_FORMAT

"""
MSP430 sensors (e.g., external temperature)
"""
@sensor
def msp430():
    prefix = "msp430"
    while True:
        try:
            ser = serial.Serial(port='/dev/ttyACM0', baudrate=9600)
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
        except serial.SerialException, e:
            print e.message
        sleep(2)