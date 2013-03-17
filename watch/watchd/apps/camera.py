from time import sleep
import os
import datetime

import sh

from watchd import sensor

DEVICE = '/dev/video0'
IMG_PATH = '/home/aiko/pysmarthouse/resources/static/'
IMG_LAST = '/home/aiko/pysmarthouse/resources/static/lastimg.dat'


@sensor
def photo():
    """
    Take photo
    """
    while True:
        if not os.path.exists(DEVICE):
            sleep(5)
            continue

        print "Device %s found" % DEVICE

        while True:
            sh.cd(IMG_PATH)
            sh.mplayer("tv:/%s" % DEVICE, "-vo", "jpeg", "-frames", "1")
            filename = "%s.jpg" % (
                datetime.datetime.isoformat(datetime.datetime.now()))
            sh.mv('00000001.jpg', filename)
            print >>file(IMG_LAST, 'w'), filename
