# !/usr/bin/python
# Copyright (C) 2015 Red Hat, All rights reserved.
# AUTHORS: Alex Collins <alcollin@redhat.com>

import os
import util
import sys


class Emulator:

    def __init__(self):
        self.dir_list = []
        self.define_dirs()
        self.create_dir_list()

    def define_dirs(self):
        self.tmp_image_dir = "/var/tmp/tmp_image_dir/"
        self.insights_output_dir = "/var/tmp/docker/"
        self.insights_dir = "/var/tmp/insights-client"
        self.log_dir = "/var/tmp/log/"
        self.vartmp_dir = "/var/tmp/vartmp/"
        self.opt_dir = "/var/tmp/insights-client/opt/"
        self.tmp_python_dir = "/var/tmp/insights-client/opt/python"

    def create_dir_list(self):
        self.dir_list.append(self.tmp_image_dir)
        self.dir_list.append(self.insights_output_dir)
        self.dir_list.append(self.insights_dir)
        self.dir_list.append(self.log_dir)
        self.dir_list.append(self.vartmp_dir)
        self.dir_list.append(self.opt_dir)
        self.dir_list.append(self.tmp_python_dir)
        self.dir_list.append("./etc/")

    def create_dirs(self):
        for d in self.dir_list:
            if not os.path.exists(d):
                cmd = ['mkdir', d]
                r = util.subp(cmd)
                if r.return_code != 0:
                    print "temp dirs did not mount"

    def remove_dirs(self):
        for d in self.dir_list:
            if d not in [self.insights_output_dir, self.insights_dir,
                         self.vartmp_dir]:
                cmd = ['rm', '-rf', d]
                r = util.subp(cmd)
                if r.return_code != 0:
                    print "temp dirs did not remove"

    def first_mounts(self):
        dir_list = ["/sys", "/proc", "/dev", "/tmp", "etc"]
        for d in dir_list:
            cmd = ['mount', '-o', "bind", d, self.tmp_image_dir + d]
            r = util.subp(cmd)
            if r.return_code != 0:
                print "mounting broke"
                print d

    def unmount(self):
        dir_list = ["/var/tmp", "/var/log", "/mnt/opt/python",
                    "/mnt", "/etc/pki/consumer", "/root/",
                    "/sys", "/proc", "/dev", "/tmp", "etc"]
        for d in dir_list:
            cmd = ['umount', self.tmp_image_dir + d]
            r = util.subp(cmd)
            if r.return_code != 0:
                print "unmounting broke"
                print d

    def second_mounts(self):
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

    def run_rsync(self):
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

    def copy_resolve_conf(self):
        cmd = ['cp', '/etc/resolv.conf', self.tmp_image_dir + '/etc/']
        r = util.subp(cmd)
        if r.return_code != 0:
            print "could not make copy host's resolve.conf"

    def prep_etc_dir(self):
        cmds = []
        cmds.append(['rm', '-rf', self.tmp_image_dir + '/etc/redhat-access-insights'])
        cmds.append(['cp', '-r', self.insights_dir + '/etc/', self.tmp_image_dir + '/etc/redhat-access-insights'])
        for c in cmds:
            r = util.subp(c)
            if r.return_code != 0:
                print "could not final prep the image's etc directory"

    def copy_launcher(self):
        cmd = ['cp', './launcher.sh', self.tmp_image_dir + '/mnt/']
        r = util.subp(cmd)
        if r.return_code != 0:
            print "could not copy launcher!"

    def chroot_and_run(self):

        cmd = ['chroot', self.tmp_image_dir, '/mnt/launcher.sh']
        r = util.subp(cmd)
        if r.return_code != 0:
            print "could not chroot and run!"
            sys.exit()

    def intial_setup(self):

        self.run_rsync()
        self.first_mounts()
        self.second_mounts()
        self.copy_resolve_conf()
        self.prep_etc_dir()
        self.copy_launcher()
