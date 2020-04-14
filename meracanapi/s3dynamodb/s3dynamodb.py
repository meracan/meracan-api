import json
import logging
import os
import time
import uuid
import boto3
from urllib.parse import urlparse
from ..dynamodb import create,delete as dynodelete,get,listall,update,query,dump,scan


def download(kwargs):
  Filename=kwargs.pop("Filename")
  item=get(kwargs)
  
  s3 = boto3.resource('s3')
  bucket = s3.Bucket(item['s3Bucket'])
  bucket.download_file(item['s3Key'], Filename)

def delete(kwargs):
  item=get(kwargs)
  s3 = boto3.resource('s3')
  bucket = s3.Bucket(item['s3Bucket'])
  response = bucket.delete_objects(Delete={'Objects': [{'Key':item['s3Key']}]})
  dynodelete(kwargs)
  return response

def upload(kwargs):
  s3 = boto3.resource('s3')
  bucket = s3.Bucket(kwargs.get('BucketName'))
  Filename=kwargs.get("Filename")
  Key=str(uuid.uuid4())
  bucket.upload_file(Filename=Filename,Key=Key)
  
  
  BucketName=kwargs.pop("BucketName")
  projectId=kwargs.pop("projectId","general")
  name = os.path.splitext(os.path.basename(Filename))[0]
  type = Filename.split(os.extsep).pop()
  item=create({"name":name,"projectId":projectId,"type":type,"s3Bucket":BucketName,"s3Key":Key,**kwargs})
  return item