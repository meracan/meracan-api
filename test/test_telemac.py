# import pytest
import os

from boto3.dynamodb.conditions import Key, Attr
from meracanapi.s3dynamodb import upload,download,delete
from meracanapi.telemac import create,delete,update,listall,query,scan,validate,get

def test_telemac():
  """ Testing DynamoDBTableCas
  """
  access={"TableCas":"TestTableCas","TableData":"TestTableData"}
  
  f1=upload(Filename="meracan-api/test/data/user_fortran/a.f",TableName="TestTableData",BucketName="mercantest")
  f2=upload(Filename="meracan-api/test/data/user_fortran/b.f",TableName="TestTableData",BucketName="mercantest")
  geo=upload(Filename="meracan-api/test/data/geo.slf",TableName="TestTableData",BucketName="mercantest")
  lqd=upload(Filename="meracan-api/test/data/lqd.lqd",TableName="TestTableData",BucketName="mercantest")
  
  keywords={
    "GEOMETRY FILE":geo['id'],
    "FORTRAN FILE":[f1['id'],f2['id']],
    "LIQUID BOUNDARIES FILE":lqd['id']
  }
  item=create("general","cas1",keywords,**access)
  
  # item=listall(**access)[1]
  validate(**item,**access)
  get(**item,**access,localFolder="meracan-api/test/data/model")
  
  

  

if __name__ == "__main__":
  test_telemac()

  