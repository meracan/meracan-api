import json
import logging
import os
from decimal import Decimal
from telapy.api.t2d import Telemac2d
from telapy.api.t3d import Telemac3d
from telapy.api.t2d import Telemac2d
from mpi4py import MPI
import numpy as np

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

from ..dynamodb import \
  create as dynocreate,\
  delete as dynodelete,\
  update as dynoupdate,\
  updateValue as dynoupdatevalue,\
  get as dynoget,\
  listall as dynolist,\
  query as dynoquery,\
  scan as dynoscan

from ..dynamodb.decimalencoder import DecimalEncoder
  
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
  return "{}".format(fileName)
  

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
  db_data = json.loads(json.dumps(item['keywords'],cls=DecimalEncoder))
  study.setValues(db_data)  
  
  for key in study.in_files:
    value=study.values[key]
    if isinstance(value,list):
      # FORTRAN FILE
      fortran_path=os.path.join(localFolder,"user_fortran")
      if not os.path.exists(fortran_path):
        os.mkdir(fortran_path)
      study.values[key]=[_downloadFile(_value,fortran_path,TableData,key,_value) for _value in value]
    else:  
      study.values[key]=_downloadFile(value,localFolder,TableData,key,value)
  
  casPath ="{}.cas".format(item['name'])
  casPath = os.path.join(localFolder,casPath)
  study.write(casPath)
  return casPath,item

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
  

def run(casFile,
  item,
  recompile=True,
  TableCas=os.environ.get('AWS_TABLECAS',None),
  ):
    if TableCas is None:raise Exception("Needs TableCas")  
    os.chdir(os.path.dirname(casFile))
    comm = MPI.COMM_WORLD
    
    if item['module']=='telemac3d':
      study = Telemac3d(casFile, user_fortran='user_fortran',comm=comm, stdout=0)
    else:
      study = Telemac2d(casFile, user_fortran='user_fortran',comm=comm, stdout=0)
    
    ilprintout = study.cas.values.get("LISTING PRINTOUT PERIOD",study.cas.dico.data["LISTING PRINTOUT PERIOD"])
    igprintout = study.cas.values.get("GRAPHIC PRINTOUT PERIOD",study.cas.dico.data["GRAPHIC PRINTOUT PERIOD"])
    

    # print()
    # raise Exception("here")
    study.set_case()
    # Initalization
    study.init_state_default()
    
    # 
    ntimesteps = study.get("MODEL.NTIMESTEPS")
    
    # Get global npoin, # Get global/local index
    if study.ncsize>1:
      data = np.zeros(study.ncsize,dtype=np.int)
      data[comm.rank]=np.max(study.get_array("MODEL.KNOLG"))
      npoin=np.max(comm.allreduce(data, MPI.SUM))
      index=study.get_array("MODEL.KNOLG").astype(np.int)-1
    else:
      npoin=study.get("MODEL.NPOIN")
      index= np.arange(npoin,dtype=np.int)
    
    for _ in range(ntimesteps):
        study.run_one_time_step()
        if _%ilprintout==0 and comm.rank==0:
          print(_)
          dynoupdatevalue(id=item['id'],progress=(float(_))/ntimesteps,TableName=TableCas)
            
        if _%igprintout==0:
          if comm.rank==0:
            None
            # values = np.zeros(npoin)
            # values[index]=study.get_array("MODEL.VELOCITYU")    
            # values=comm.allreduce(values, MPI.SUM)    
        
            
            
        # if _%1000==0:
            # study.concatenation_step()
            # print(study.get_array("MODEL.X")[0])
            # print(_)
        # tmp = study.get_array("MODEL.IKLE")
        # study.set_array("MODEL.IKLE", tmp)
        # tmp2 = study.get_array("MODEL.IKLE")
        # diff = abs(tmp2 - tmp)
        # assert np.amax(diff) == 0
        # tmp = study.get_array("MODEL.WATERDEPTH")
        # study.set_array("MODEL.WATERDEPTH", tmp)
        # tmp2 = study.get_array("MODEL.WATERDEPTH")
        # diff = abs(tmp2 - tmp)
        # assert np.amax(diff) < 1e-8
    # Ending the run
    if comm.rank==0:
      dynoupdatevalue(id=item['id'],progress=1,TableName=TableCas)
    study.finalize()
    del study
    return None
