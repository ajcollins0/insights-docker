
import util
import json


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
        """ returns a list of all iamge ids """

        cmd = ['docker', 'images', '-q', '--no-trunc']
        out = util.subp(cmd)
        trim_out = out.stdout.strip()
        return_list = []
        for line in trim_out.split('\n'):
            return_list.append(line)

        return return_list

    def dprint(self, json_obj):
        """debug method for printing"""

        print json.dumps(json_obj,indent=2)

if __name__ == '__main__':

    x = DockerClient()
    tmp = x.images()

    for line in tmp:
        print line

    x.dprint(x.info())
