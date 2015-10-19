"""
	This module contains the Domain() class from which
	the Portals() class is meant to be based on.
"""
from __init__ import __version__ as VERSION
from requests.auth import HTTPBasicAuth
class Domain(object):
	def __init__(	self,
					domain,
					user,
					auth,
					use_token=False):
		"""
			Abstract the whitelabel/domain
		"""
		self.__domain = domain
		self.__user = user
		if use_token:
			self.__headers = {'Authorization': 'Token '+ auth}
			self.__auth = None
		else:
			self.__headers = {}
			self.__auth = HTTPBasicAuth(user, auth)
		self.__durl = 'https://'+self.__domain
		self.__user_agent = 'Portals-Bindings-v{0}'.format(VERSION)
		self.__content_type = 'application/json; charset=utf-8'

	def domain(self):
		return self.__domain
	def user(self):
		return self.__user
	def auth(self):
		return self.__auth
	def domain_url(self):
		return self.__durl
	def user_agent(self):
		return self.__user_agent
	def content_type(self):
		return self.__content_type
	def headers(self):
		return self.__headers
