# !/usr/bin/python
# Copyright (C) 2015 Red Hat, All rights reserved.
# AUTHORS: Alex Collins <alcollin@redhat.com>

import os
import util 
import docker

from mount import DockerMount, Mount, MountError

if __name__ == '__main__':
    
    if os.geteuid() != 0:
            raise ValueError("This command must be run as root.")

    client = docker.Client(base_url='unix://var/run/docker.sock')

    for im in client.images(quiet=True):
    
        print im
        try:
            print "mounting first thing"
            DockerMount('tmp/').mount(im)

            print "attempting to mount the rootfs"
            # only need to bind-mount on the devicemapper driver
            if client.info()['Driver'] == 'devicemapper':
                DockerMount.mount_path(os.path.join('tmp/', "rootfs"), 'tmp/', bind=True)

            print "attempting unmount"

            dev = DockerMount.get_dev_at_mountpoint('tmp/')

            # If there's a bind-mount over the directory, unbind it.
            if dev.rsplit('[', 1)[-1].strip(']') == '/rootfs' \
                    and client.info()['Driver'] == 'devicemapper':
                Mount.unmount_path('tmp/')

            DockerMount('tmp/').unmount()


        except MountError as dme:
            raise ValueError(str(dme))

