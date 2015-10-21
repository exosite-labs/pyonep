# pylint: disable=W0312,R0913
import requests, json
from pyonep.portals.constants import HTTP_STATUS
from pyonep.portals.endpoints import Endpoints
from pyonep.portals.utils import dictify_device_meta,\
                                 stringify_device_meta
from getpass import getpass
import sys

if sys.version_info[0] < 3:
    _input = raw_input
else:
    _input = input

class Portals(Endpoints):
    def __init__(   self,
                    domain,
                    portal_name,
                    user,
                    auth='__prompt__',
                    use_token=False,
                    debug=False):
        """
            Params:
                domain:         the domain of the Exosite domain your Portal is on. 
                                i.e. mydomain.exosite.com
                portal_name:    the name of the Exosite Portal. i.e. 'My Device Portal'
                user:           typically, the email address you use to logon to Portals 
                                or your Portals user name
                auth:           if left blank, the creator of the Portals object will 
                                be prompted for their Portals password if specifying the 
                                auth parameter, it should be either the user password or a 
                                Portals token
                use_token:      if using a token in the auth parameter, set this to True. 
                                Otherwise, leave blank
        """
        if auth == '__prompt__':
            print('') # some interpreters don't put a newline before the getpass prompt
            auth = getpass('Enter User Password: ')
        else:
            auth = auth
        Endpoints.__init__(   self, 
                            domain,
                            portal_name,
                            user,
                            auth,
                            use_token=use_token
        )

    def get_portals_list(self):
        """     Method to return a list of Portal names with their id's. 
        
            Returns list of tuples as [(id_1, portal_name1), (id_2, portal_name2)]
        """
        portal_ids = self.get_domain_portal_ids()
        portals = [ (p, self.get_portal_by_id(p)) for p in portal_ids ]
        return [ (p[0], p[1]['info']['description']['name'], p) for p in portals ]

    def user_portals_picker(self):
        """
            This function is broken and needs to either be fixed or discarded.

            User-Interaction function. Allows user to choose which Portal
            to make the active one.
        """
        # print("Getting Portals list. This could take a few seconds...")
        portals = self.get_portals_list()
        done = False
        while not done:
            opts = [ (i, p) for i, p in enumerate(portals) ]
            # print('')
            for opt, portal in opts:
                print("\t{0} - {1}".format(opt, portal[1]))
            # print('')
            valid_choices = [o[0] for o in opts]
            choice = _input("Enter choice ({0}): ".format(valid_choices) )
            if int(choice) in valid_choices:
                done = True

                # loop through all portals until we find an 'id':'rid' match
                self.set_portal_name( opts[int(choice)][1][1] )
                self.set_portal_id( opts[int(choice)][1][0] )
                # self.set_portal_rid( opts[int(choice)][1][2][1]['info']['key'] )
                # self.__portal_sn_rid_dict = opts[int(choice)][1][2][1]['info']['aliases']

            else:
                print("'{0}' is not a valid choice. Please choose from {1}".format(
                    choice, valid_choices))


    def get_portal_by_name(self, portal_name):
        """
            Set active portal according to the name passed in 'portal_name'.

            Returns dictionary of device 'serial_number: rid'
        """
        portals = self.get_portals_list()

        for p in portals:
            # print("Checking {!r}".format(p))
            if portal_name == p[1]:
                # print("Found Portal!")
                self.set_portal_name( p[1] )
                self.set_portal_id( p[0] )
                self.set_portal_cik( p[2][1]['info']['key'] )
                # print("Active Portal Details:\nName: {0}\nId: {1}\nCIK: {2}".format(
                #                               self.portal_name(),
                #                               self.portal_id(),
                #                               self.portal_cik()))
                return p
        return None

    @classmethod
    def login_to_portal(cls,
                        domain=None,
                        portal_name=None,
                        user=None,
                        credential=None,
                        use_token=False,
                        portal_id=None,
                        # portal_rid=None,
                        get_devices=False,
                        debug=False):
        """
            A classmethod that returns a (token, Portals object) tuple.

            This method can be interactive based on the input arguments.

            Sets up the Portals object with all the member variables
            it needs to make future api calls. It basically just calls 
            Portals.get_portal_by_name(), but instead of returning a 
            Portals object, it returns a Portals() object.

            This is a convenience function that can be called at the 
            time of instantiation.

            Instantiate the Portals object with user/password authentication
            then call this function. The resultant object will be a Portals
            object that uses token authentication for all future calls 
            instead of using user/password credentials.

            Examples:
                # for interactive mode, get a password prompt, a token 
                # and a logged-in Portals object
                token, B = Portals.login_to_portal( domain=<domain>,
                                                     portal_name=<portal>,
                                                     user=<user/email>
                )

                # for non-interactive mode, passing in user password to 
                # get a token and a logged-in Portals object
                token, B = Portals.login_to_portal( domain=<domain>,
                                                     portal_name=<portal>,
                                                     user=<user/email>,
                                                     credential=<password>
                )

                # for non-interactive mode, passing in token to get a 
                # logged-in Portals object
                token, B = Portals.login_to_portal( domain=<domain>,
                                                     portal_name=<portal>,
                                                     user=<user/email>,
                                                     credential=<token>,
                                                     use_token=True
                )

                # for non-interactive mode, passing in token and id 
                # to get a Portals object that doesn't need to make any 
                # Portals API calls. 
                token, B = Portals.login_to_portal( domain=<domain>,
                                                     portal_name=<portal>,
                                                     user=<user/email>,
                                                     credential=<token>,
                                                     use_token=True,
                                                     portal_id=<portal_id>,
                                                     portal_rid=<portal_rid>
                )
        """
        if domain is None:
            domain = _input("Enter domain: ")
        if portal_name is None:
            portal_name = _input("Enter name of Portal: ")
        if user is None:
            user = _input("Enter username: ")
        if None is credential:
            # interactive mode
            B = Portals(   domain=domain,
                            portal_name=portal_name,
                            user=user,
                            debug=debug
            )
            token = B.get_user_token()
            # print("Got token {0}".format(token))
        elif not None is credential and not use_token:
            # non-interactive, using a user-password to retrieve token
            B = Portals(   domain=domain,
                            portal_name=portal_name,
                            user=user,
                            auth=credential,
                            debug=debug
            )
            token = B.get_user_token()
        elif not None is credential and use_token:
            # non-interactive, mainly just need to instantiate an object.
            B = Portals(   domain=domain,
                            portal_name=portal_name,
                            user=user,
                            auth=credential,
                            use_token=use_token,
                            debug=debug
            )
            token = credential

        if portal_id is None: # or portal_rid is None:
            B.get_portal_by_name(B.portal_name())
        else:
            B.set_portal_id(portal_id)
            # B.set_portal_rid(portal_rid)
        if get_devices:
            B.map_aliases_to_device_objects()
        return token, B

    def rename_device(self, device_obj, new_name):
        """
            Returns 'device object' of newly created device.
            
            http://docs.exosite.com/portals/#update-device
            http://docs.exosite.com/portals/#device-object
        """
        device_obj['info']['description']['name'] = new_name
        return self.update_device(device_obj)

    def add_device_with_name_location_timezone( self,
                                                model,
                                                serial,
                                                name,
                                                location,
                                                timezone):
        """
            This method wraps the self.add_device() and self.rename_device()
            methods.
            
            Returns device object.
        """
        retval = None
        retval = self.add_location_timezone_to_device(
                    self.rename_device(
                        self.add_device(
                            model,
                            serial),
                        name
                    ),
                    location,
                    timezone
        )
        return retval

    def add_location_timezone_to_device(self, device_obj, location, timezone):
        """
            Returns 'device object' with updated location
            
            http://docs.exosite.com/portals/#update-device
            http://docs.exosite.com/portals/#device-object
        """
        device_obj['info']['description']['meta']['location'] = location
        device_obj['info']['description']['meta']['Location'] = location
        device_obj['info']['description']['meta']['timezone'] = timezone
        device_obj['info']['description']['meta']['Timezone'] = timezone
        return self.update_device(device_obj)

    def delete_device(self, rid):
        """
            Deletes device object with given rid

            http://docs.exosite.com/portals/#delete-device
        """
        headers = {
                'User-Agent': self.user_agent(),
                'Content-Type': self.content_type()
            }
        headers.update(self.headers())
        r = requests.delete(    self.portals_url()+'/devices/'+rid, 
                                headers=headers,
                                auth=self.auth())
        if HTTP_STATUS.NO_CONTENT == r.status_code:
            print("Successfully deleted device with rid: {0}".format(rid))
            return True
        else:
            print("Something went wrong: <{0}>: {1}".format(
                        r.status_code, r.reason))
            r.raise_for_status()
            return False

    def list_portal_data_sources(self):
        """
            List data sources of the portal.

            http://docs.exosite.com/portals/#list-portal-data-source
        """
        headers = {
                'User-Agent': self.user_agent(),
        }
        headers.update(self.headers())

        r = requests.get(   self.portals_url()+'/portals/'+self.portal_id()+'/data-sources',
                    headers=headers,
                    auth=self.auth()
                    )
        if HTTP_STATUS.OK == r.status_code:
            return r.json()
        else:
            print("Something went wrong: <{0}>: {1}".format(
                        r.status_code, r.reason))
            return {}

    def list_device_data_sources(self, device_rid):
        """
            List data sources of a portal device with rid 'device_rid'.

            http://docs.exosite.com/portals/#list-device-data-source
        """
        headers = {
                'User-Agent': self.user_agent(),
        }
        headers.update(self.headers())

        r = requests.get(   self.portals_url()+'/devices/'+device_rid+'/data-sources', 
                    headers=headers, auth=self.auth())
        if HTTP_STATUS.OK == r.status_code:
            return r.json()
        else:
            print("Something went wrong: <{0}>: {1}".format(
                        r.status_code, r.reason))
            return None

    def get_data_source_bulk_request(self, rids, limit=5):
        """
            This grabs each datasource and its multiple datapoints for a particular device.
        """
        headers = {
                'User-Agent': self.user_agent(),
                'Content-Type': self.content_type()
        }
        headers.update(self.headers())

        r = requests.get(   self.portals_url()
                            +'/data-sources/['
                            +",".join(rids)
                            +']/data?limit='+str(limit),
                            headers=headers, auth=self.auth())
        if HTTP_STATUS.OK == r.status_code:
            return r.json()
        else:
            print("Something went wrong: <{0}>: {1}".format(
                        r.status_code, r.reason))
            return {}

    def get_cik(self, rid):
        """
            Retrieves the CIK key for a device.
        """
        device = self.get_device(rid)
        return device['info']['key']

    def get_all_devices_in_portal(self):
        """
            This loops through the get_multiple_devices method 10 rids at a time.
        """
        rids = self.get_portal_by_name(
                        self.portal_name()
                )[2][1]['info']['aliases']

        # print("RIDS: {0}".format(rids))
        device_rids = [ rid.strip() for rid in rids ]

        blocks_of_ten = [ device_rids[x:x+10] for x in range(0, len(device_rids), 10) ]
        devices = []
        for block_of_ten in blocks_of_ten:
            retval = self.get_multiple_devices(block_of_ten)
            if retval is not None:
                devices.extend( retval )
            else:
                print("Not adding to device list: {!r}".format(retval))

        # Parse 'meta' key's raw string values for each device
        for device in devices:
            dictify_device_meta(device)

        return devices

    def map_aliases_to_device_objects(self):
        """
            A device object knows its rid, but not its alias.
            A portal object knows its device rids and aliases.

            This function adds an 'portals_aliases' key to all of the 
            device objects so they can be sorted by alias.
        """
        all_devices = self.get_all_devices_in_portal()
        for dev_o in all_devices:
            dev_o['portals_aliases'] = self.get_portal_by_name(
                                                        self.portal_name()
                                                )[2][1]['info']['aliases'][ dev_o['rid'] ]
        return all_devices

    def search_for_devices_by_serial_number(self, sn):
        """
            Returns a list of device objects that match the serial number
            in param 'sn'.

            This will match partial serial numbers.
        """
        import re

        sn_search = re.compile(sn)

        matches = []
        for dev_o in self.get_all_devices_in_portal():
            # print("Checking {0}".format(dev_o['sn']))
            try:
                if sn_search.match(dev_o['sn']):

                    matches.append(dev_o)
            except TypeError as err:
                print("Problem checking device {!r}: {!r}".format(
                                    dev_o['info']['description']['name'],
                                    str(err)))
        return matches

    def print_device_list(self, device_list=None):
        """
            Optional parameter is a list of device objects. If omitted, will
            just print all portal devices objects.
        """
        dev_list = device_list if device_list is not None else self.get_all_devices_in_portal()

        for dev in dev_list:
            print('{0}\t\t{1}\t\t{2}'.format(
                    dev['info']['description']['name'],
                    dev['sn'],
                    dev['portals_aliases']\
                        if len(dev['portals_aliases']) != 1
                        else dev['portals_aliases'][0]
                )
            )

    def print_sorted_device_list(self, device_list=None, sort_key='sn'):
        """
            Takes in a sort key and prints the device list according to that sort.

            Default sorts on serial number.

            Current supported sort options are:
                - name
                - sn
                - portals_aliases

            Can take optional device object list.
        """
        dev_list = device_list if device_list is not None else self.get_all_devices_in_portal()
        sorted_dev_list = []
        if sort_key == 'sn':
            sort_keys = [ k[sort_key] for k in dev_list if k[sort_key] is not None ]
            sort_keys = sorted(sort_keys)
            for key in sort_keys:
                sorted_dev_list.extend([ d for d in dev_list if d['sn'] == key ])

        elif sort_key == 'name':
            sort_keys = [ k['info']['description'][sort_key]\
                    for k in dev_list if k['info']['description'][sort_key] is not None ]
            sort_keys = sorted(sort_keys)
            for key in sort_keys:
                sorted_dev_list.extend( [ d for d in dev_list\
                                            if d['info']['description'][sort_key] == key
                                        ]
                )

        elif sort_key == 'portals_aliases':
            sort_keys = [ k[sort_key] for k in dev_list if k[sort_key] is not None ]
            sort_keys = sorted(sort_keys)
            for key in sort_keys:
                sorted_dev_list.extend([ d for d in dev_list if d[sort_key] == key ])

        else:
            print("Sort key {!r} not recognized.".format(sort_key))
            sort_keys = None

        self.print_device_list(device_list=sorted_dev_list)

    def get_user_id_from_email(self, email):
        """ Uses the get-all-user-accounts Portals API to retrieve the
        user-id by supplying an email. """
        accts = self.get_all_user_accounts()

        for acct in accts:
            if acct['email'] == email:
                return acct['id']
        return None

    def get_user_permission_from_email(self, email):
        """ Returns a user's permissions object when given the user email."""
        _id = self.get_user_id_from_email(email)
        return self.get_user_permission(_id)

    def add_dplist_permission_for_user_on_portal(self, user_email, portal_id):
        """ Adds the 'd_p_list' permission to a user object when provided
            a user_email and portal_id."""
        _id = self.get_user_id_from_email(user_email)
        print(self.get_user_permission_from_email(user_email))
        retval = self.add_user_permission(  _id, json.dumps( 
                        [{'access': 'd_p_list', 'oid':{'id': portal_id, 'type':'Portal'}}] 
                )
        )
        print(self.get_user_permission_from_email(user_email))
        return retval

    def get_portal_cik(self, portal_name):
        """ Retrieves portal object according to 'portal_name' and
        returns its cik. """
        portal = self.get_portal_by_name(portal_name)
        cik = portal[2][1]['info']['key']
        return cik
