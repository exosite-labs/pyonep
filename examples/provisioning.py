#==========================================================================
# provisioning.py
# Demonstrates use of the provision API
#==========================================================================
##
## Tested with python 2.7.2
##
## Copyright (c) 2014, Exosite LLC
## All rights reserved.
##
import sys
import random
import logging
try:
  import httplib
except:
  # python 3
  from http import client as httplib


import pyonep
from pyonep.provision import Provision
from pyonep.onep import OnepV1
from pyonep.exceptions import ProvisionException

# configure logging
logging.basicConfig(stream=sys.stderr)
# change these to logging.DEBUG for verbose debug output
logging.getLogger("pyonep.onep").setLevel(logging.ERROR)
logging.getLogger("pyonep.provision").setLevel(logging.ERROR)

if __name__ == '__main__':
    # Vendor token and name are listed at the top of
    # https://<your domain>.exosite.com/admin/managemodels
    # (Vendor token is also available on the domain admin home page)
    vendorname = 'YOUR_VENDOR_NAME'
    vendortoken = 'YOUR_VENDOR_TOKEN'
    # CIK of client to clone for model
    clonecik = 'YOUR_CLONE_CIK'
    # CIK of parent of clonecik client. In the case of Portals,
    # this is the CIK of the portal. It can be found in your portal under
    # Account > Portals
    # Look for: Key: 123abc...
    portalcik = 'YOUR_PORTAL_CIK'

    print('pyonep version ' + pyonep.__version__)
    r = random.randint(1, 10000000)
    model = 'MyTestModel' + str(r)
    sn1 = '001' + str(r)
    sn2 = '002' + str(r)
    sn3 = '003' + str(r)
    op = OnepV1()
    isok, portalrid = op.lookup(portalcik, 'alias', '')
    if not isok:
        print("Failed to look up portal RID")
    else:
        print("portalrid: '{}'".format(portalrid))
    isok, clonerid = op.lookup(clonecik, 'alias', '')
    if not isok:
        print("Failed to look up clone RID")
        exit()
    else:
        print("clonerid: '{}'".format(clonerid))
        provision = Provision('m2.exosite.com', https=True, port=443, manage_by_cik=False, verbose=False, raise_api_exceptions=True)
    try:
        print("model_create()")
        provision.model_create(vendortoken, model, clonerid, aliases=False)

        # production code should read isok before using body
        print provision.model_list(vendortoken).body
        print provision.model_info(vendortoken, model).body
        print("serialnumber_add()")
        provision.serialnumber_add(vendortoken, model, sn1)
        print("serialnumber_add_batch()")
        provision.serialnumber_add_batch(vendortoken, model, [sn2, sn3])
        print provision.serialnumber_list(vendortoken, model, limit=10).body
        print("serialnumber_remove_batch()")
        provision.serialnumber_remove_batch(vendortoken, model, [sn2, sn3])
        print provision.serialnumber_list(vendortoken, model).body
        print("serialnumber_enable()")
        provision.serialnumber_enable(vendortoken, model, sn1, portalrid)  # return clientid
        print "AFTER ENABLE:", provision.serialnumber_info(vendortoken, model, sn1).body
        print("serialnumber_disable()")
        provision.serialnumber_disable(vendortoken, model, sn1)
        print "AFTER DISABLE:", provision.serialnumber_info(vendortoken, model, sn1).body
        print("serialnumber_reenable()")
        provision.serialnumber_reenable(vendortoken, model, sn1)
        print "AFTER REENABLE:", provision.serialnumber_info(vendortoken, model, sn1).body
        print("serialnumber_activate()")
        sn_cik = provision.serialnumber_activate(model, sn1, vendorname).body  # return client key
        print "AFTER ACTIVATE:", provision.serialnumber_info(vendortoken, model, sn1).body
        content_id = "a.txt"
        content_data = "This is content data"
        print("content_create()")
        provision.content_create(vendortoken, model, content_id, "This is text")
        print provision.content_list(vendortoken, model)
        print("content_upload()")
        print provision.content_upload(vendortoken, model, content_id, content_data, "text/plain")
        print provision.content_list(vendortoken, model)
        print provision.content_info(vendortoken, model, content_id)
        print("content_download()")
        print provision.content_download(sn_cik, vendorname, model, content_id)
        print("content_remove()")
        provision.content_remove(vendortoken, model, content_id)
        print("model_remove()")
        provision.model_remove(vendortoken, model)
    except ProvisionException:
        ex = sys.exc_info()[1]
        print('API Error: {0} {1}'.format(ex.response.status(), ex.response.reason()))
    except httplib.HTTPException:
        ex = sys.exc_info()[1]
        print('HTTPException: {0}'.format(ex))
