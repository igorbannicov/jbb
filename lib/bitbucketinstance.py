import os
import requests
import json
import logging
from urllib.parse import urlparse
from pprint import pprint as pp
from .utils import *


triggers_list = ['APPROVED', 
				 'COMMENTED',
 				 'DECLINED',
 				 'DELETED',
 				 'MERGED',
 				 'OPENED',
 				 'BUTTON_TRIGGER',
 				 'REOPENED',
                 'RESCOPED_FROM',
 			     'RESCOPED_TO',
 				 'REVIEWED',
 				 'UNAPPROVED',
                 'UPDATED']

filters_list = ['NONE', 'PULL_REQUEST_TO_BRANCH', 'BUTTON_TRIGGER_TITLE']

class BitBucketInstance:


	def __init__(self, url='http://localhost:8080', user = 'admin', password = 'admin'):
		u = urlparse(url)
		self.logger = logging.getLogger("M::BitBucket")
		self._url_ = u.netloc
		self._user_ = user
		self._password_ = password
		self._api_ = u.scheme + '://' + u.netloc + '/rest/api/1.0/'  # BitBucket Stash API URL
		self._napi_ = u.scheme + '://' + u.netloc + '/rest/prnfb-admin/1.0/settings/notifications' # BitBucket Stash Pull Request Notifier API URL
		self._bapi_ = u.scheme + '://' + u.netloc + '/rest/prnfb-admin/1.0/settings/buttons' # BitBucket Stash Pull Request Notifier Buttons API URL
		self.logger.info("Module initialized")

	# Get list of all available projects
	def getProjects(self):
		self.logger.info("Getting projects list")
		try:
			plist = []
			url = self._api_ + 'projects/'
			rq = requests.get(url, auth=(self._user_, self._password_))
			x = 0
			for item in rq.json()['values']:
				plist.append(item['key'])
			return plist
		except Exception as e:
			self.logger.error("An error occured: " + str(e))
			exit()

	# Get list of all available repos in a project
	def getRepos(self, project):
		self.logger.info("Getting repos list from "+project)
		try:
			rlist = []
			url = self._api_ + 'projects/' + project + '/repos?limit=999'
			rq = requests.get(url, auth=(self._user_, self._password_))
			x = 0
			for item in rq.json()['values']:
				rlist.append(item['slug'])
			return rlist
		except Exception as e:
			self.logger.error("An error occured: " + str(e))
			exit()

	# Get list of all available repos in a project
	def getBranches(self, project, repo):
		self.logger.info("Getting branches list from "+project+" project, "+repo+" repo")
		try:
			brlist = []
			url = self._api_ + 'projects/' + project + '/repos/' + repo + '/branches'
			rq = requests.get(url, auth=(self._user_, self._password_))
			x = 0
			for item in rq.json()['values']:
				brlist.append(item['displayId'])
			return brlist
		except Exception as e:
			self.logger.error("An error occured: " + str(e))
			exit()

	# Get list of all available PR notifications for a repo
	def getNotifications(self, project, repo):
		self.logger.info("Getting notifications list from "+project+" project, "+repo+" repo")
		try:
			notifications = []
			rq = requests.get(self._napi_, auth=(self._user_, self._password_))
			for item in rq.json():
				if item["repositorySlug"] == repo and item["projectKey"] == project:
					notifications.append(item)
			return notifications
		except Exception as e:
			self.logger.error("An error occured: " + str(e))
			exit()

	# Get list of all available PR notifications for a repo
	def getButtons(self, project, repo):
		self.logger.info("Getting buttons list from "+project+" project, "+repo+" repo")
		try:
			buttons = []
			rq = requests.get(self._bapi_, auth=(self._user_, self._password_))
			for item in rq.json():
				if item["repositorySlug"] == repo and item["projectKey"] == project:
					buttons.append(item)
			return buttons
		except Exception as e:
			self.logger.error("An error occured: " + str(e))
			exit()

	# Delete PR notifications by uuid
	def deleteNotification(self, uuid):
		self.logger.info("Deleting notification with uuid "+uuid)
		try:
			url = self._napi_ + "/" + uuid
			rq = requests.delete(url, auth=(self._user_, self._password_))
		except Exception as e:
			self.logger.error("An error occured: " + str(e))
			exit()

	# Update PR notifications by uuid
	def updateNotification(self, uuid, payload):
		self.logger.info("Updating notification with uuid "+uuid)
		try:
			url = self._napi_ + "/" + uuid
			rq = requests.post(url, auth=(self._user_, self._password_))
		except Exception as e:
			self.logger.error("An error occured: " + str(e))
			exit()

	# Function to select triggers from list
	def selectTriggers(self):
		os.system('clear')
		self.logger.info("Selecting triggers")
		try:
			ready = False
			tlist = []
			while not ready:
				cprint("Triggers: \n", "green")
				for x in range(len(triggers_list)):
					print('{:3}'.format(str(x)) + " -> " + triggers_list[x])
				order = input("Select a trigger from list to add: ")
				try:
					tlist.append(triggers_list[int(order)])
					confirm = input("Select another? (Y/N) ").upper()
					if confirm != 'Y':
						ready = True
				except Exception as e:
					self.logger.error("An error occured: " + str(e))
					exit()
			return tlist
		except Exception as e:
			self.logger.error("An error occured: " + str(e))
			exit()

	# Function to select filters from list
	def selectFilters(self, project, repo):
		self.logger.info("Selecting filters")
		try:
			ready = False
			while not ready:
				os.system('clear')
				cprint("Filters available: \n", "green")
				for x in range(len(filters_list)):
					print('{:3}'.format(str(x)) + " -> " + filters_list[x])
				forder = input("Select a trigger from list to add: ")
				try:
					# In case we want to filter by buttons
					if filters_list[int(forder)] == 'BUTTON_TRIGGER_TITLE':
						os.system('clear')
						buttons_list = self.getButtons(project, repo)
						cprint("\tButtons available: \n", "green")
						for b in range(len(buttons_list)):
							print('{:3}'.format(str(b)) + " -> " + buttons_list[b]['name'])
						order = input("Select a button from list to add: ")
						try:
							button = buttons_list[int(order)]['name']
							return filters_list[int(forder)], button
						except Exception as e:
							self.logger.error("An error occured: " + str(e))
							exit()

					# In case we want to filter by buttons
					if filters_list[int(forder)] == 'PULL_REQUEST_TO_BRANCH':
						branches_list = self.getBranches(project, repo)
						os.system('clear')
						cprint("\tBranches available: \n", "green")
						for br in range(len(branches_list)):
							print('{:3}'.format(str(br)) + " -> " + branches_list[br])
						order = input("Select a branch from list to add: ")
						try:
							branch = branches_list[int(order)]
							return filters_list[int(forder)], branch
						except Exception as e:
							self.logger.error("An error occured: " + str(e))
							exit()
					if filters_list[int(forder)] == 'NONE':
						return None, None
				except Exception as e:
					self.logger.error("An error occured: " + str(e))
					exit()
		except Exception as e:
			self.logger.error("An error occured: " + str(e))
			exit()
		
	# Function to select a project
	def selectProject(self):
		self.logger.info("Selecting project")
		try:
			os.system('clear')
			cprint("Projects list:\n", "green")
			projects = self.getProjects()
			for p in range(len(projects)):
				print('{:3}'.format(str(p)) + " -> " + projects[p])
			order = input("Select a Bitbucket project from list: ")
			try:
				return projects[int(order)]
			except Exception as e:
				self.logger.error("An error occured: " + str(e))
				exit()
		except Exception as e:
			self.logger.error("An error occured: " + str(e))
			exit()

	# Function to select a repo
	def selectRepo(self, project):
		self.logger.info("Selecting repo from project "+project)
		try:
			os.system('clear')
			cprint("Repositories list:\n", "green")
			repos = self.getRepos(project)
			for r in range(len(repos)):
				print('{:3}'.format(str(r)) + " -> " + repos[r])
			order = input("Select a Bitbucket repo from list: ")
			try:
				return repos[int(order)]
			except Exception as e:
				self.logger.error("An error occured: " + str(e))
				exit()
		except Exception as e:
			self.logger.error("An error occured: " + str(e))
			exit()

	# Function to select a notification
	def selectNotification(self, project, repo):
		self.logger.info("Selecting a notification from repo " + repo + ", project "+project)
		try:
			os.system('clear')
			cprint("Notifications list:\n", "green")
			notifications = self.getNotifications(project=project, repo=repo)
			for x in range(len(notifications)):
				print('{:3}'.format(str(x)) + '{:30}'.format(notifications[x]['name']) + notifications[x]['uuid'])
			order = input("Select a notification from list: ")
			try:
				return notifications[int(order)]
			except Exception as e:
				self.logger.error("An error occured: " + str(e))
				exit()
		except Exception as e:
			self.logger.error("An error occured: " + str(e))
			exit()

	# Function to add a notification
	def addNotification(self, url, user, password):
		self.logger.info("Creating notification")
		try:
			u = urlparse(url)
			jenkinsurl = u.scheme + '://' + u.netloc + '/view/crumbIssuer/api/xml?xpath=//crumb/text()'
			notification = {}
			os.system('clear')
			cprint("Enter the data for new PR notification:\n", "green")
			name = input("Name: ")
			if name != "":
				notification['name'] = name
			else:
				self.logger.error("Creating notification failed - name not specified")
				cprint("Notification name can not be empty.\n", "red")
				exit()

			# Creating notification
			notification['uuid'] = ""
			notification['url'] = url
			notification['method'] = 'GET'
			notification['triggerIfCanMerge'] = 'ALWAYS'
			notification['triggerIgnoreStateList'] = []
			notification['updatePullRequestRefs'] = False
			notification['postContentEncoding'] ='NONE'
			notification['httpVersion'] = 'HTTP_1_0'
			notification['headers'] = []
			notification['injectionUrl'] = jenkinsurl
			notification['injectionUrlRegexp'] = '<crumb>([^<]*)</crumb>'
			notification['user'] = user
			notification['password'] = password
			notification['triggers'] = self.selectTriggers()
			project = self.selectProject()
			repo = self.selectRepo(project)
			notification['projectKey'] = project
			notification['repositorySlug'] = repo
			fstring, fregexp = self.selectFilters(project, repo)
			if fstring == None:
				notification['filterString'] = ''
			else:
				notification['filterString'] = '${' + fstring + '}'
			if fregexp == None:
				notification['filterRegexp'] = ''
			else:
				notification['filterRegexp'] = fregexp
			
			try:
				headers = {'Content-Type': 'application/json; charset=UTF-8', 'Accept': 'application/json, text/javascript, */*; q=0.01'}
				data = json.dumps(notification, sort_keys=True)
				os.system('clear')
				cprint("Trying to create notification: ", "yellow")
				rq = requests.post(self._napi_, auth=(self._user_, self._password_), data=data, headers=headers)
				if rq.status_code == 200:
					cprint("OK.\n", "green")
					self.logger.info("Notification " + notification['name'] + " created for project " + project + ", repo " + repo)
				else:
					cprint("FAIL!\n", "red")
					cprint(str(rq.status_code) + "\n", "red")
					self.logger.error("Creating notification failed: HTTP response code" + str(rq.status_code))
					self.logger.error("HTTP response body" + str(rq.text))
				cprint("Press any key to continue", "yellow")
			except Exception as e:
				cprint("Notification could not be created.\n", "red")
				pp(notification)
				cprint("An error occured.\n", 'red')
				cprint(str(exc) + '\n', 'red')
				self.logger.error("Creating notification failed: " + str(e))
				exit()
		except Exception as e:
			self.logger.error("An error occured: " + str(e))
			exit()
