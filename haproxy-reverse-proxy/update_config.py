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
        if os.path.isfile(dir1) and os.path.isfile(dir2):
                return filecmp.cmp(dir1,dir2)
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

call(["service", "haproxy", "start"])
while True:
        try:
                call(["cp", "/etc/haproxy/haproxy.cfg", "/etc/haproxy/haproxy.prev"])
                ip_res = requests.get('http://reverse-proxy.internal.aptitudelabs.com:5000/get_my_ip')
                ip = json.loads(ip_res.text)['ip']

                res = requests.get('http://reverse-proxy.internal.aptitudelabs.com:4243/services')
                services = json.loads(res.text)
                frontend_config = ""
                backend_config = ""

                for service in services:
                        try:
                                service_name = service['Spec']['Name']
                                for env in service['Spec']['TaskTemplate']['ContainerSpec']['Env']:
                                        if 'VIRTUAL_HOST' in env:
                                                virtual_host = env.split('=')[1]
                                for network in service['Endpoint']['VirtualIPs']:
                                        if '10.254' in network['Addr']:
                                                ip = network['Addr'].split('/')[0]
                                backend_config += "backend " + service_name.replace("-","_") + "\n        server " + service_name.replace("-","_") + " 127.0.0.1:" + str(service['Endpoint']['Ports'][0]['PublishedPort']) + "\n"
                                frontend_config += "        use_backend " + service_name.replace("-","_") + " if { hdr(host) -i " + virtual_host + " }\n"
                        except Exception as e:
                                print e
                with open('/etc/haproxy/haproxy.cfg', 'w') as config_file:
                        config = """global
        daemon
        maxconn 4096

defaults
        mode http
        timeout connect 5000ms
        timeout client 50000ms
        timeout server 50000ms

frontend localhost
        mode http
        bind *:80\n"""
                        config = config + frontend_config + backend_config
                        config_file.write(config)

        except Exception as e:
                print e
        if not are_dir_trees_equal("/etc/haproxy/haproxy.cfg", "/etc/haproxy/haproxy.prev"):
                call(["service", "haproxy", "reload"])
        else:
                print "  no config change"
        time.sleep(60)
