from flask import Flask, render_template

import watch

app = Flask(__name__)

@app.route("/")
def hello():
    sensors = []
    for sensor in watch.WATCH_LIST:
        data = file(watch.LOG_PATH_FORMAT % sensor).readlines()
        sensors.append({"name":sensor, "data":[line.strip().split("=") for line in data]})

    return render_template("index.html", data=sensors)

if __name__ == "__main__":
    app.run(debug = True)