
import util
import sys
import json
from docker import Client

""" makeshift docker api suited for RHAI """

class DockerClient:

    def __init__(self):
        pass

    def info(self):
        """ returns a dict of all of the docker info data"""

        cmd = ['docker', 'info']
        out = util.subp(cmd)
        trim_out = out.stdout.strip()
        return_dict = {}
        for line in trim_out.split('\n'):
            tmp_list = line.split(':', 1)
            return_dict[tmp_list[0].strip()] = tmp_list[1].strip()

        return return_dict

    def images(self):
        """ returns a list of all image ids """

        cmd = ['docker', 'images', '-q', '--no-trunc']
        out = util.subp(cmd)
        trim_out = out.stdout.strip()
        return_list = []
        for line in trim_out.split('\n'):
            return_list.append(line)

        # return a set to remove dup ID's
        return list(set(return_list))

    def containers(self, running=True):
        """ returns a list of all container ids """

        if running:
            cmd = ['docker', 'ps', '-q', '--no-trunc']
        else:
            cmd = ['docker', 'ps', '-a', '-q', '--no-trunc']
        out = util.subp(cmd)
        trim_out = out.stdout.strip()
        return_list = []
        for line in trim_out.split('\n'):
            return_list.append(line)

        return return_list

    def inspect(self, obj_id):
        """ returns a dict of the inspection of a container or image """

        cmd = ['docker', 'inspect', obj_id]
        out = util.subp(cmd)
        trim_out = out.stdout.strip()
        ret = json.loads(trim_out[2:-2])
        return ret

    def is_a_container(self, obj_id):
        """ returns true if obj ID is a container ID"""

        conts = self.containers(False)
        if obj_id in conts:
            return True

        return False

    def is_an_image(self, obj_id):
        """ returns true if obj ID is a image ID"""

        ims = self.images()
        if obj_id in ims:
            return True

        return False

    def remove_container(self, cont_id):
        """ *force* removes the given container id, fails if
            container ID isn't found """

        cmd = ['docker', 'rm', '-f', cont_id]
        out = util.subp(cmd)

        if out.return_code is not 0:
            #FIXME RAISE EXCEPT HERE
            print "container ID not found, unable to remove object:"
            print cont_id

    def create_container(self, iid):
        """ creates a container from image iid and returns the new
            container's id """

        cmd = ['docker', 'create', '--env=_RHAI_TEMP_CONTAINER',
               iid, '/bin/true']
        out = util.subp(cmd)

        if out.return_code is not 0:
            #FIXME RAISE EXCEPT HERE
            print "container was not created"

        return out.stdout.strip()

    def commit(self, container):


        cmd = ['docker', 'commit', '-c', "ENV _RHAI_TEMP_CONTAINER=True", container]
        out = util.subp(cmd)
        if out.return_code is not 0:
            #FIXME RAISE EXCEPT HERE
            print "image was not commited"

        return out.stdout.strip()


    def remove_image(self, image_id):

        cmd = ['docker', 'rmi', '-f', image_id]
        out = util.subp(cmd)
        if out.return_code is not 0:
            #FIXME RAISE EXCEPT HERE
            print "image was not deleted"

    def _force_remove_all_temp_containers(self):
        """ inspects all contaiers and removes any that are
            temporary containers created by RHAI """

        conts = self.containers(False)
        tag = '_RHAI_TEMP_CONTAINER'

        for cid in conts:
            info = self.inspect(cid)
            if tag in info['Config']['Env']:
                self.remove_container(cid)

    def _force_remove_all_temp_images(self):
        """ inspects all images and removes any that are
            temporary containers created by RHAI """

        ims = self.images()
        tag = '_RHAI_TEMP_CONTAINER=True'

        for iid in ims:
            info = self.inspect(iid)
            if tag in info['Config']['Env']:
                self.remove_image(cid)

    def dprint(self, json_obj):
        """debug method for printing"""
        print json.dumps(json_obj, indent=2)

if __name__ == '__main__':

    x = DockerClient()

    temp = x.info()
    x.dprint(temp)
    