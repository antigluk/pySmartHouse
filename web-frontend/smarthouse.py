"""
Front-end web application, shows sensors and allow some control
"""

from flask import Flask, render_template

from watchd import watch, LOG_PATH, LOG_PATH_FORMAT

import sh
import os
import fnmatch

app = Flask(__name__)

def get_info():
    return {"host": sh.hostname().strip(),
            "ip": sh.hostname("-i").strip(),
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
            sensors.append({"name":sensor, "data":[line.strip().split("=") for line in data]})

    return render_template("index.html", data=sensors, info=get_info())

if __name__ == "__main__":
    app.run(debug = True, host='0.0.0.0')