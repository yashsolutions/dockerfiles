#!/usr/bin/env python
import tornado.ioloop
import tornado.web
import json
import redis
import requests
import jenkins
import re
from xml.etree import ElementTree

username = 'ashish.nanotkar'
password = '1561164d4c145077d7fd3aaeb5d2479e'

class SubmitHandler(tornado.web.RequestHandler):
    def post(self):
	try:
	    param_string = self.get_argument('params')
      	    param_lines = param_string.split("\n")
	
  	    params = {}
	    for line in param_lines:
		params[line.split('=')[0]] = ('='.join(line.split('=')[1:])).strip(" '\"\r\n")
	    server = jenkins.Jenkins('http://jenkins.internal.aptitudelabs.com/', username=username, password=password)
  	    server.build_job('SRKay/common/deploy-to-swarm', params, token=password)
	
	    output = "Deployment submitted for tag " + params['GIT_COMMIT'] + " of " + params['SERVICE'] + " on " + params['DEPLOY_ENV'] + " environment<br><a href='http://jenkins.internal.aptitudelabs.com/job/SRKay/job/common/job/deploy-to-swarm/'>Check deployment job</a><br>"
	except Exception as e:
	    output = "Bad request. " + str(e)
	output += "<br><a href='/'>Check tags</a> or <a href='http://status.internal.aptitudelabs.com'>Check status</a><br>"
	self.write(output)

class DeployHandler(tornado.web.RequestHandler):
    def post(self):
	output = "<a href='/'>Check tags</a> or <a href='http://status.internal.aptitudelabs.com'>Check status</a><br><br>"

	success = True
	try:
		config = requests.get('http://jenkins.internal.aptitudelabs.com/job/SRKay/job/system/job/' + self.get_argument('service') + '/config.xml', auth=(username, password))
		tree = ElementTree.fromstring(config.content)
		param_lines = tree.findall('.//hudson.plugins.parameterizedtrigger.PredefinedBuildParameters/properties')[0].text.split("\n")
		param_string = ""
                params = {}
                for line in param_lines:
                    params[line.split('=')[0]] = ('='.join(line.split('=')[1:])).strip(" '\"\r\n")
		params['GIT_COMMIT'] = self.get_argument('tag')
                params['DEPLOY_ENV'] = self.get_argument('env')
                for key, value in params.iteritems():
                    param_string += key + "=" + value + "\r"
	except Exception as e:
	    print e
	    try:
	
		config = requests.get('http://jenkins.internal.aptitudelabs.com/job/SRKay/job/' + self.get_argument('service') + '/job/pipeline/config.xml', auth=(username, password))
		tree = ElementTree.fromstring(config.content)
		m = re.findall('string\(name\:(.*)? value\:(.*)\)', tree.findall('.//script')[0].text)
		param_string = ""
		params = {}
		for content in m:
		    params[content[0].strip(", '\"")] = content[1].strip(", \r\n")
		params['GIT_COMMIT'] = self.get_argument('tag')
		params['DEPLOY_ENV'] = self.get_argument('env')
		for key, value in params.iteritems():
		    param_string += key + "=" + value + "\r"
	    except Exception as e:
		print e
		success = False
	        param_string = 'I am sorry. I was not able to get deployment parameters. Does the job name and format on Jenkins follow the standards?'
	if success:
		output += '<form action=/submit method=post>Deployment Params:<br><textarea rows=15 cols=100 name=params>' + param_string + '</textarea> <br><br><input type=submit value=Deploy></form>'
	else:
		output += param_string

	self.write(output)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
	services = []
	output = ""
        try:
	    for ip in ["internal-swarm-01.ip", "prod-swarm-01.ip"]:
	            r = requests.get("http://" + ip + ":4243/services")
        	    services.extend(json.loads(r.text))
            r_server = redis.Redis(host='ansible.ip', db=2)
        except Exception as e:
            print e

	app_services = {}
	sys_services = []
	envs = ['qa', 'dev', 'stage', 'internal', 'prod']
	app_envs = []
        for service in services:
	    info = {}
            try:
                info['name'] = '-'.join(service['Spec']['Name'].split("-")[1:])
                info['env'] = service['Spec']['Name'].split("-")[0]
		if info['env'] not in app_envs:
                        sys_services.append(info['name'])
		if info['env'] == 'internal' and info['name'] not in sys_services:
			sys_services.append(info['name'])
            except Exception as e:
		print e
	    
	    if info['name'] not in app_services.keys():
		app_services[info['name']] = {}
            try:
                info['image_tag'] = service['Spec']['TaskTemplate']['ContainerSpec']['Image'].split('@')[0].split(':')[1]
            except:
                info['image_tag'] = '-'
	    try:
                info['virtual_host'] = ""
                for env in service['Spec']['TaskTemplate']['ContainerSpec']['Env']:
                    if 'VIRTUAL_HOST' in env:
                        info['virtual_host'] = env.split('=')[1]
            except:
                info['virtual_host'] = ""

            try:
                info['replicas'] = str(service['Spec']['Mode']['Replicated']['Replicas'])
            except:
                info['replicas'] = '-'
	
	    app_services[info['name']][info['env']] = info

	output += "<a href='http://status.internal.aptitudelabs.com'>Check service status</a><br><form method=post action='/deploy'>Deploy tag: <input type=text name=tag> of <select name=service>"
	for name in app_services.keys():
	    output += "<option vaule=\"" + name + "\">" + name + "</option>"
	output += "</select> on <select name=env>"
	for env in envs:
	    output += "<option vaule=\"" + env + "\">" + env + "</option>"
	output += "</select> <input type=submit value=deploy></form>"
	output += "<table><tr><th style=\"white-space:nowrap;text-align:left\">service name</th>\
        <th style=\"white-space:nowrap;text-align:left\">qa</th>\
        <th style=\"white-space:nowrap;text-align:left\">dev</th>\
        <th style=\"white-space:nowrap;text-align:left\">stage</th>\
        <th style=\"white-space:nowrap;text-align:left\">internal</th>\
        <th style=\"white-space:nowrap;text-align:left\">prod</th>\
        </tr>"

	for name, service in app_services.iteritems():
	    output += "<tr><td style=\"white-space:nowrap;\">" + name + "</td>"
	    for env in envs:
		tag = service[env]['image_tag'] if env in service.keys() else '-'
                output += "<td style=\"white-space:nowrap;\">" + tag + "</td>"
        output += "</tr></table>"
        self.write(output)

class FileHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/deploy", DeployHandler),
        (r"/submit", SubmitHandler),
        (r"/static/(.*)", FileHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(9000)
    tornado.ioloop.IOLoop.current().start()
