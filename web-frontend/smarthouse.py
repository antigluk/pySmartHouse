"""
Front-end web application, shows sensors and allow some control
"""

from flask import Flask, render_template

from watchd import LOG_PATH

import sh
import os
import fnmatch
import socket
import fcntl
import struct

app = Flask(__name__)

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])

def get_info():
    return {"host": sh.hostname().strip(),
            "ip": get_ip_address("eth0"),#sh.hostname("-i").strip(),
            "version": "0.0.1",
            }

@app.route("/")
def index():
    sensors = []
    for sensor in os.listdir(LOG_PATH):
        if not fnmatch.fnmatch(sensor, 'sensor_*'):
            continue
        file_name = os.path.join(LOG_PATH, sensor)
        if os.path.exists(file_name):
            data = file(file_name).readlines()
            sensors.append({"name":sensor[len("sensor_"):], "data":[line.strip().split("=") for line in data]})

    return render_template("index.html", data=sensors, info=get_info())

if __name__ == "__main__":
    app.run(debug = False, host='0.0.0.0')