import os
import requests
import logging
import xmltodict
from termcolor import colored
from .utils import *


class JenkinsInstance:
	EMPTY_CONFIG = '''<?xml version='1.0' encoding='UTF-8'?>
						<project>
							<actions/>
							<description/>
							<keepDependencies>false</keepDependencies>
							<properties/>
							<scm class="hudson.scm.NullSCM"/>
							<canRoam>true</canRoam>
							<disabled>false</disabled>
							<blockBuildWhenDownstreamBuilding>false</blockBuildWhenDownstreamBuilding>
							<blockBuildWhenUpstreamBuilding>false</blockBuildWhenUpstreamBuilding>
							<authToken></authToken>
							<triggers/>
							<concurrentBuild>false</concurrentBuild>
							<builders/>
							<publishers/>
							<buildWrappers/>
						</project>'''

	# Initialize connection
	def __init__(self, url='http://localhost:8080', user = 'admin', password = 'admin'):
		self.logger = logging.getLogger("M::Jenkins")
		self.url = url
		self.user = user
		self.password = password
		self.logger.info("Module initialized")

	def _crumb_(self):
		url = self.url + "/crumbIssuer/api/xml?xpath=//crumb"
		rq = requests.get(url, auth=(self.user, self.password))
		crumb = xmltodict.parse(rq.text)
		return crumb['crumb']

	# Returns a Jenkins views list
	def getViews(self):
		self.logger.info("Getting views list")
		try:
			url = self.url + '/api/json'
			rq = requests.get(url, auth=(self.user, self.password))
			return rq.json()['views']
		except Exception as e:
			self.logger.error("An error occured: " + str(e))
			exit()

	def getJobs(self):
		self.logger.info("Getting jobs list")
		try:
			jobs = []
			url = self.url + '/api/json'
			rq = requests.get(url, auth=(self.user, self.password))
			for job in rq.json()['jobs']:
				if job['_class'] != 'com.cloudbees.hudson.plugins.folder.Folder':
					jobs.append(job)
			return jobs
		except Exception as e:
			self.logger.error("An error occured: " + str(e))
			exit()

	def getFolders(self):
		self.logger.info("Getting folders list")
		try:
			folders = []
			url = self.url + '/api/json'
			rq = requests.get(url, auth=(self.user, self.password))
			for job in rq.json()['jobs']:
				if job['_class'] == 'com.cloudbees.hudson.plugins.folder.Folder':
					folders.append(job)
			return folders
		except Exception as e:
			self.logger.error("An error occured: " + str(e))
			exit()

	# Returns a list of Jenkins jobs from Jenkins view config (XML)
	def getJobsFromView(self, view):
		self.logger.info("Getting jobs list from view "+view)
		try:
			jobList = []
			url = self.url + '/view/' + view + '/api/json'
			rq = requests.get(url, auth=(self.user, self.password))
			for job in rq.json()['jobs']:
				jobList.append(job)
			self.logger.info("Done getting job list")
			return jobList
		except Exception as e:
			self.logger.error("An error occured: " + str(e))
			exit()

	# Select Jenkins view dialog
	def selectView(self):
		self.logger.info("Select view ")
		try:
			os.system('clear')
			cprint("Jenkins views list:\n", "green")
			views = self.getViews()
			for x in range(len(views)):
				print('{:3}'.format(str(x)) + " -> " + views[x]['name'])
			order = input("Select a view where your Jenkins job is located: ")
			try:
				view = views[int(order)]
				return view
			except Exception as exc:
				self.logger.error("An error occured: " + str(e))
				cprint("An error occured.\n", 'red')
				cprint(exc + '\n', 'red')
				exit()
		except Exception as e:
			self.logger.error("An error occured: " + str(e))
			exit()

	# Select Jenkins job dialog
	def selectJob(self, view):
		self.logger.info("Select job from view "+view)
		try:
			found = False
			os.system('clear')
			cprint("Jenkins jobs selection:\n","green")
			jobs = self.getJobsFromView(view)
			while not found:
				for x in range(len(jobs)):
					print('{:3}'.format(str(x)) + " -> " + jobs[x]['name'], end='')
					if jobs[x]['_class'] == 'com.cloudbees.hudson.plugins.folder.Folder':
						cprint(" (F)\n", "orange")
					else:
						print()
				order = input("Select a Jenkins job: ")
				try:
					job = jobs[int(order)]
					if job['_class'] != 'com.cloudbees.hudson.plugins.folder.Folder':
						self.logger.info("Got job " + job['name'])
						found = True
						return job
					else:
						url = self.url + '/view/' + view + '/job/' + job['name'] + '/api/json'
						rq = requests.get(url, auth=(self.user, self.password))
						jobs = rq.json()['jobs']
				except Exception as e:
					self.logger.error("An error occured: " + str(e))
					exit()
		except Exception as e:
			self.logger.error("An error occured: " + str(e))
			exit()

	def getJobDetails(self, job):
		self.logger.info("Get details for job " + job['name'])
		try:
			url = job['url'] + '/config.xml'
			rq = requests.get(url, auth=(self.user, self.password))
			data = xmltodict.parse(rq.text)
			return data
		except Exception as e:
			self.logger.error("An error occured: " + str(e))
			exit()

	def createJob(self, name):
		self.logger.info("Create job with name " + name)
		try:
			crumb = self._crumb_()
			headers = {'Jenkins-Crumb': crumb, 'Content-Type': 'application/xml'}
			data = self.EMPTY_CONFIG
			url = self.url + "/createItem?name=" + name
			rq = requests.post(url, auth=(self.user, self.password), data=data, headers=headers)
			response = rq.status_code
			if response == 200:
				return True
			else:
				return False
		except Exception as e:
			self.logger.error("An error occured: " + str(e))
			exit()

	def deleteJob(self, job):
		self.logger.info("Delete job with name " + job['name'])
		try:
			crumb = self._crumb_()
			headers = {'Jenkins-Crumb': crumb, 'Content-Type': 'application/xml'}
			url = job['url'] + "/doDelete"
			rq = requests.post(url, auth=(self.user, self.password), headers=headers)
			response = rq.status_code
			if response == 200:
				return True
			else:
				return False
		except Exception as e:
			self.logger.error("An error occured: " + str(e))
			exit()

	def deleteView(self, view):
		self.logger.info("Delete view with name " + view['name'])
		try:
			crumb = self._crumb_()
			headers = {'Jenkins-Crumb': crumb, 'Content-Type': 'application/xml'}
			url = view['url'] + "/doDelete"
			rq = requests.post(url, auth=(self.user, self.password), headers=headers)
			response = rq.status_code
			if response == 200:
				return True
			else:
				return False
		except Exception as e:
			self.logger.error("An error occured: " + str(e))
			exit()
