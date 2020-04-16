import json
import logging
import os
import time
import uuid
import boto3
from urllib.parse import urlparse
from ..dynamodb import create,delete as dynodelete,get,listall,update,query,dump,scan


def download(Filename,**kwargs):
  item=get(**kwargs)
  s3 = boto3.resource('s3')
  bucket = s3.Bucket(item['BucketName'])
  bucket.download_file(item['ObjectKey'], Filename)

def delete(**kwargs):
  item=get(**kwargs)
  s3 = boto3.resource('s3')
  bucket = s3.Bucket(item['BucketName'])
  response = bucket.delete_objects(Delete={'Objects': [{'Key':item['ObjectKey']}]})
  dynodelete(**kwargs)
  return response

def upload(Filename,BucketName=os.environ.get('AWS_BUCKETNAME',None),projectId="general",s3folder="data",**kwargs):
  s3 = boto3.resource('s3')
  if BucketName is None: raise Exception("Need BucketName")
  bucket = s3.Bucket(BucketName)
  
  Key=os.path.join(s3folder, str(uuid.uuid4()))
  bucket.upload_file(Filename=Filename,Key=Key)
  
  name = os.path.splitext(os.path.basename(Filename))[0]
  type = Filename.split(os.extsep).pop()
  item=create(name=name,projectId=projectId,type=type,BucketName=BucketName,ObjectKey=Key,**kwargs)
  return item