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


def mplayer():
    sh.cd(IMG_PATH)
    sh.mplayer("tv:/%s" % DEVICE, "-vo", "jpeg:quality=100", '-vf', 'scale=640:480', '-fps', '1')


def cleaner():
    sh.cd(IMG_PATH)
    while True:
        try:
            sh.rm("[0-9]*.jpg")
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
                if int(k) > 1000:
                    print "[%s] Found motion!! k=%s" % (time(), k)
                    RECORDING = True
                    last_treshold = time()

                # sleep(1)
        except:
            mplayer_p.terminate()
            cleaner_p.terminate()
