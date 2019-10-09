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
jobs = []
folders = []

## Init jenkins object
try:
	jenkins = JI(url=config['jenkins']['url'], 
			     user=config['jenkins']['user'], 
			     password=config['jenkins']['password'])
except Exception as e:
	cprint("An error occured: \n", "red")
	cprint(str(e) + "\n", "red")
	mylogger.error("An error occured at startup: " + str(e))
	exit()

## Create folder procedure
def make_folder(path):
	try:
		if not os.path.exists(path):
			os.makedirs(path)
			print("Successfully created the directory %s " % path)
		else:
			print("Directory %s already exists" % path)
	except OSError:
	    print ("Creation of the directory %s failed" % path)

## Transform object url to os path
def urlToPath(view, url):
	cleanUrl = re.sub(jenkins.url, '', url)
	cleanPath = re.sub('/job', '', cleanUrl)
	path = importsPath+view+cleanPath
	return(path)

def processFolder(view, folder):
	folderPath = urlToPath(view, folder['url'])
	make_folder(folderPath)
	jobItems, folderItems = jenkins.getJobsFromFolder(folder)
	for itemFolder in folderItems:
		processFolder(view, itemFolder)
	for jobItem in jobItems:
		jobPath = folderPath+'/'+jobItem['name'] + '.xml'
		f= open(jobPath,"w")
		jobcfg = jenkins.getJobDetails(jobItem)
		f.write(jobcfg)
		f.close

mylogger.info("Dumping Jenkins view")
try:
	view = jenkins.selectView()
	items = jenkins.getJobsFromView(view['name'])
	viewPath = importsPath+view['name']
	make_folder(viewPath)
	for item in items:
		if item['_class'] != 'com.cloudbees.hudson.plugins.folder.Folder':
			jobPath = viewPath + '/' + item['name'] + '.xml'
			f= open(jobPath,"w")
			jobcfg = jenkins.getJobDetails(item)
			f.write(jobcfg)
			f.close
		if item['_class'] == 'com.cloudbees.hudson.plugins.folder.Folder':
			processFolder(view['name'], item)
except Exception as e:
	mylogger.error("An error occured: " + str(e))
	exit()
