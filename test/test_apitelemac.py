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

def test_apitelemac():
#   """ Testing DynamoDBTableCas
#   """
  access={"TableCas":"TestTableCas","TableData":"TestTableData","BucketName":"mercantest"}
  uploadFile('meracan-api/test/data/telemac2d/bump/t2d_bump_FE.cas',**access)
  
  # f1=upload(Filename="meracan-api/test/data/user_fortran/a.f",TableName="TestTableData",BucketName="mercantest")
#   f2=upload(Filename="meracan-api/test/data/user_fortran/b.f",TableName="TestTableData",BucketName="mercantest")
#   geo=upload(Filename="meracan-api/test/data/geo.slf",TableName="TestTableData",BucketName="mercantest")
#   lqd=upload(Filename="meracan-api/test/data/lqd.lqd",TableName="TestTableData",BucketName="mercantest")
  
#   keywords={
#     "GEOMETRY FILE":geo['id'],
#     "FORTRAN FILE":[f1['id'],f2['id']],
#     "LIQUID BOUNDARIES FILE":lqd['id']
#   }
#   item=create("general","cas1",keywords,**access)
  
#   # item=listall(**access)[1]
#   validate(**item,**access)
#   get(**item,**access,localFolder="meracan-api/test/data/model")
  

if __name__ == "__main__":
  # test_TelemacCas()
  test_apitelemac()
  

  