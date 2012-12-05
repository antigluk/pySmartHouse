"""
Front-end web application, shows sensors and allow some control
"""

from flask import Flask, render_template

import watch

import sh
import os

app = Flask(__name__)

def get_info():
    return {"host": sh.hostname().strip(),
            "ip": sh.hostname("-i").strip(),
            }

@app.route("/")
def index():
    sensors = []
    for sensor in watch.WATCH_LIST:
        file_name = watch.LOG_PATH_FORMAT % sensor
        if os.path.exists(file_name):
            data = file(file_name).readlines()
            sensors.append({"name":sensor, "data":[line.strip().split("=") for line in data]})

    return render_template("index.html", data=sensors, info=get_info())

if __name__ == "__main__":
    app.run(debug = False, host='0.0.0.0')