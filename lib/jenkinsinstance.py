import os
import random
import string
import hashlib
import requests
import logging
import xmltodict
from xml.etree import ElementTree as et
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
	JOB_TYPES = ['NONE', 'PR', 'CI-DEV', 'CI-QA']

	# Initialize connection
	def __init__(self, url='http://localhost:8080', user = 'admin', password = 'admin'):
		self.logger = logging.getLogger("M::Jenkins")
		self.url = url
		self.user = user
		self.password = password
		self.logger.info("Module initialized")

	def _crumb_(self):
		self.logger = logging.getLogger("M::Jenkins::_CRUMB_")
		self.logger.info("Starting")
		url = self.url + "/crumbIssuer/api/xml?xpath=//crumb"
		rq = requests.get(url, auth=(self.user, self.password))
		crumb = xmltodict.parse(rq.text)
		self.logger.info(crumb['crumb'])
		return crumb['crumb']

	# Returns a Jenkins views list
	def getViews(self):
		self.logger = logging.getLogger("M::Jenkins::GetViews")
		self.logger.info("Starting")
		try:
			url = self.url + '/api/json'
			rq = requests.get(url, auth=(self.user, self.password))
			return rq.json()['views']
		except Exception as e:
			self.logger.error("An error occured: " + str(e))
			exit()

	def getJobs(self):
		self.logger = logging.getLogger("M::Jenkins::GetJobs")
		self.logger.info("Starting")
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
		self.logger = logging.getLogger("M::Jenkins::GetFolders")
		self.logger.info("Starting")
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
		self.logger = logging.getLogger("M::Jenkins::GetJobsFromView")
		self.logger.info("Starting")
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

	# Returns a list of Jenkins jobs from Jenkins view config (XML)
	def getJobsFromPath(self, path):
		self.logger = logging.getLogger("M::Jenkins::GetJobsFromPath")
		self.logger.info("Starting")
		try:
			jobList = []
			url = self.url + path + '/api/json'
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
		self.logger = logging.getLogger("M::Jenkins::SelectView")
		self.logger.info("Starting")
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
		self.logger = logging.getLogger("M::Jenkins::SelectJob")
		self.logger.info("Starting")
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



	# Select path in Jenkins
	def selectPath(self):
		self.logger = logging.getLogger("M::Jenkins::SelectPath")
		self.logger.info("Starting")
		path = ''
		found = False
		self.logger.info("Select view ")
		try:
			os.system('clear')
			cprint("Jenkins views list:\n", "green")
			views = self.getViews()
			self.logger.info("Got views list")
			for x in range(len(views)):
				print('{:3}'.format(str(x)) + " -> " + views[x]['name'])
			order = input("Select a view where your Jenkins job is located: ")
			view = views[int(order)]
			self.logger.info("Selected view")
			if view['name'] != 'all':
				path = path + '/views/' + view['name']
			jobs = self.getJobsFromView(view['name'])

			while not found:
				folders = []
				for x in range(len(jobs)):
					if jobs[x]['_class'] == 'com.cloudbees.hudson.plugins.folder.Folder':
						folders.append(jobs[x])
						print('{:3}'.format(str(x)) + " -> (Folder) -> " + jobs[x]['name'])
				if len(folders) > 0:
					order = input("Select a folder or press H to create a job here ")
					key = order.upper()
					if key != 'H':
						try:
							folder = jobs[int(order)]
							path = '/job/' + folder['name']
							jobs = self.getJobsFromPath(path)
							self.logger = logging.getLogger("M::Jenkins::SelectPath")
						except:
							pass
					else:
						found = True
						return path
				else:
					cprint("Create a job here? (Y/N) ", "green")
					order = input()
					if order.upper() == 'Y':
						found = True
						return path
					else:
						cprint("WHOA! I don't get the idea... Bye.\n", "red")
						exit()
		except Exception as e:
			self.logger.error("An error occured in creation job: " + str(e))
			exit()




	def getJobDetails(self, job):
		self.logger = logging.getLogger("M::Jenkins::GetJobDetails")
		self.logger.info("Starting")
		try:
			url = job['url'] + '/config.xml'
			rq = requests.get(url, auth=(self.user, self.password))
			data = xmltodict.parse(rq.text)
			return data
		except Exception as e:
			self.logger.error("An error occured: " + str(e))
			exit()

	def createJob(self):
		self.logger = logging.getLogger("M::Jenkins::CreateJob")
		self.logger.info("Starting")
		try:
			os.system('clear')
			cprint('Enter new job name: ', 'green')
			jname = input()
			os.system('clear')
			cprint('Jenkins job types: \n', 'green')
			for x in range(len(self.JOB_TYPES)):
				print('{:3}'.format(str(x)) + " -> " + self.JOB_TYPES[x])
			order = input("Select a Jenkins job type: ")
			try:
				jtype = self.JOB_TYPES[int(order)]
			except Exception as e:
				self.logger.error(e)
			xml = self.parseJobXML(jtype)
			jdata = et.tostring(xml, encoding='utf8', method='xml')
			self.logger = logging.getLogger("M::Jenkins::CreateJob")
			jpath = self.selectPath()
			self.logger = logging.getLogger("M::Jenkins::CreateJob")
			crumb = self._crumb_()
			headers = {'Jenkins-Crumb': crumb, 'Content-Type': 'application/xml'}
			url = self.url + jpath + "/createItem?name=" + jname
			self.logger.info(url)
			self.logger.info(headers)
			self.logger.info(xmltodict.parse(jdata))
			rq = requests.post(url, auth=(self.user, self.password), data=jdata, headers=headers)
			
			response = rq.status_code
			if response == 200:
				return True
			else:
				return False
		except Exception as e:
			self.logger.error("An error occured: " + str(e))
			exit()

	def deleteJob(self, job):
		self.logger = logging.getLogger("M::Jenkins::DeleteJob")
		self.logger.info("Starting")
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
		self.logger = logging.getLogger("M::Jenkins::DeleteView")
		self.logger.info("Starting")
		try:
			crumb = self._crumb_()
			headers = {'Jenkins-Crumb': crumb, 'Content-Type': 'application/xml; charset=utf-8', 'Content-Type': 'text/xml; charset=utf-8'}
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

	def parseJobXML(self, type):
		self.logger = logging.getLogger("M::Jenkins::ParseJobXML")
		self.logger.info("Starting")
		try:
			if type == 'PR':
				tree = et.parse('templates/PR.xml')
				tree = tree.getroot()
				m = hashlib.md5()
				letters = string.ascii_lowercase
				rdata = ''.join(random.choice(letters) for i in range(12)).encode('utf-8')
				m.update(rdata)
				token = m.hexdigest()
				tree.find('authToken').text = token
				self.logger.info('XML Parsed')
				return tree
		except Exception as e:
			self.logger.error("An error occured: " + str(e))
			exit()

		