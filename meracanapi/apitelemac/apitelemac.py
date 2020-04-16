import json
import logging
import os
from decimal import Decimal
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

from ..dynamodb import \
  create as dynocreate,\
  delete as dynodelete,\
  update as dynoupdate,\
  get as dynoget,\
  listall as dynolist,\
  query as dynoquery,\
  scan as dynoscan
  
from .cas2json.telemac_cas import TelemacCas
from ..s3dynamodb import download as dynodownload,upload as dynoupload


def create(projectId,name,keywords,module="telemac2d",TableCas=os.environ.get('AWS_TABLECAS',None),**kwargs):
  if TableCas is None:raise Exception("Needs TableCas")
  return dynocreate(projectId=projectId,name=name,keywords=keywords,module=module,TableName=TableCas)

def pre(function):
  """ Decorator for ...
  """
  def wrapper(**kwargs):
    kwargs['TableName'] = kwargs.pop('TableCas',os.environ.get('AWS_TABLECAS'))
    return function(**kwargs)
  return wrapper
@pre
def delete(**kwargs):
  return dynodelete(**kwargs)    
@pre
def update(**kwargs):
  return dynoupdate(**kwargs)
@pre
def listall(**kwargs):
  return dynolist(**kwargs)
@pre
def query(**kwargs):
  return dynoquery(**kwargs)
@pre
def scan(**kwargs):
  return dynoscan(**kwargs)

def _downloadFile(id,localFolder,TableData,key,value):
  """ Get local file path and download file from S3
  """
  item=dynoget(id=id,TableName=TableData)
  if item is None:
    logger.error("Keyword={0},Value={1} does not exist".format(key,value))
    return None
  fileName = "{}.{}".format(item['name'],item['type'])
  filePath=os.path.join(localFolder,fileName)
  dynodownload(filePath,TableName=TableData,**item)
  return "'{}'".format(fileName)
  

def download(id,
  localFolder=os.environ.get('TELEMAC_LOCALFOLDER',""),
  TableCas=os.environ.get('AWS_TABLECAS',None),
  TableData=os.environ.get('AWS_TABLEDATA',None),
  **kwargs
  ):
  """ Download cas and files
  """
  if TableCas is None:raise Exception("Needs TableCas")
  if TableData is None:raise Exception("Needs TableData")

  item=dynoget(id=id,TableName=TableCas)
  study=TelemacCas(item['module'])
  study.setValues(item['keywords'])  
  
  for key in study.in_files:
    value=study.values[key]
    study.values[key]=_downloadFile(value,localFolder,TableData,key,value)
  casPath ="{}.cas".format(item['name'])
  casPath = os.path.join(localFolder,casPath)
  study.write(casPath)
  return logging  

def uploadFile(casFile,
  projectId="general",
  name=None,
  module="telemac2d",
  localFolder=os.environ.get('TELEMAC_LOCALFOLDER',""),
  TableCas=os.environ.get('AWS_TABLECAS',None),
  TableData=os.environ.get('AWS_TABLEDATA',None),
  BucketName=os.environ.get('AWS_BUCKETNAME',None),
  **kwargs
  ):
  """ Upload cas and files
  """
  if TableCas is None:raise Exception("Needs TableCas")
  if TableData is None:raise Exception("Needs TableData")
  if BucketName is None:raise Exception("Needs BucketName")

  study=TelemacCas(module,casFile)
  
  if name is None:
    name=os.path.splitext(os.path.basename(casFile))[0]
    
  def _upload(file):
    f=dynoupload(Filename=file,TableName=TableData,BucketName=BucketName)
    return f['id']
  
  for key in study.in_files:
    if key=="FORTRAN FILE":
      files=study.values[key]
      study.values[key]=[_upload(file) for file in files]
    else:
      file=study.values[key]
      study.values[key]=_upload(file)

  ddb_data = json.loads(json.dumps(study.values), parse_float=Decimal)
  create(projectId,name,ddb_data,TableCas=TableCas,TableData=TableData)
  
  # TODO: if error, delete all
  
  return logging