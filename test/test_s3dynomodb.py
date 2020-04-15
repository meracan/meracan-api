# import pytest
import os

from boto3.dynamodb.conditions import Key, Attr
from meracanapi.s3dynamodb import upload,download,delete

def test_s3():
  """ Testing S3DynamoDBTableCas
  """
  access={"BucketName":"mercantest","TableName":"TestTableData"}
  item=upload(Filename="meracan-api/test/data/test.txt",**access)
  download(id=item['id'],Filename="meracan-api/test/data/test.2.txt",**access)
  delete(id=item['id'],**access)

def test_temp():
  """ Temporary testing. Delete when done.
  """
  None
  

if __name__ == "__main__":
  test_s3()
  # test_temp()

  