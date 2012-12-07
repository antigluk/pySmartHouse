import serial

from time import sleep, time

from watchd import sensor
from watchd import LOG_PATH_FORMAT

from sqlite3dbm import sshelve as sqlite

"""
MSP430 sensors (e.g., external temperature)
"""
@sensor
def msp430():
    prefix = "msp430"
    while True:
        try:
            ser = serial.Serial(port='/dev/ttyACM0', baudrate=9600)
            db = sqlite.open(LOG_PATH_FORMAT % prefix)
            try:
                while True:
                    ser.write("1")
                    line = ser.readline().strip()
                    for sensor in line.split(';'):
                        name, value = sensor.split('\t')

                    db[int(time())] = \
                      [tuple(sensor.split('\t')) for sensor in line.split(';')]

                    sleep(2)
            finally:
                ser.close()
        except serial.SerialException, e:
            print e.message
        sleep(2)