from onepv1lib.provision import Provision

if __name__ == '__main__':
  ownercik  = 'VENDOR-CIK'
  clonerid  = 'CLONE-TEMPLATE-RID'
  sn_owner  = 'DEVICE-CLIENT-OWNER-RID'
  provision = Provision('http://127.0.0.1:8080')
  model  ='test_model'
  vendor = 'exosite'
  provision.vendor_register(ownercik, vendor)
  provision.model_create(ownercik, model, clonerid)
  print provision.model_list(ownercik)
  print provision.model_info(ownercik, model)
  provision.serialnumber_add(ownercik, model, '001')
  provision.serialnumber_add_batch(ownercik, model, ['002','003'])
  print provision.serialnumber_list(ownercik, model)
  provision.serialnumber_remove_batch(ownercik, model, ['002','003'])
  print provision.serialnumber_list(ownercik, model)
  provision.serialnumber_enable(ownercik, model, '001',sn_owner) ## return clientid
  print "AFTER ENABLE:",provision.serialnumber_info(ownercik, model, '001')
  provision.serialnumber_disable(ownercik, model, '001')
  print "AFTER DISABLE:",provision.serialnumber_info(ownercik, model, '001')
  provision.serialnumber_reenable(ownercik, model, '001')
  print "AFTER REENABLE:",provision.serialnumber_info(ownercik, model, '001')
  sn_cik = provision.serialnumber_activate(ownercik, model, '001') ##return client key
  print "AFTER ACTIVATE:",provision.serialnumber_info(ownercik, model, '001')
  content_id = "a.txt"
  content_data = "This is content data"
  provision.content_create(ownercik, model ,content_id, "This is a.txt!")
  print provision.content_list(ownercik, model)
  provision.content_upload(ownercik, model, content_id, content_data, "text/plain")
  print provision.content_info(ownercik, model, content_id)
  provision.content_download(sn_cik, vendor, model, content_id)
  provision.content_remove(ownercik, model, content_id)  
  provision.model_remove(ownercik, model)
  provision.vendor_unregister(ownercik, vendor)
