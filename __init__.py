# !/usr/bin/python
# Copyright (C) 2015 Red Hat, All rights reserved.
# AUTHORS: Alex Collins <alcollin@redhat.com>

import os
from docker_client import DockerClient
from mount import DockerMount, Mount, MountError
from emulator import Emulator


def mount_obj(path, obj, driver):
    """ mounts the obj to the given path """

    DockerMount(path).mount(obj)

    # only need to bind-mount on the devicemapper driver
    if driver == 'devicemapper':
        DockerMount.mount_path(os.path.join(path, "rootfs"), path, bind=True)


def unmount_obj(path, driver):
    """ unmount the given path """

    dev = DockerMount.get_dev_at_mountpoint(path)

    # If there's a bind-mount over the directory, unbind it.
    if dev.rsplit('[', 1)[-1].strip(']') == '/rootfs' \
            and driver == 'devicemapper':
        Mount.unmount_path(path)

    DockerMount(path).unmount()


def remove_old_data():
    """ deleted old output """

    import util
    cmd = ['rm', '-rf', "/var/tmp/docker/"]
    r = util.subp(cmd)
    if r.return_code != 0:
        print "old data was not deleted"


def scan(images=True):
    """ scanning method that will scan all images or containers """

    client = DockerClient()
    emu = Emulator()

    objs = client.images() if images is True else client.containers()

    # If there are no images/containers on the machine, objs will be ['']
    if objs == ['']:
        return

    # does actual work here!
    for im in objs:
        try:
            emu.create_dirs()
            mount_obj(emu.tmp_image_dir, im, client.info()['Storage Driver'])

            if emu.is_applicable():

                print "scanning " + im[:12]
                emu.intial_setup()

                emu.chroot_and_run()

                emu.unmount()
            else:
                print im[:12] + " is not RHEL based"

            unmount_obj(emu.tmp_image_dir, client.info()['Storage Driver'])
            emu.remove_dirs()

        except MountError as dme:
            raise ValueError(str(dme))

    emu.gather_data(images)


def main():

    remove_old_data()
    print "Scanning Images:"
    scan(True)
    print "Scanning Containers:"
    scan(False)

if __name__ == '__main__':

    if os.geteuid() != 0:
            raise ValueError("This MUST must be run as root.")
    main()
