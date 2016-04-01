#==========================================================================
# provisioning.py
# Demonstrates use of the provision API
#==========================================================================
#
# Tested with python 2.7.2
#
# Copyright (c) 2014, Exosite LLC
# All rights reserved.
#
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

def provision_example(vendorname, vendortoken, clonerid, portalcik, portalrid):
    print('pyonep version ' + pyonep.__version__)
    r = random.randint(1, 10000000)
    model = 'MyTestModel' + str(r)
    sn1 = '001' + str(r)
    sn2 = '002' + str(r)
    sn3 = '003' + str(r)
    op = OnepV1()

    provision = Provision('m2.exosite.com',
                            https=True,
                            port=443,
                            manage_by_cik=False,
                            verbose=False,
                            httptimeout=20,
                            raise_api_exceptions=True,
                            manage_by_sharecode=True)
    # manage by sharecode
    option = "[\"" + vendorname + "\", \"" + model +"\"]"
    meta = {"meta" : option}
    print("op.share", portalcik, clonerid, meta)
    isok, sharecode = op.share(portalcik, clonerid, meta)
    if not isok:
        print("failed to create share code")
        return False
    try:
        print("model_create() ", vendortoken, model, sharecode)
        provision.model_create(vendortoken, model, sharecode, aliases=False)

        # production code should read isok before using body
        print("model_list()")
        print(provision.model_list(vendortoken).body)
        print(provision.model_info(vendortoken, model).body)
        print("serialnumber_add()")
        provision.serialnumber_add(vendortoken, model, sn1)
        print("serialnumber_add_batch()")
        provision.serialnumber_add_batch(vendortoken, model, [sn2, sn3])
        print(provision.serialnumber_list(vendortoken, model, limit=10).body)
        print("serialnumber_remove_batch()")
        provision.serialnumber_remove_batch(vendortoken, model, [sn2, sn3])
        print(provision.serialnumber_list(vendortoken, model).body)
        print("serialnumber_enable()")
        provision.serialnumber_enable(
            vendortoken, model, sn1,
            portalrid)  # return clientid
        print("AFTER ENABLE:", provision.serialnumber_info(vendortoken,
                                                           model, sn1).body)
        print("serialnumber_disable()")
        provision.serialnumber_disable(vendortoken, model, sn1)
        print("AFTER DISABLE:", provision.serialnumber_info(vendortoken,
                                                            model, sn1).body)
        print("serialnumber_reenable()")
        provision.serialnumber_reenable(vendortoken, model, sn1)
        print("AFTER REENABLE:", provision.serialnumber_info(vendortoken,
                                                             model, sn1).body)
        print("serialnumber_activate()")

        # return client key,
        sn_cik = provision.serialnumber_activate(model, sn1, vendorname).body
        print("AFTER ACTIVATE:", provision.serialnumber_info(vendortoken,
                                                             model, sn1).body)

        def test_content(content_id, content_data, content_type, content_meta):
            print("content_create()")
            provision.content_create(vendortoken, model, content_id,
                                    content_meta)
            print(provision.content_list(vendortoken, model))
            print("content_upload()")
            print(provision.content_upload(vendortoken, model, content_id,
                                        content_data, content_type))
            print(provision.content_list(vendortoken, model))
            print(provision.content_info(vendortoken, model, content_id))
            print("content_download()")
            print(provision.content_download(sn_cik, vendorname, model, content_id))
            print("content_remove()")
            provision.content_remove(vendortoken, model, content_id)

        test_content("a.txt", "This is content data", "text/plain", "This is text")

        # TODO: binary content

        print("model_remove()")
        provision.model_remove(vendortoken, model)
    except ProvisionException:
        ex = sys.exc_info()[1]
        print('API Error: {0} {1}'.format(ex.response.status(),
                                          ex.response.reason()))
        return False
    except httplib.HTTPException:
        ex = sys.exc_info()[1]
        print('HTTPException: {0}'.format(ex))
        return False

    # no error
    return True

if __name__ == '__main__':
    # To make tests run, keep test/testconfig.py.template in sync with this.
    provision_example(
        # Vendor token and name are listed at the top of
        # https://<your domain>.exosite.com/admin/managemodels
        # (Vendor token is also available on the domain admin home page)
        vendorname='<VENDOR NAME HERE>',
        vendortoken='<VENDOR TOKEN HERE>',
        # RID of client to clone for model
        clonerid='<CLONE DEVICE RID HERE>',
        # CIK and RID of portal of client to clone for model
        portalcik='<PORTAL CIK HERE>',
        portalrid='<PORTAL RID HERE>',
    )
