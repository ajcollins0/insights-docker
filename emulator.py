# !/usr/bin/python
# Copyright (C) 2015 Red Hat, All rights reserved.
# AUTHORS: Alex Collins <alcollin@redhat.com>

import os
import util
import sys

""" Class that makes a mounted image/container rootfs
    emulate a normal machine's rootfs to allow
    redhat-access-insights code to run """


class Emulator:

    def __init__(self):
        self.dir_list = []
        self.define_dirs()
        self.create_dir_list()

    def define_dirs(self):
        """ define all directory paths """
        self.tmp_image_dir = "/var/tmp/tmp_image_dir/"
        self.insights_output_dir = "/var/tmp/docker/"
        self.insights_dir = "/var/tmp/insights-client"
        self.log_dir = "/var/tmp/log/"
        self.vartmp_dir = "/var/tmp/vartmp/"
        self.opt_dir = "/var/tmp/insights-client/opt/"
        self.tmp_python_dir = "/var/tmp/insights-client/opt/python"

    def create_dir_list(self):
        """ create a list of dir paths for easier creation/deletion """

        self.dir_list.append(self.tmp_image_dir)
        self.dir_list.append(self.insights_output_dir)
        self.dir_list.append(self.insights_dir)
        self.dir_list.append(self.log_dir)
        self.dir_list.append(self.vartmp_dir)
        self.dir_list.append(self.opt_dir)
        self.dir_list.append(self.tmp_python_dir)
        self.dir_list.append("./etc/")

    def create_dirs(self):
        """ creates a dir of every entry in self.dir_list """

        for d in self.dir_list:
            if not os.path.exists(d):
                cmd = ['mkdir', d]
                r = util.subp(cmd)
                if r.return_code != 0:
                    print "temp dirs did not mount"

    def remove_dirs(self):
        """ remove directories in dir_list with a few exception dirs """

        for d in self.dir_list:
            if d not in [self.insights_output_dir, self.insights_dir,
                         self.vartmp_dir]:
                cmd = ['rm', '-rf', d]
                r = util.subp(cmd)
                if r.return_code != 0:
                    print "temp dirs did not remove"

    def _first_mounts(self):
        """ Mount the intial directories into the rootfs  """

        dir_list = ["/sys", "/proc", "/dev", "/tmp", "etc"]
        for d in dir_list:
            cmd = ['mount', '-o', "bind", d, self.tmp_image_dir + d]
            r = util.subp(cmd)
            if r.return_code != 0:
                print "mounting broke"
                print d

    def unmount(self):
        """ unmount all mounted directories """
        dir_list = ["/var/tmp", "/var/log", "/mnt/opt/python",
                    "/mnt", "/etc/pki/consumer", "/root/",
                    "/sys", "/proc", "/dev", "/tmp", "etc"]
        for d in dir_list:
            cmd = ['umount', self.tmp_image_dir + d]
            r = util.subp(cmd)
            if r.return_code != 0:
                print "unmounting broke"
                print d

    def _second_mounts(self):
        """ Mount the second round of directories into the rootfs """
        cmds = []
        cmds.append(['mount', '-o', "bind", self.vartmp_dir, self.tmp_image_dir + "/var/tmp"])
        cmds.append(['mount', '-o', "bind", self.log_dir, self.tmp_image_dir + "/var/log"])
        cmds.append(['mount', '-o', "bind", self.insights_dir, self.tmp_image_dir + "/mnt"])
        cmds.append(['mount', '-o', "bind", "/usr/lib/python2.7/", self.tmp_image_dir + "mnt/opt/python"])
        cmds.append(['mount', '-o', "bind", "/etc/pki/consumer/", self.tmp_image_dir + "etc/pki/consumer"])
        cmds.append(['mount', '-o', "bind", "/root/", self.tmp_image_dir + "/root/"])

        for c in cmds:
            r = util.subp(c)
            if r.return_code != 0:
                print "second mount, broke"
                print c

    def _run_rsync(self):
        """ run rsync to pull out the rootfs /etc/ dir
            (later it is re-mounted inside the container so RHAI can edit
            any needed files """
        # rsync -aqPS ${IMAGE}/etc .
        if os.path.exists(self.tmp_image_dir + "etc/"):
            cmd = ['rsync', '-aqPS', self.tmp_image_dir + "etc/", "./etc/"]
            r = util.subp(cmd)
            if r.return_code != 0:
                print "rsync didn't copy correctly"

        # FIXME for some reason, some versions of RHEL containers don't have these dirs?
        # odd right?
        if not os.path.exists("./etc/pki"):
            cmd = ['mkdir', './etc/pki']
            r = util.subp(cmd)
            if r.return_code != 0:
                print "could not make temp pki directory"

        if not os.path.exists("./etc/pki/consumer"):
            cmd = ['mkdir', './etc/pki/consumer']
            r = util.subp(cmd)
            if r.return_code != 0:
                print "could not make temp consumer directory"

    def _copy_resolve_conf(self):
        """ copy the host machines resolve.conf and put it into the rootfs' /etc/ dir """
        cmd = ['cp', '/etc/resolv.conf', self.tmp_image_dir + '/etc/']
        r = util.subp(cmd)
        if r.return_code != 0:
            print "could not make copy host's resolve.conf"

    def _prep_etc_dir(self):
        """ remove the RHAI dir from the mounted etc dir in the rootfs and
            Copy the RHAI source code into the rootfs etc dir """

        cmds = []
        cmds.append(['rm', '-rf', self.tmp_image_dir + '/etc/redhat-access-insights'])
        cmds.append(['cp', '-r', self.insights_dir + '/etc/', self.tmp_image_dir + '/etc/redhat-access-insights'])
        for c in cmds:
            r = util.subp(c)
            if r.return_code != 0:
                print "could not final prep the image's etc directory"

    def _copy_launcher(self):
        """ copy the launching script into the rootfs/mnt dir """

        cmd = ['cp', './launcher.sh', self.tmp_image_dir + '/mnt/']
        r = util.subp(cmd)
        if r.return_code != 0:
            print "could not copy launcher!"

    def chroot_and_run(self):
        """ give the chroot cmda and run the launcher script in the rootfs """

        cmd = ['chroot', self.tmp_image_dir, '/mnt/launcher.sh']
        r = util.subp(cmd)
        if r.return_code != 0:
            print "could not chroot and run!"
            sys.exit()

    def gather_data(self, ims):
        """ Move the output dir into a designed output dir in /var/tmp/ """
        obj_type = ('images' if ims is True else 'containers')
        output_path = self.insights_output_dir + obj_type

        if not os.path.exists(output_path):
            cmd = ['mkdir', output_path]
            r = util.subp(cmd)
            if r.return_code != 0:
                print "could not make output directory"

        files = os.listdir(self.vartmp_dir)
        for f in files:
            cmd = ['mv', self.vartmp_dir + f, output_path]
            r = util.subp(cmd)
            if r.return_code != 0:
                print "could not move dir into output dir"
                print f
                print cmd

        self._remove_var_tmp_dir()

    def _remove_var_tmp_dir(self):
        """ remove the old location of where RHAI's output was stored """

        cmd = ['rm', '-rf', self.vartmp_dir]
        r = util.subp(cmd)
        if r.return_code != 0:
            print "vartmp dir did not remove"

    def intial_setup(self):
        """ Call all needed defs for setup in order"""

        self._run_rsync()
        self._first_mounts()
        self._second_mounts()
        self._copy_resolve_conf()
        self._prep_etc_dir()
        self._copy_launcher()

    def is_applicable(self):
        """ reutrn true if we can scan this image/container, false otherwise """

        etc_release_path = self.tmp_image_dir + "etc/redhat-release"
        if not os.path.exists(etc_release_path):
            return False

        os_release = open(etc_release_path).read()
        if 'Red Hat Enterprise Linux' in os_release and '7.' in os_release:
            return True
        else:
            return False
