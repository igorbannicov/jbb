#!/usr/local/bin/python3

import os
import logging
import logging.config
import configparser
from pprint import pprint as pp
from lib.jenkinsinstance import JenkinsInstance as JI
from lib.bitbucketinstance import BitBucketInstance as BI
from lib.utils import *


finished = False
config = configparser.ConfigParser()
config.read('config.ini')
logging.config.fileConfig('config.ini')
mylogger = logging.getLogger('CORE')
mylogger.info("Starting application")

try:
	bucket = BI(url=config['bitbucket']['url'],
				user=config['bitbucket']['user'], 
				password=config['bitbucket']['password'])
	jenkins = JI(url=config['jenkins']['url'], 
			     user=config['jenkins']['user'], 
			     password=config['jenkins']['password'])
except Exception as e:
	cprint("An error occured: \n", "red")
	cprint(str(e) + "\n", "red")
	mylogger.error("An error occured at startup: " + str(e))
	exit()

menu_items = ['View Jenkins job', 			#1
              'Create Jenkins job', 		#2
              'Delete Jenkins job', 		#3
              'Delete Jenkins view',		#4
              'View PR notifications',		#5
              'Create PR notification',		#6
              'Delete PR notification', 	#7
              'Quit']						#8

def viewJenkinsJob():
	mylogger.info("View Jenkins job")
	try:
		view = jenkins.selectView()
		job = jenkins.selectJob(view['name'])
		jobcfg = jenkins.getJobDetails(job)
		pp(jobcfg)
	except Exception as e:
		mylogger.error("An error occured: " + str(e))
		exit()

def createJenkinsJob():
	mylogger.info("Create Jenkins job")
	try:
		print("Not implemented yet.")
	except Exception as e:
		mylogger.error("An error occured: " + str(e))
		exit()

def deleteJenkinsJob():
	mylogger.info("Delete Jenkins job")
	try:
		view = jenkins.selectView()
		job = jenkins.selectJob(view['name'])
		jobcfg = jenkins.getJobDetails(job)
		jenkins.deleteJob(job)
	except Exception as e:
		mylogger.error("An error occured: " + str(e))
		exit()

def notificationsView():
	mylogger.info("Notifications view")
	try:
		project = bucket.selectProject()
		repo = bucket.selectRepo(project)
		notifications = bucket.getNotifications(project=project, repo=repo)
		for notification in notifications:
			print('{:30}'.format(notification['name']) + notification['uuid'])
	except Exception as e:
		mylogger.error("An error occured: " + str(e))
		exit()

def notificationCreate():
	mylogger.info("Create notification")
	try:
		view = jenkins.selectView()
		job = jenkins.selectJob(view)
		token = jenkins.getJobDetails(job)['authToken']
		url = jenkins.url + '/view/' + view + '/job/' + job + '/buildWithParameters?token=' + token + '&${EVERYTHING_URL}'
		bucket.addNotification(url, jenkins_user, jenkins_password)
	except Exception as e:
		mylogger.error("An error occured: " + str(e))
		exit()

def notificationDelete():
	mylogger.info("Delete Notification")
	try:
		project = bucket.selectProject()
		repo = bucket.selectRepo(project)
		notification = bucket.selectNotification(project, repo)
		pp(notification)
		print(colored("Are you sure you want to delete this PR Notification? (Y/N) ", 'red'), end='')
		confirm = input()
		confirm = confirm.upper()
		if confirm == "Y":
			bucket.deleteNotification(notification['uuid'])
	except Exception as e:
		mylogger.error("An error occured: " + str(e))
		exit()



while not finished:
	os.system('clear')
	print('\t Select an option\n')
	for x in range(len(menu_items)):
		cprint('{:2}'.format(str(x + 1)), "orange")
		print(" ...... " + menu_items[x])
	print('\n')
	key = getch()
	try:
		option = int(key)
		if option == 1:
			viewJenkinsJob()
			getch()
		if option == 2:
			createJenkinsJob()
			getch()
		if option == 3:
			deleteJenkinsJob()
			getch()
		if option == 4:
			deleteJenkinsView()
			getch()
		if option == 5:
			notificationsView()
			getch()
		if option == 6:
			notificationCreate()
			getch()
		if option == 7:
			notificationDelete()
			getch()
		elif option == 8:
			mylogger.info("Exit")
			finished = True
			exit()
		else:
			pass
	except:
		if key == 'q':
			mylogger.info("Exit")
			exit()
		else:
			pass
