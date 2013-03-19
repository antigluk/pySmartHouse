from time import sleep, time
import os
import datetime
import glob

from multiprocessing import Process

import sh

from watchd import sensor

DEVICE = '/dev/video0'
IMG_PATH = '/home/aiko/pysmarthouse/resources/static/'
IMG_LAST = '/home/aiko/pysmarthouse/resources/static/lastimg.dat'
IMG_DB = '/home/aiko/diff/'
ENABLED_FILE = '/home/aiko/camera_enabled.marker'


def mplayer():
    sh.cd(IMG_PATH)
    sh.rm('-f', "[0-9]*.jpg")
    sh.mplayer("tv:/%s" % DEVICE, "-vo", "jpeg:quality=100", '-vf', 'scale=640:480', '-fps', '1')


def cleaner():
    sh.cd(IMG_PATH)
    while True:
        try:
            sh.rm('-f', "[0-9]*.jpg")
        except sh.ErrorReturnCode:
            pass
        sleep(10)


@sensor
def photo():
    """
    Take photo
    """
    print "Camera daemon started"
    RECORDING = False
    last_treshold = 0

    sh.mkdir('-p', IMG_DB)
    while True:
        try:
            print "Looking up for %s" % DEVICE
            if not os.path.exists(DEVICE):
                sleep(5)
                continue

            if not os.path.exists(ENABLED_FILE):
                print "[%s] Camera still disabled..." % time()
                sleep(5)
                continue

            print "Device %s found" % DEVICE

            mplayer_p = Process(target=mplayer)
            mplayer_p.start()
            print "mplayer started"

            cleaner_p = Process(target=cleaner)
            cleaner_p.start()
            print "cleaner started"

            while True:
                sh.cd(IMG_PATH)
                filename = "lastimg.jpg"

                if not os.path.exists(ENABLED_FILE):
                    print "[%s] Camera disabled... shutting down" % time()
                    mplayer_p.terminate()
                    cleaner_p.terminate()
                    sh.rm('-f', filename)
                    break

                try:
                    sh.mv(filename, filename+".old")
                except sh.ErrorReturnCode:
                    pass

                try:
                    files = glob.glob("[0-9]*.jpg")
                    files.sort()
                    sh.mv(files[-1], filename)
                except sh.ErrorReturnCode:
                    pass

                print "[%s] Photo" % time()

                print >>file(IMG_LAST, 'w'), filename

                if RECORDING:
                    print "[%s] Recording..." % time()
                    filename_d = "%s.jpg" % (
                                 datetime.datetime.isoformat(datetime.datetime.now()))
                    sh.cp(filename, IMG_DB + filename_d)

                    if time() - last_treshold > 30:
                        RECORDING = False

                k = sh.compare('-metric', 'AE', '-fuzz', '15%', 'lastimg.jpg',
                               'lastimg.jpg.old', 'diff.jpg', _err_to_out=True)
                if int(k) > 1500:
                    print "[%s] Found motion!! k=%s" % (time(), k)
                    RECORDING = True
                    last_treshold = time()

                # sleep(1)
        except:
            mplayer_p.terminate()
            cleaner_p.terminate()
