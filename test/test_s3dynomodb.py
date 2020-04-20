import pytest
import time
from meracanapi import S3DynamoDB

def test_s3():
  """ Testing S3DynamoDB
  """
  s3dyno=S3DynamoDB(BucketName="mercantest",TableName="TestTableData")
  
  # Upload file to S3 and DynamoDB
  item=s3dyno.upload(Filename="test/data/test.txt")
  
  # Download file to specific path
  Filename=s3dyno.download(Filename="test/output/test.1.txt",id=item['id'])
  time.sleep(1)
  with open(Filename,"r") as file:assert file.read()=="This is a test file"
  
  # Download file to folder using name and type from DynamoDB
  Filename=s3dyno.download(localFolder="test/output",id=item['id'])
  time.sleep(1)
  with open(Filename,"r") as file:assert file.read()=="This is a test file"
  
  # Update file
  s3dyno.upload(Filename="test/data/update.txt",id=item['id'])
  
  # Download updated file to specific path
  Filename=s3dyno.download(Filename="test/output/update.txt",id=item['id'])
  time.sleep(1)
  with open(Filename,"r") as file:assert file.read()=="This is the updated file"
  
  # Delete file
  s3dyno.delete(id=item['id'])
  
  # List all files in s3
  s3dyno.s3list()


if __name__ == "__main__":
  test_s3()
  # test_temp()

  