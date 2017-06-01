#!/usr/bin/env python
import requests
import json
import time
import filecmp
import os.path
import os
from subprocess import call

def are_dir_trees_equal(dir1, dir2):
        """
        Compare two directories recursively. Files in each directory are
        assumed to be equal if their names and contents are equal.

        @param dir1: First directory path
        @param dir2: Second directory path

        @return: True if the directory trees are the same and
        there were no errors while accessing the directories or files,
        False otherwise.
        """

        dirs_cmp = filecmp.dircmp(dir1, dir2)
        if len(dirs_cmp.left_only)>0 or len(dirs_cmp.right_only)>0 or                 len(dirs_cmp.funny_files)>0:
                return False
        (_, mismatch, errors) =  filecmp.cmpfiles(
                dir1, dir2, dirs_cmp.common_files, shallow=False)
        if len(mismatch)>0 or len(errors)>0:
                return False
        for common_dir in dirs_cmp.common_dirs:
                new_dir1 = os.path.join(dir1, common_dir)
                new_dir2 = os.path.join(dir2, common_dir)
                if not are_dir_trees_equal(new_dir1, new_dir2):
                        return False
        return True

call(["service", "nginx", "start"])
while True:
        try:
                call(["mkdir", "-p", "/old_config"])
                call(["cp", "-r", "/etc/nginx/sites-enabled/", "/old_config/"])
                ip_res = requests.get('http://reverse-proxy.'+os.environ['DEPLOY_ENV']+'.aptitudelabs.com:5000/get_my_ip')
                ip = json.loads(ip_res.text)['ip']

                res = requests.get('http://reverse-proxy.'+os.environ['DEPLOY_ENV']+'.aptitudelabs.com:4243/services')
                services = json.loads(res.text)

                for service in services:
                        try:
                                for env in service['Spec']['TaskTemplate']['ContainerSpec']['Env']:
                                        if 'VIRTUAL_HOST' in env:
                                                virtual_host = env.split('=')[1]
				for network in service['Endpoint']['VirtualIPs']:
					if '10.254' in network['Addr']:
						ip = network['Addr'].split('/')[0]
                                config = """
server {
        server_name """ + virtual_host + """;
        location / {
                proxy_pass http://""" + ip + """:""" + str(service['Endpoint']['Ports'][0]['TargetPort']) + """;
        }
}
"""
                                with open('/etc/nginx/sites-enabled/' + virtual_host, 'w') as config_file:
                                        config_file.write(config)
                        except Exception as e:
                                print e

        except Exception as e:
                print e
        if not are_dir_trees_equal("/etc/nginx/sites-enabled", "/old_config/sites-enabled"):
                call(["service", "nginx", "reload"])
        else:
                print "  no config change"
        time.sleep(60)

