#!/usr/bin/env python
import requests
import redis
import json
import socket
import time
import os

while True:
    try:
        service_check = {}
        r_server = redis.Redis(host='192.168.185.4', db=2)
        services = []
        servers = ["192.168.185.6"]
        for ip in servers:
            r = requests.get("http://" + ip + ":4243/services")
            services.extend(json.loads(r.text))
        counter = 1
        for service in services:
            try:
                service_name = service['Spec']['Name']
            except Exception as e:
                print e
                service_name = 'unknown-service-' + str(counter)

            host_ip = "192.168.185.6"

            try:
                replicas = str(service['Spec']['Mode']['Replicated']['Replicas'])
            except Exception as e:
                print e
                replicas = 'NA'

            try:
                target_port = str(service['Endpoint']['Ports'][0]['TargetPort'])
            except Exception as e:
                print e
                target_port = 'NA'

            try:
                published_port = str(service['Endpoint']['Ports'][0]['PublishedPort'])
            except Exception as e:
                print e
                published_port = 'NA'

            try:
                virtual_host = ""
                for env in service['Spec']['TaskTemplate']['ContainerSpec']['Env']:
                    if 'VIRTUAL_HOST' in env:
                        virtual_host = env.split('=')[1]
            except Exception as e:
                print e
                virtual_host = ""

            try:
                ip = "NA"
                for network in service['Endpoint']['VirtualIPs']:
                    if '10.254' in network['Addr']:
                        ip = network['Addr'].split('/')[0]
            except Exception as e:
                print e
                ip = "NA"
            """
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex((ip, int(target_port)))
                overlay_tcp = 'OK' if not result else 'FAILED'
            except Exception as e:
                print e
                overlay_tcp = 'FAILED' if target_port != 'NA' else 'NA'
            """
            try:
                ping = os.system("ping -c 1 " + service_name)
                service_ping = 'OK' if ping == 0 else 'FAILED'
            except Exception as e:
                print e
                service_ping = 'FAILED'

            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex((host_ip, int(published_port)))
                host_tcp = 'OK' if not result else 'FAILED'
            except Exception as e:
                print e
                host_tcp = 'FAILED' if target_port != 'NA' else 'NA'
            """
            try:
                r = requests.get('http://' + ip + ":" + target_port, timeout=1)
                container_response = r.status_code
            except Exception as e:
                print e
                container_response = 'NA'
            """
            try:
                r = requests.get('http://' + host_ip + ":" + published_port, timeout=1)
                host_response = r.status_code
            except Exception as e:
                print e
                host_response = 'NA'

            try:
                r = requests.get('http://' + virtual_host, timeout=1)
                proxy_response = r.status_code
            except Exception as e:
                print e
                proxy_response = 'NA'
            counter += 1
            r_server.set('check_' + service_name, {
                #'overlay_tcp': overlay_tcp,
                'service_ping': service_ping,
                'host_tcp': host_tcp,
                #'container_response': container_response,
                'host_response': host_response,
                'proxy_response': proxy_response
                })
            time.sleep(1)

    except Exception as e:
        print e
    time.sleep(1)
