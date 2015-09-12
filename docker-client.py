
import util
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
            tmp_list = line.split(':'[0])
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

        if self._is_a_container(obj_id):
            return self._container_inspect(obj_id)

        return self._image_inspect(obj_id)

    def _container_inspect(self, obj_id):
        pass
        #FIXME the return dicts will have multiple keys, need to make a 
        # to dict converter in util

    def _image_inspect(self, obj_id):
        pass

    def _is_a_container(self, obj_id):
        """ returns true if obj ID is a container ID"""

        conts = self.containers(False)
        if obj_id in conts:
            return True

        return False

    def dprint(self, json_obj):
        """debug method for printing"""

        print json.dumps(json_obj, indent=2)

if __name__ == '__main__':

    x = DockerClient()

    x.inspect("ea061f56e49899b605cb1157731a53f50fe97c35d714f2835e540253928dc9e0 ")


    #c = Client(base_url='unix://var/run/docker.sock')
    # print json.dumps(c.info(),indent=2)



