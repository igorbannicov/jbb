#!/usr/local/bin/python3

import os
import re
import logging
import logging.config
import configparser
from pprint import pprint as pp
from lib.jenkinsinstance import JenkinsInstance as JI
from lib.utils import *


config = configparser.ConfigParser()
config.read('config.ini')
logging.config.fileConfig('config.ini')
mylogger = logging.getLogger('CORE')
mylogger.info("Starting application")

jobs = []
folders = []

try:
	jenkins = JI(url=config['jenkins_import']['url'], 
			     user=config['jenkins_import']['user'], 
			     password=config['jenkins_import']['password'])
except Exception as e:
	cprint("An error occured: \n", "red")
	cprint(str(e) + "\n", "red")
	mylogger.error("An error occured at startup: " + str(e))
	exit()


def parseFolder(folder):
	items = ()
	items = jenkins.getJobsFromFolder(folder)
	if items != ():
		for entry in items:
			for item in entry:
				if item['_class'] == 'com.cloudbees.hudson.plugins.folder.Folder':
					print ("Found folder %s" % item['name'])
					parseFolder(item)
				else:
					print("Found job %s" % item['name'])
					jenkins.deleteJob(item)
	jenkins.deleteJob(folder)

view = jenkins.selectView()
mylogger.info("Dumping Jenkins view")
try:
	print("Deleting view %s " % view['name'])
	path = '/view/'+view['name']
	items = jenkins.getJobsFromView(view['name'])
	for item in items:
		path = path + '/job/'+item['name']
		if item['_class'] == 'com.cloudbees.hudson.plugins.folder.Folder':
			parseFolder(item)
		if item['_class'] != 'com.cloudbees.hudson.plugins.folder.Folder':
			print('Deleting job %s ' % item['name'])
			jenkins.deleteJob(item)
	jenkins.deleteView(view)
except Exception as e:
	mylogger.error("An error occured: " + str(e))
	exit()
