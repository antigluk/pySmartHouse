"""
Front-end web application, shows sensors and allow some control
"""

from flask import Flask, render_template, Markup

from watchd import LOG_PATH

import sh
import os
import fnmatch
import socket
import fcntl
import struct

app = Flask(__name__)

MSP430SERIAL = "/dev/ttyACM0"

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])

def get_info(wide=False):
    try:
        ip = get_ip_address("eth0")
    except IOError:
        try:
            ip = get_ip_address("wlan0")
        except IOError:
            try:
                ip = get_ip_address("lo")
            except IOError:
                ip = "0.0.0.0"
    f = {
            "host": sh.hostname().strip(),
            "ip": ip,#sh.hostname("-i").strip(),
            "version": "0.0.1",
        }
    if os.path.exists(MSP430SERIAL):
        f.update({"msp430" : {"port": MSP430SERIAL}})
    if wide:
        f.update({
                "ifconfig" : sh.ifconfig(),
                "route" : sh.route(),
            })
    return f

@app.route("/all")
def all_sensors():
    sensors = []
    for sensor in os.listdir(LOG_PATH):
        if not fnmatch.fnmatch(sensor, 'sensor_*'):
            continue
        file_name = os.path.join(LOG_PATH, sensor)
        if os.path.exists(file_name):
            data = file(file_name).readlines()
            sensors.append({"name":sensor[len("sensor_"):], "data":[line.strip().split("=") for line in data]})

    return render_template("all_sensors.html", data=sensors, info=get_info())


@app.route("/")
def index():
    sensors = {}
    for sensor in os.listdir(LOG_PATH):
        if not fnmatch.fnmatch(sensor, 'sensor_*'):
            continue
        file_name = os.path.join(LOG_PATH, sensor)
        if os.path.exists(file_name):
            data = file(file_name).readlines()
            sensors.update({sensor[len("sensor_"):]: dict([line.strip().split("=") for line in data])})

    return render_template("index.html", data=sensors, info=get_info())

@app.route("/info")
def sysinfo():
    return render_template("sysinfo.html", info=get_info(wide=True))

if __name__ == "__main__":
    app.run(debug = False, host='0.0.0.0')
