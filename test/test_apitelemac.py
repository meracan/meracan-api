# import pytest
import os

from meracanapi import ApiTelemac

access={"TableCas":"TestTableCas","TableData":"TestTableData","BucketName":"mercantest"}

def test_ApiTelemac():
  
  api=ApiTelemac(localFolder="test/output",**access)
  
  # Upload/Donwload cas file and files
  item=api.upload(Filename='test/data/telemac2d/confluence/t2d_confluence.cas')
  cas,item=api.download(**item)
  
  #  Update keyword
  api.update(id=item['id'],keywords={"FRICTION COEFFICIENT":30})
  cas,item=api.download(**item)
  
  # Add liquid boundary file (example) and re-download
  lqd=api.uploadFile(id=item['id'],keyword="LIQUID BOUNDARIES FILE",Filename='test/data/telemac2d/confluence/dummy.lqd')
  cas,item=api.download(**item)
  
  # Add fortran file (example) and re-download
  f=api.addFortran(id=item['id'],Filename='test/data/telemac2d/confluence/other.f')
  cas,item=api.download(**item)
  
  # Remove fortran file (example) and re-download
  api.rmFortran(id=item['id'],fortranId=f['id'])
  cas,item=api.download(**item)
  
def test_ApiTelemac_Run():
  api=ApiTelemac(localFolder="test/output",**access)
  
  # Upload/Donwload cas file and files
  item=api.upload(Filename='test/data/telemac2d/confluence/t2d_confluence.cas')
  api.run(item['id'])
  
if __name__ == "__main__":
  # test_ApiTelemac()
  test_ApiTelemac_Run()
  

  