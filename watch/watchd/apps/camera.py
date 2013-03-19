from time import sleep, time
import os
import datetime

import sh

from watchd import sensor

DEVICE = '/dev/video0'
IMG_PATH = '/home/aiko/pysmarthouse/resources/static/'
IMG_LAST = '/home/aiko/pysmarthouse/resources/static/lastimg.dat'
IMG_DB = '/home/aiko/diff/'


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

            while True:
                sh.cd(IMG_PATH)
                sh.mplayer("tv:/%s" % DEVICE, "-vo", "jpeg", "-frames", "1", '-vf', 'scale=640:480')
                # filename = "%s.jpg" % (
                #     datetime.datetime.isoformat(datetime.datetime.now()))
                filename = "lastimg.jpg"
                try:
                    sh.mv(filename, filename+".old")
                except sh.ErrorReturnCode:
                    pass

                try:
                    sh.mv('00000001.jpg', filename)
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

                k = sh.compare('-metric', 'AE', '-fuzz', '5%', 'lastimg.jpg',
                               'lastimg.jpg.old', 'diff.jpg', _err_to_out=True)
                if int(k) > 1000:
                    print "[%s] Found motion!!" % time()
                    RECORDING = True
                    last_treshold = time()

                # sleep(1)
        except:
            pass
