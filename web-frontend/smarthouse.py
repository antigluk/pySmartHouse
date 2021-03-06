#-*- coding: utf8 -*-

"""
Front-end web application, shows sensors and allow some control
"""

from __future__ import division

from flask import Flask, render_template, redirect

from watchd import LOG_PATH

from auth import requires_auth

import sh
import os
import fnmatch
import socket
import fcntl
import struct

from sqlite3dbm import sshelve as sqlite

app = Flask(__name__)

MSP430SERIAL = "/dev/ttyACM0"
VIDEO_DEVICE = "/dev/video0"
IMG_LAST = '/home/aiko/pysmarthouse/resources/static/lastimg.dat'
VIDEO_ENABLED_FILE = "/home/aiko/camera_enabled.marker"


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

    f = {"host": sh.hostname().strip(),
         "ip": ip,  # sh.hostname("-i").strip(),
         "version": "0.0.1",
         }

    if os.path.exists(MSP430SERIAL):
        f.update({"msp430": {"port": MSP430SERIAL}})

    if os.path.exists(VIDEO_DEVICE):
        f.update({"video": {"port": VIDEO_DEVICE}})

    if wide:
        try:
            f.update({"ifconfig": sh.Command("/sbin/ifconfig")(),
                      "route": sh.Command("/sbin/route")(),
                      })
        except:
            pass
    return f


@app.route("/all")
@requires_auth
def all_sensors():
    sensors = []
    for sensor in os.listdir(LOG_PATH):
        if not fnmatch.fnmatch(sensor, 'sensor_*'):
            continue
        file_name = os.path.join(LOG_PATH, sensor)

        if os.path.exists(file_name):
            data = sqlite.open(file_name).getlast()[0][1]
            sensors.append({"name": sensor[len("sensor_"):], "data": data})

    return render_template("all_sensors.html", data=sensors, info=get_info())


@app.route("/charts/")
@requires_auth
def charts_list():
    sensors = []
    for sensor in os.listdir(LOG_PATH):
        if not fnmatch.fnmatch(sensor, 'sensor_*'):
            continue
        sensors.append(sensor)

    return render_template("sensors_list.html", charts=sensors, info=get_info())


@app.route("/charts/<device>")
@requires_auth
def chart_sensors(device):
    file_name = os.path.join(LOG_PATH, device)
    if os.path.exists(file_name):
        data = sqlite.open(file_name).getlast()[0][1]
        return render_template("device_sensors.html", device_name=device,
                               sensors=sorted(dict(data).keys()), info=get_info())
    # return render_template("chart.html", sensor={'name': device}, info=get_info())


@app.route("/charts/<device>/<sensor>")
@requires_auth
def chart(device, sensor):
    file_name = os.path.join(LOG_PATH, device)
    if os.path.exists(file_name):
        N = 3*60*60//2
        C = 10
        d = sqlite.open(file_name).getlast(N)
        d += [(d[-1][0], [(x[0], x[1]) for x in d[-1][1]]) for x in xrange(N-len(d))]
        # print d
        data = [[(d[0][1][n][0], (d[K*(N//C)][0], sum([float(o) for o in row]) /
                (1 if len(row) == 0 else len(row)))) for n, row in
            enumerate([[x[i][1] for x in [x[1] for x in d][(K*(N//C)):(K+1)*(N//C)]] for i in
                      xrange(len(d[0][1]))])] for K in xrange(C)]
        # data = [sum(numpy.array(data[(i*(N/C)):((i+1)*(N/C))][1]))/(N/C) for i in xrange(C)]
        # data.reverse()
        print data
        keys = [int(dict(v)[sensor][0]) for v in data]
        keys = ["-%d min" % ((v-min(keys))/60) for v in keys]
        return render_template("chart.html", device_name=device,
                               sensor_name=sensor,
                               data={
                               'x': keys,
                               'y': [str(dict(v)[sensor][1])[:4] for v in data],
                               },
                               info=get_info())
    # return render_template("chart.html", sensor={'name': device}, info=get_info())


@app.route("/")
@requires_auth
def index():
    sensors = {}
    if os.path.exists(LOG_PATH):
        for sensor in os.listdir(LOG_PATH):
            if not fnmatch.fnmatch(sensor, 'sensor_*'):
                continue
            file_name = os.path.join(LOG_PATH, sensor)
            if os.path.exists(file_name):
                data = sqlite.open(file_name).getlast()[0][1]
                sensors.update({sensor[len("sensor_"):]: dict(data)})

    return render_template("index.html", data=sensors, info=get_info())


@app.route("/info")
@requires_auth
def sysinfo():
    return render_template("sysinfo.html", info=get_info(wide=True))


@app.route("/video")
@requires_auth
def video():
    # image = None
    # if os.path.exists(IMG_LAST):
        # image = file(IMG_LAST).read().strip()
    image = "lastimg.jpg.old.jpg"

    enabled = os.path.exists(VIDEO_ENABLED_FILE)

    return render_template("video.html", info=get_info(wide=True),
                           img=image, enabled=enabled)


@app.route("/video/disable")
@requires_auth
def disable_video():
    sh.rm('-f', VIDEO_ENABLED_FILE)
    return redirect('/video')


@app.route("/video/enable")
@requires_auth
def enable_video():
    sh.touch(VIDEO_ENABLED_FILE)
    return redirect('/video')


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
