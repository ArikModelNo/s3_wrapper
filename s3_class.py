import datetime
import operator
import requests
import base64
import boto3
import re
import os
import sys
PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
from s3_wrapper.s3_config import config


class S3():
	"""
	Class for interacting with an AWS S3 Bucket.

	Make sure to create s3_config.py and populate it.
	"""

	def __init__(self, cwd = ''):
		self.cwd = cwd
		self._session = boto3.Session(
			aws_access_key_id=config['AWS_ACCESS_KEY_ID'],
			aws_secret_access_key=config['AWS_SECRET_ACCESS_KEY'])
		self._bucket = self._session.resource('s3').Bucket(config['BUCKET'])

	cwd = property(operator.attrgetter('_cwd'))

	@cwd.setter
	def cwd(self, c):
		if c.endswith('/'):
			c = c[:-1]
		self._cwd = c

	def printCWD(self):
		"""
		Prints the current working directory.
		
		Returns nothing.
		"""
		print(self.cwd)

	def _assemblePath(self, path, filename):
		"""
		Assembles a full path from given parameters.

		Returns str of full path.
		"""
		if self.cwd == '':
			if path == '':
				return f'{filename}'
			return f'{path}/{filename}'
		else:
			return f'{self.cwd}/{path}/{filename}'

	def accessibleFiles(self, **kwargs):
		"""
		Determines which files are accessible from CWD.
		Optionally prints list when called as accessibleFiles(print=True)

		Returns list of accessible files.
		"""
		accessible_files = []
		if kwargs.get('print') is True:
			print('** Accessible Files **')
		for path in self._bucket.objects.all():
			if path.key.startswith(self.cwd):
				if not path.key.endswith('/'):
					accessible_files.append(path.key)
					if kwargs.get('print') is True:
						print('\t' + path.key)
		return accessible_files

	def accessibleDirectories(self):
		"""
		Determines which directories are accessible from CWD
		and prints the hierarchy.

		Returns nothing.
		"""
		print('** Accessible Directories **')
		for path in self._bucket.objects.all():
			if path.key.startswith(self.cwd):
				if path.key.endswith('/'):
					list_of_path = path.key.split('/')
					print('\t' * (len(list_of_path) - 1), end='')
					print(list_of_path[-2])

	def checkIfFileExists(self, path, filename):
		"""
		Checks if a file at a given path exists.
		Prints full path to file if found.

		Returns True if it does, False if it doesn't.
		"""
		if not filename:
			print('Why you no give filename?')
			return False
		full_path = self._assemblePath(path, filename)
		for obj_path in self._bucket.objects.all():
			if full_path == obj_path.key:
				print(f'Found file [{full_path}]!')
				return True
		return False

	def uploadWithBase64(self, path, filename, data_base64, **kwargs):
		"""
		Uploads file of given base64 data.

		Returns nothing.
		"""
		if not filename:
			print('Why you no give filename?')
			return False
		public = kwargs.get('public')
		if public is None:
			print('Is this file public or not?')
			return False
		permissions = 'bucket-owner-full-control'
		if public is True:
			permissions = 'public-read'
		data_base64 = data_base64[data_base64.find(',') + 1:]
		data_base64 = base64.b64decode(data_base64)
		full_path = self._assemblePath(path, filename)
		self._bucket.put_object(Key=full_path, Body=data_base64, ACL=permissions)

	def uploadWithBinary(self, path, filename, data_binary, **kwargs):
		"""
		Uploads file of given binary.

		Returns nothing.
		"""
		if not filename:
			print('Why you no give filename?')
			return False
		public = kwargs.get('public')
		if public is None:
			print('Is this file public or not?')
			return False
		permissions = 'bucket-owner-full-control'
		if public is True:
			permissions = 'public-read'
		full_path = self._assemblePath(path, filename)
		self._bucket.put_object(Key=full_path, Body=data_binary, ACL=permissions)

	def uploadWithURL(self, path, data_url):
		"""
		Uploads file of given url.

		Returns False upon failure to download or interprate file.
		"""
		permissions = 'bucket-owner-full-control'
		try:
			response = requests.get(data_url)
		except:
			print('Failed to retrieve file')
			return False
		data_binary = response.content
		content_disposition = response.headers.get('Content-Disposition')
		if content_disposition is None:
			print('Failed to retrieve content disposition')
			return False
		else:
			regex_result = re.findall('filename="(.*?)"', content_disposition)[0]
			if regex_result != '':
				filename = regex_result
			else:
				print('Failed to retrieve file name')
				filename = 'untitled_' + datetime.datetime.now().isoformat()
		full_path = self._assemblePath(path, filename)
		self._bucket.put_object(Key=full_path, Body=data_binary, ACL=permissions)
