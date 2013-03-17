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
    RECORDING = False
    last_treshold = 0

    sh.mkdir('-p', IMG_DB)
    while True:
        if not os.path.exists(DEVICE):
            sleep(5)
            continue

        print "Device %s found" % DEVICE

        while True:
            sh.cd(IMG_PATH)
            sh.mplayer("tv:/%s" % DEVICE, "-vo", "jpeg", "-frames", "1")
            # filename = "%s.jpg" % (
            #     datetime.datetime.isoformat(datetime.datetime.now()))
            filename = "lastimg.jpg"
            sh.mv(filename, filename+".old")
            sh.mv('00000001.jpg', filename)
            print >>file(IMG_LAST, 'w'), filename

            if RECORDING:
                filename_d = "%s.jpg" % (
                             datetime.datetime.isoformat(datetime.datetime.now()))
                sh.cp(filename, IMG_DB + filename_d)

                if time() - last_treshold > 10:
                    RECORDING = False

            k = sh.compare('-metric', 'AE', '-fuzz', '5%', 'lastimg.jpg',
                           'lastimg.jpg.old')
            if k > 2000:
                RECORDING = True
                last_treshold = time()

            sleep(1)
