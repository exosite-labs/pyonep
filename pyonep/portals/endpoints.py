"""
    A python abstraction of the Exosite Portals API endpoints.
"""
# pylint: disable=W0312
import requests, json
from pyonep.portals.constants import HTTP_STATUS
from pyonep.portals.utils import dictify_device_meta
from pyonep.portals.__version__ import __version__ as VERSION
from requests.auth import HTTPBasicAuth

try:
    # python3
    import http.client as http_client
except ImportError:
    # Python 2
    import httplib as http_client


class Domain(object):
    """
        This module contains the Domain() class from which
        the Portals() class is meant to be based on.
    """
    def __init__(   self,
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

class Endpoints(Domain):
    """
        The Endpoints() class should be as stateless as possible.

    """
    def __init__(   self,
                    domain,
                    portal_name,
                    user,
                    auth,
                    portal_id=None,
                    # portal_rid=None,
                    use_token=False,
                    debug=False
                    ):
        Domain.__init__(self, domain=domain, user=user, auth=auth, use_token=use_token)
        self.__purl = self.domain_url()+'/api/portals/v1'
        self.__vendor = self.domain().split('.')[0]
        self.__portal_name = portal_name
        self.__portal_id = portal_id
        # self.__portal_rid = portal_rid
        self.__portal_cik = None
        http_client.HTTPConnection.debuglevel = int(debug)


    # #####################################################
    #   Endpoints class member setters and getters.
    # #####################################################
    def set_portals_url(self, url):
        """ Member variable setter for  Portals API Base url. """
        self.__purl = url
    def set_vendor(self, vendor):
        """ Member variable setter for Exosite Vendor. """
        self.__vendor = vendor
    def set_portal_id(self, _id):
        """ Member variable setter for numerical Portal ID. """
        self.__portal_id = _id
    # def set_portal_rid(self, rid):
    #   self.__portal_rid = rid
    def set_portal_cik(self, cik):
        """ Member variable setter for Portal CIK. """
        self.__portal_cik = cik
    def set_portal_name(self, name):
        """ Member variable setter for Portal name. """
        self.__portal_name = name
    def portals_url(self):
        """ Returns Portals API Base url. """
        return self.__purl
    def vendor(self):
        """ Returns Exosite Vendor. """
        return self.__vendor
    def portal_id(self):
        """ Returns numerical Portal ID. """
        return self.__portal_id
    # def portal_rid(self):
    #   return self.__portal_rid
    def portal_cik(self):
        """ Returns numerical Portal CIK. """
        return self.__portal_cik
    def portal_name(self):
        """ Returns numerical Portal name. """
        return self.__portal_name

    # #####################################################
    #   Portals API method abstractions.
    # #####################################################
    def get_user_token(self):
        """
            Gets a authorization token for session reuse.

            http://docs.exosite.com/portals/#get-user-token-for-openid-user
        """
        headers = { 'User-Agent': self.user_agent(),
                'Host': self.domain(),
                'Accept': '*/*',
        }
        headers.update(self.headers())
        r = requests.get(   self.portals_url()+'/users/_this/token',
                            headers=headers,
                            auth=self.auth())
        if HTTP_STATUS.OK == r.status_code:
            return r.text
        else:
            print("get_user_token: Something went wrong: <{0}>: {1}".format(
                        r.status_code, r.reason))
            r.raise_for_status()

    def get_domain_portal_ids(self):
        """
            Gets the list of Portal ids.

            http://docs.exosite.com/portals/#list-portal-by-domain
        """
        headers = { 'User-Agent': self.user_agent(),
                'Host': self.domain(),
                'Accept': '*/*'
        }
        headers.update(self.headers())

        r = requests.get(   self.portals_url()+'/portals',
                            headers=headers,
                            auth=self.auth())
        if HTTP_STATUS.OK == r.status_code:
            return [ _id['id'] for _id in r.json() ]
        else:
            print("get_user_portals: Something went wrong: <{0}>: {1}".format(
                        r.status_code, r.reason))
            r.raise_for_status()

    def get_user_portals(self):
        """
            Gets the list of Portals authorized for this user.

            http://docs.exosite.com/portals/#list-portals-of-authenticated-user
        """
        headers = { 'User-Agent': self.user_agent(),
                'Host': self.domain(),
                'Accept': '*/*'
        }
        headers.update(self.headers())

        r = requests.get(   self.portals_url()+'/portal',
                            headers=headers,
                            auth=self.auth())
        if HTTP_STATUS.OK == r.status_code:
            return r.json()
        else:
            print("get_user_portals: Something went wrong: <{0}>: {1}".format(
                        r.status_code, r.reason))
            r.raise_for_status()

    def get_portal_by_id(self, ID):
        """     Returns a portal object by ID input. 
        
            http://docs.exosite.com/portals/#get-portal
        """
        headers = { 'User-Agent': self.user_agent(),
                'Host': self.domain(),
                'Accept': '*/*'
        }
        headers.update(self.headers())

        r = requests.get(   self.portals_url()+'/portals/'+str(ID),
                            headers=headers,
                            auth=self.auth())
        if HTTP_STATUS.OK == r.status_code:
            return r.json()
        else:
            print("get_portal_by_id: Something went wrong: <{0}>: {1}".format(
                        r.status_code, r.reason))
            r.raise_for_status()


    def add_device(self, model, serial):
        """
            Returns 'device object' of newly created device.

            http://docs.exosite.com/portals/#create-device
            http://docs.exosite.com/portals/#device-object
        """
        device = {
                'model': model,
                'vendor': self.vendor(),
                'sn': serial,
                'type': 'vendor'
        }
        headers = {
                'User-Agent': self.user_agent(),
        }
        headers.update(self.headers())

        r = requests.post(  self.portals_url()+'/portals/'+self.portal_id()+'/devices', 
                                data=json.dumps(device),
                                headers=headers,
                                auth=self.auth())

        if HTTP_STATUS.ADDED == r.status_code:
            # fix the 'meta' to be dictionary instead of string
            device_obj = r.json()
            return dictify_device_meta(device_obj)
        else:
            print("add_device: Something went wrong: <{0}>: {1}".format(
                        r.status_code, r.reason))
            r.raise_for_status()

    def update_device(self, device_obj):
        """ Implements the Update device Portals API.
            
            http://docs.exosite.com/portals/#update-device
        """
        rid = device_obj['rid']
        device_obj['info']['description']['meta'] = \
                json.dumps(device_obj['info']['description']['meta'])
        headers = {
                'User-Agent': self.user_agent(),
        }
        headers.update(self.headers())

        r = requests.put(   self.portals_url()+'/devices/'+rid, 
                            data=json.dumps(device_obj),
                            headers=headers,
                            auth=self.auth())
        if HTTP_STATUS.OK == r.status_code:
            # fix the 'meta' to be dictionary instead of string
            updated_dev_obj = r.json()
            updated_dev_obj['info']['description']['meta'] =\
                            json.loads(device_obj['info']['description']['meta'])
            return updated_dev_obj
        else:
            print("update_device: Something went wrong: <{0}>: {1}".format(
                        r.status_code, r.reason))
            r.raise_for_status()

    def update_portal(self, portal_obj):
        """ Implements the Update device Portals API.

            This function is extremely dangerous. The portal object
            you pass in will completely overwrite the portal.
            
            http://docs.exosite.com/portals/#update-portal
        """
        headers = {
                'User-Agent': self.user_agent(),
        }
        headers.update(self.headers())

        r = requests.put(   self.portals_url()+'/portals/'+self.portal_id(), 
                            data=json.dumps(portal_obj),
                            headers=headers,
                            auth=self.auth())
        if HTTP_STATUS.OK == r.status_code:
            return r.json()
        else:
            print("update_portal: Something went wrong: <{0}>: {1}".format(
                        r.status_code, r.reason))
            r.raise_for_status()

    def get_device(self, rid):
        """
            Retrieve the device object for a given RID.

            http://docs.exosite.com/portals/#get-device
        """
        headers = {
                'User-Agent': self.user_agent(),
                'Content-Type': self.content_type()
        }
        headers.update(self.headers())

        url = self.portals_url()+'/devices/'+rid
        # print("URL: {0}".format(url))

        r = requests.get(   url,
                            headers=headers,
                            auth=self.auth())
    
        if HTTP_STATUS.OK == r.status_code:
            # fix the 'meta' to be dictionary instead of string
            device_obj = r.json()
            # device_obj['info']['description']['meta'] = \
                    # json.loads(device_obj['info']['description']['meta'])
            return device_obj
        else:
            print("get_device: Something went wrong: <{0}>: {1}".format(
                        r.status_code, r.reason))
            r.raise_for_status()

    def get_multiple_devices(self, rids):
        """
            Implements the 'Get Multiple Devices' API.

            Param rids: a python list object of device rids.

            http://docs.exosite.com/portals/#get-multiple-devices
        """
        headers = {
                'User-Agent': self.user_agent(),
                'Content-Type': self.content_type()
        }
        headers.update(self.headers())

        url = self.portals_url()+'/users/_this/devices/' + str(rids).replace("'", "").replace(' ','')
        # print("URL: {0}".format(url))
        r = requests.get(   url,
                            headers=headers,
                            auth=self.auth())
    
        if HTTP_STATUS.OK == r.status_code:
            # TODO: loop through all rids and fix 'meta' to be dict like add_device and get_device do
            return r.json()
        else:
            print("get_multiple_devices: Something went wrong: <{0}>: {1}".format(
                        r.status_code, r.reason))
            r.raise_for_status()

    def get_all_user_accounts(self):
        """Get all user accounts

            Returns the user accounts if successful, otherwise returns None.

            http://docs.exosite.com/portals/#get-all-user-accounts
        """

        headers = {
                'User-Agent': self.user_agent(),
                'Content-Type': self.content_type()
        }
        headers.update(self.headers())

        url = self.portals_url()+'/accounts'
        # print("URL: {0}".format(url))
        r = requests.get(   url,
                            headers=headers,
                            auth=self.auth())
    
        if HTTP_STATUS.OK == r.status_code:
            return r.json()
        else:
            print("get_all_user_accounts: Something went wrong: <{0}>: {1}".format(
                        r.status_code, r.reason))
            r.raise_for_status()

    def get_user_permission(self, user_id):
        """ http://docs.exosite.com/portals/#get-user-permission """

        headers = {
                'User-Agent': self.user_agent(),
                'Content-Type': self.content_type()
        }
        headers.update(self.headers())

        url = self.portals_url()+'/users/{0}/permissions'.format(user_id)
        # print("URL: {0}".format(url))
        r = requests.get(   url,
                            headers=headers,
                            auth=self.auth())
    
        if HTTP_STATUS.OK == r.status_code:
            return r.json()
        else:
            print("get_user_permission: Something went wrong: <{0}>: {1}".format(
                        r.status_code, r.reason))
            r.raise_for_status()

    def add_user_permission(self, user_id, permission_obj):
        """ 'permission' param should be a string. 
                e.g. '[{"access":"d_u_list","oid":{"id":"1576946496","type":"Domain"}}]'

        http://docs.exosite.com/portals/#add-user-permission
        """

        headers = {
                'User-Agent': self.user_agent(),
                'Content-Type': self.content_type()
        }
        headers.update(self.headers())

        url = self.portals_url()+'/users/{0}/permissions'.format(user_id)
        # print("URL: {0}".format(url))
        r = requests.post(  url,
                            data=permission_obj,
                            headers=headers,
                            auth=self.auth())
    
        if HTTP_STATUS.OK == r.status_code:
            return r.json()
        else:
            print("add_user_permission: Something went wrong: <{0}>: {1}".format(
                        r.status_code, r.reason))
            r.raise_for_status()

    def create_token(self, user_id, permission_obj):
        """ 'permission_obj' param should be a string. 
                e.g. '[{"access":"d_u_list","oid":{"id":"1576946496","type":"Domain"}}]'

        http://docs.exosite.com/portals/#add-user-permission
        """

        headers = {
                'User-Agent': self.user_agent(),
                'Content-Type': self.content_type()
        }
        headers.update(self.headers())

        url = self.portals_url()+'/users/{0}/permissions'.format(user_id)
        # print("URL: {0}".format(url))
        r = requests.post(  url,
                            data=permission_obj,
                            headers=headers,
                            auth=self.auth())
    
        if HTTP_STATUS.OK == r.status_code:
            return r.json()
        else:
            print("create_token: Something went wrong: <{0}>: {1}".format(
                        r.status_code, r.reason))
            r.raise_for_status()







