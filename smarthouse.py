"""
Front-end web application, shows sensors and allow some control
"""

from flask import Flask, render_template

import watch

import sh

app = Flask(__name__)

def get_info():
    return {"host": sh.hostname().strip(),
            "ip": sh.hostname("-i").strip(),
            }

@app.route("/")
def index():
    sensors = []
    for sensor in watch.WATCH_LIST:
        data = file(watch.LOG_PATH_FORMAT % sensor).readlines()
        sensors.append({"name":sensor, "data":[line.strip().split("=") for line in data]})

    return render_template("index.html", data=sensors, info=get_info())

if __name__ == "__main__":
    app.run(debug = True)