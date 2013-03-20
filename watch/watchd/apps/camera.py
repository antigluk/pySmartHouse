from time import sleep, time
import os
import sys
import datetime
import glob
import signal

from multiprocessing import Process

import sh

from watchd import sensor

DEVICE = '/dev/video0'
IMG_PATH = '/home/aiko/static'
IMG_LAST = '/home/aiko/static/lastimg.dat'
IMG_DB = '/home/aiko/diff/'
ENABLED_FILE = '/home/aiko/camera_enabled.marker'

processes = []


def kill_handler(signal, frame):
    print "Killed. Terminating childs..."
    for p in processes:
        print "kill %s" % p
        p.terminate()
    sys.exit(0)


def mplayer():
    sh.cd(IMG_PATH)
    while True:
        sh.rm('-f', glob.glob("[0-9]*.jpg"))
        sh.mplayer("tv:/%s" % DEVICE, "-vo", "jpeg:quality=100", '-vf', 'scale=320:240', '-fps', '2')


def cleaner():
    sh.cd(IMG_PATH)
    while True:
        try:
            sh.rm('-f', glob.glob("[0-9]*.jpg"))
        except sh.ErrorReturnCode:
            pass
        sleep(10)


@sensor
def photo():
    """
    Take photo
    """
    print "Camera daemon started"
    signal.signal(signal.SIGTERM, kill_handler)
    RECORDING = False
    last_treshold = 0
    lastname = None

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
            processes.append(mplayer_p)
            mplayer_p.start()
            print "mplayer started"

            cleaner_p = Process(target=cleaner)
            processes.append(cleaner_p)
            cleaner_p.start()
            print "cleaner started"

            while True:
                sh.cd(IMG_PATH)
                filename = "lastimg.jpg"

                if not os.path.exists(ENABLED_FILE):
                    print "[%s] Camera disabled... shutting down" % time()
                    mplayer_p.terminate()
                    cleaner_p.terminate()
                    processes.remove(mplayer_p)
                    processes.remove(cleaner_p)
                    sh.rm('-f', filename)
                    break

                try:
                    sh.cp('-f', filename, filename+".old.jpg")
                except sh.ErrorReturnCode:
                    pass

                try:
                    files = glob.glob("[0-9]*.jpg")
                    files.sort()
                    newname = files[-1]
                    if lastname != newname:
                        sh.mv(newname, filename)
                        lastname = newname
                    else:
                        print "[%s] No images yet (copy)" % time()
                except sh.ErrorReturnCode:
                    pass
                except IndexError:
                    print "[%s] No images yet" % time()
                    sleep(0.5)
                    continue

                print "[%s] Photo" % time()

                print >>file(IMG_LAST, 'w'), filename

                if RECORDING:
                    print "[%s] Recording..." % time()
                    filename_d = "%s.jpg" % (
                                 datetime.datetime.isoformat(datetime.datetime.now()))
                    sh.cp(filename, IMG_DB + filename_d)

                    if time() - last_treshold > 15:
                        RECORDING = False
                else:
                    k = sh.compare('-metric', 'AE', '-fuzz', '15%', 'lastimg.jpg',
                                   'lastimg.jpg.old.jpg', 'diff.jpg', _err_to_out=True)
                    if int(k) > 1500:
                        print "[%s] Found motion!! k=%s" % (time(), k)
                        RECORDING = True
                        last_treshold = time()

                # sleep(1)
        except Exception, e:
            print "[%s] Exception... shutting down. %s %s" % \
                (time(), e.__class__.__name__, e.message)
            mplayer_p.terminate()
            cleaner_p.terminate()
            processes.remove(mplayer_p)
            processes.remove(cleaner_p)
            sleep(1)
