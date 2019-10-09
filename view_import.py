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

importsPath = os.getcwd()+'/imports/'

try:
	jenkins = JI(url=config['jenkins_import']['url'], 
			     user=config['jenkins_import']['user'], 
			     password=config['jenkins_import']['password'])
except Exception as e:
	cprint("An error occured: \n", "red")
	cprint(str(e) + "\n", "red")
	mylogger.error("An error occured at startup: " + str(e))
	exit()

def jobPathToUrl(path):
	urlPath = ''
	path = re.sub(importsPath, '', path)
	if path[0] == '/':
		path = path[1:]
	folders = path.split('/')
	for item in folders:
		if item != '':
			if folders.index(item) == 0:
				urlPath = '/view/' + item
			else:
				if item.endswith('.xml'):
					pass
				else:
					urlPath = urlPath + '/job/' + item
	return(urlPath)

def parseFolder(view, path):
	for item in os.listdir(path):
		myPath = path + '/' + item
		if os.path.isdir(myPath):
			print ("Found folder %s" % item)
			jenkins.createFolder(item, jobPathToUrl(path))
			parseFolder(view, myPath)
		else:
			print("Found job %s" % item)
			urlpath = jobPathToUrl(myPath)
			name = item.split('.')[0]
			jenkins.createNewJob(name, myPath, urlpath)



for item in os.listdir(importsPath):
	print("Creating view %s " % item)
	jenkins.createListView(item)
	print("Done")
	viewPath = importsPath + '/' + item
	parseFolder(item, viewPath)