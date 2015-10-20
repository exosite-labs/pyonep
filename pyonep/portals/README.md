# Portals API support in pyonep
This package contains python modules, classes and methods for supporting 
the Portals API in interactive programs such as bpython and IPython as well 
as for creating custom Web Applications for customers already using Portals.

## Sample Usage

```
(pyonep3)[will@W-MB-P|11:29:19|~/projects/pyonep](master)
$ bpython
bpython version 0.14.2 on top of Python 3.4.1 /Users/willcharlton/.virtualenvs/pyonep3/bin/python3
>>> from pyonep.portals.bindings import Bindings
>>> token, B = Bindings.login_to_portal()
Enter domain: willcharlton.exosite.com
Enter name of Portal: APtivator
Enter username: willcharlton

Enter User Password: 
>>> token
'"GW9RKLa3Rfq70B9Q5XuIRKl23ko56fRJCG1Gljhv87o8fdtcvbPTpg2AObCb6wIi9XQDDB5fWOIDxD_M7iB8RwVF"'
>>> B
<pyonep.portals.bindings.Bindings object at 0x10356d278>
>>> B.portal_cik()
'4bc278b*********************************'
>>> all_devices = B.get_all_devices_in_portal()
>>> my_permissions = B.get_user_permission_from_email('willcharlton@exosite.com')
>>> my_permissions
[{'oid': {'id': '08899e*********************************', 'type': 'Device'}, 'access': '___admin'}, {'oid': {'id': '129ecc2*********
************************', 'type': 'Device'}, 'access': '___admin'}, {'oid': {'id': '17f7dea7*********************************', 'typ
e': 'Device'}, 'access': '___admin'}, {'oid': {'id': '1af911f*********************************', 'type': 'Device'}, 'access': '___adm
in'}, {'oid': {'id': '37a3201d1*********************************', 'type': 'Device'}, 'access': '___admin'}, {'oid': {'id': '46a4781a**
*******************************', 'type': 'Device'}, 'access': '___admin'}, {'oid': {'id': '5dc867d69*********************************',
 'type': 'Device'}, 'access': '___admin'}, {'oid': {'id': '7ab367ec*********************************', 'type': 'Device'}, 'access': '_
__admin'}, {'oid': {'id': '7d977ab*********************************', 'type': 'Device'}, 'access': '___admin'}, {'oid': {'id': '84d88
40*********************************', 'type': 'Device'}, 'access': '___admin'}, {'oid': {'id': '9f7b05e3******************************
***', 'type': 'Device'}, 'access': '___admin'}, {'oid': {'id': 'bcae0c794*********************************', 'type': 'Device'}, 'access
': '___admin'}, {'oid': {'id': 'e02713e4*********************************', 'type': 'Device'}, 'access': '___admin'}, {'oid': {'id': '
e19232ca*********************************', 'type': 'Device'}, 'access': '___admin'}, {'oid': {'id': 'e33a2f95***********************
**********', 'type': 'Device'}, 'access': '___admin'}, {'oid': {'id': 'f6a1d366d*********************************', 'type': 'Device'}, 
'access': '___admin'}, {'oid': {'id': '1479******', 'type': 'Domain'}, 'access': '___admin'}, {'oid': {'id': '15207*****', 'type': 'Por
tal'}, 'access': '___admin'}, {'oid': {'id': '12400*****', 'type': 'Portal'}, 'access': '___admin'}]
>>> B.get_user_id_from_email(
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ B.get_user_id_from_email: (self, email)                                                                │
│ get_user_id_from_email                                                                                 │
│ Uses the get-all-user-accounts Portals API to retrieve the user-id by supplying an email.              │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘

```

This has been tested on Python 2.7.9 and Python 3.4.1. 