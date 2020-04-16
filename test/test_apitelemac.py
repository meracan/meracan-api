# import pytest
import os


from meracanapi.s3dynamodb import upload,download,delete
from meracanapi.apitelemac import TelemacCas,create,delete,update,listall,query,scan,download,uploadFile

def test_TelemacCas():
  study=TelemacCas('telemac2d','meracan-api/test/data/telemac2d/bump/t2d_bump_FE.cas')
  print(study)
  
  keywords={
    
    "GEOMETRY FILE":"geo.slf",
    "FORTRAN FILE":["f1.f","f2.f"],
    "LIQUID BOUNDARIES FILE":"lqd.lqd",
    "MASS-BALANCE":True,
  }
  study=TelemacCas('telemac2d')
  study.setValues(keywords)
  study.write("meracan-api/test/data/test.cas")

def test_apitelemac_upload():
#   """ Testing DynamoDBTableCas
#   """
  access={"TableCas":"TestTableCas","TableData":"TestTableData","BucketName":"mercantest"}
  uploadFile('meracan-api/test/data/telemac2d/bump/t2d_bump_FE.cas',**access)

def test_apitelemac_download():
  access={"TableCas":"TestTableCas","TableData":"TestTableData","BucketName":"mercantest"}
  download("0221693c-8da3-4f93-8aa0-dd21b5b9828e",**access)

if __name__ == "__main__":
  # test_TelemacCas()
  # test_apitelemac_upload()
  test_apitelemac_download()
  

  