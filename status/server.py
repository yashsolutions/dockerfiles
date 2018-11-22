#!/usr/bin/env python
import json
import os
import redis
import requests
import tornado.ioloop
import tornado.web

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        services = []
        servers = ["192.168.185.6"]
        try:
            for ip in servers:
                r = requests.get("http://" + ip + ":4243/services")
                services.extend(json.loads(r.text))
            r_server = redis.Redis(host='192.168.185.4', db=2)
        except Exception as e:
            print e

        output = "<img class=\"image-box-image-new\" src=\"https://storage.googleapis.com/wzukusers/user-25377885/images/58918da884b2fVqQXMFG/Yash-Logo_d400.png\" width=\"354\" height=\"236\" style=\"width: 200px;height: 150px;margin-top: -15px;margin-left: 0px;\">\
        <table><tr><th style=\"white-space:nowrap;\">ServiceName</th>\
        <th style=\"white-space:nowrap;\">Replicas</th><th>TargetPort</th>\
        <th style=\"white-space:nowrap;\">PublishedPort</th>\
        <th style=\"white-space:nowrap;\">OverlayIP</th>\
        <th style=\"white-space:nowrap;\">VirtualHost</th>\
        <th style=\"white-space:nowrap;\">ServicePing</th>\
        <th style=\"white-space:nowrap;\">HostTcpPing</th>\
        <th style=\"white-space:nowrap;\">HostStatus</th>\
        <th style=\"white-space:nowrap;\">ProxyStatus</th>\
        <th style=\"white-space:nowrap;\">Tag/Commit</th>\
        </tr>"

        for service in services:
            try:
                service_name = service['Spec']['Name']
            except:
                service_name = 'Unknown Service'

            try:
                image_tag = service['Spec']['TaskTemplate']['ContainerSpec']['Image'].split('@')[0].split(':')[1]
            except:
                image_tag = 'NA'


            try:
                replicas = str(service['Spec']['Mode']['Replicated']['Replicas'])
            except:
                replicas = 'NA'

            try:
                target_port = str(service['Endpoint']['Ports'][0]['TargetPort'])
            except:
                target_port = 'NA'

            try:
                published_port = str(service['Endpoint']['Ports'][0]['PublishedPort'])
            except:
                published_port = 'NA'

            try:
                virtual_host = ""
                for env in service['Spec']['TaskTemplate']['ContainerSpec']['Env']:
                    if 'VIRTUAL_HOST' in env:
                        virtual_host = env.split('=')[1]
            except:
                virtual_host = ""

            try:
                overlay_ip = "NA"
                for network in service['Endpoint']['VirtualIPs']:
                    if '10.254' in network['Addr']:
                        overlay_ip = network['Addr'].split('/')[0]
            except:
                overlay_ip = "NA"

            try:
                check = json.loads(r_server.get('check_' + service_name).replace("'",'"'))
                service_ping = check['service_ping'] if check['service_ping'] != 'FAILED' else '<font color=red>FAILED</font>'
                host_tcp = check['host_tcp'] if check['host_tcp'] != 'FAILED' else '<font color=red>FAILED</font>'
                host_response = str(check['host_response']) if check['host_response'] != 'NA' and check['host_response'] < 500 else '<font color=red>'+str(check['host_response'])+'</font>'
                proxy_response = str(check['proxy_response']) if check['proxy_response'] != 'NA' and check['proxy_response'] < 500 else '<font color=red>'+str(check['proxy_response'])+'</font>'
            except Exception as e:
                print e
                service_ping = 'NA'
                host_tcp = 'NA'
                container_response = 'NA'
                host_response = 'NA'
                proxy_response = 'NA'

            output += "<tr><td style=\"white-space:nowrap;\">" + service_name + \
                "</td><td style=\"white-space:nowrap;\">" + replicas + \
                "</td><td style=\"white-space:nowrap;\">" + target_port + \
                "</td><td style=\"white-space:nowrap;\">" + published_port + \
                "</td><td style=\"white-space:nowrap;\">" + overlay_ip + \
                "</td><td style=\"white-space:nowrap;\"><a href=\"http://" + virtual_host + "\">" + virtual_host + "</a>" + \
                "</td><td style=\"white-space:nowrap;\">" + service_ping + \
                "</td><td style=\"white-space:nowrap;\">" + host_tcp + \
                "</td><td style=\"white-space:nowrap;\">" + host_response + \
                "</td><td style=\"white-space:nowrap;\">" + proxy_response + \
                "</td><td style=\"white-space:nowrap;\">" + image_tag + \
                "</td></tr>"
        output += "</table>"
        self.write(output)

class FileHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/static/(.*)", FileHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(9000)
    tornado.ioloop.IOLoop.current().start()
