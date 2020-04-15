import json
import logging
import os
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
  

from ..s3dynamodb import download,upload

telType={
  "STRING":str,
  "INTEGER":int,
  "REAL":float,
  "LOGICAL":bool
}

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


def _f(dico,key,value):
  type=telType[dico[key]["TYPE"]]
  if isinstance(value,list):
    for item in value:
      if not isinstance(item,type):logger.warning("Keyword={0},Value={1} is not {2}".format(key,item,type))
  else:  
    if not isinstance(value,type):logger.warning("Keyword={0},Value={1} is not {2}".format(key,value,type))
  return value

def _downloadFile(id,localFolder,TableData,key,value,isDownload):
  """ Get local file path and download file from S3
  """
  item=dynoget(id=id,TableName=TableData)
  if item is None:logger.error("Keyword={0},Value={1} does not exist".format(key,value));return
  fileName = "{}.{}".format(item['name'],item['type'])
  filePath=os.path.join(localFolder,fileName)
  
  if isDownload:download(filePath,TableName=TableData,**item)
  return "'{}'".format(fileName)
  


def validate(id,
  localFolder=os.environ.get('TELEMAC_LOCALFOLDER',""),
  TableCas=os.environ.get('AWS_TABLECAS',None),
  TableData=os.environ.get('AWS_TABLEDATA',None),
  isDownload=False,
  **kwargs
  ):
  """ Validate/Download cas 
  """
  if TableCas is None:raise Exception("Needs TableCas")
  if TableData is None:raise Exception("Needs TableData")

  item=dynoget(id=id,TableName=TableCas)
  
  module=item['module']
  Filename="dico/{}.dico.json".format(module)
  Filename=os.path.join(os.path.dirname(os.path.realpath(__file__)),Filename)
  if not os.path.exists(Filename):raise Exception("Module dictionary does not exist- {}".format(module))
  with open(Filename) as json_file:
    dico = json.load(json_file)
  
  strCas=""
  keywords=item['keywords']
  for key in keywords:
    key=key.upper()
    if not key in dico:logger.warning("Keyword={0} does not exist in {1} dictionary".format(key,module));continue
    
    value=keywords[key]
    
    if key=="FORTRAN FILE":
      if not isinstance(value,list):logger.warning("Keyword={0},Value={1} requires a list".format(key,value));continue
      value=_f(dico,key,value)
      fortranFolder=os.path.join(localFolder,"user_fortran")
      if not os.path.exists(fortranFolder):os.mkdir(fortranFolder)
      for id in value:
        _downloadFile(id,fortranFolder,TableData,key,value,isDownload)
      strValue="'user_fortran'"
    else:
      #
      # Validate values
      #
      
      if "APPARENCE" in dico[key]:
        # list type
        if not isinstance(value,list):logger.warning("Keyword={0},Value={1} requires a list".format(key,value));continue
        value=_f(dico,key,value)
        sep="," if dico[key]['APPARENCE']=="DYNLIST2" else ";"
        strValue=sep.join(value)
      else:
        # float,int,bool,string type
        strValue=_f(dico,key,value)
        #
        # Validate file: Get item from dynanodb, create filePath and download.
        #
        if "FILE" in key:
          strValue=_downloadFile(value,localFolder,TableData,key,value,isDownload)

    strCas+="{} = {}\n".format(key,strValue)
    
  if isDownload:
    casPath ="{}.cas".format(item['name'])
    casPath = os.path.join(localFolder,casPath)
    with open(casPath,"w") as file:
      file.write(strCas)
  return logging  

def get(id,**kwargs):
  """   
  """
  return validate(id,isDownload=True,**kwargs)

