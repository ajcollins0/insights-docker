# !/usr/bin/python
# Copyright (C) 2015 Red Hat, All rights reserved.
# AUTHORS: Alex Collins <alcollin@redhat.com>

import os
from docker_client import DockerClient
from mount import DockerMount, Mount, MountError
from emulator import Emulator


def mount_obj(path, obj, driver):

    DockerMount(path).mount(obj)

    # only need to bind-mount on the devicemapper driver
    if driver == 'devicemapper':
        DockerMount.mount_path(os.path.join(path, "rootfs"), path, bind=True)


def unmount_obj(path, driver):
    dev = DockerMount.get_dev_at_mountpoint(path)

    # If there's a bind-mount over the directory, unbind it.
    if dev.rsplit('[', 1)[-1].strip(']') == '/rootfs' \
            and driver == 'devicemapper':
        Mount.unmount_path(path)

    DockerMount(path).unmount()


def main():

    client = DockerClient()
    emu = Emulator()

    for im in client.images():
        print im[:12]
        try:

            emu.create_dirs()
            mount_obj(emu.tmp_image_dir, im, client.info()['Storage Driver'])
            emu.intial_setup()

            emu.chroot_and_run()

            emu.unmount()
            unmount_obj(emu.tmp_image_dir, client.info()['Storage Driver'])
            emu.remove_dirs()

        except MountError as dme:
            raise ValueError(str(dme))

if __name__ == '__main__':

    if os.geteuid() != 0:
            raise ValueError("This MUST must be run as root.")
    main()
