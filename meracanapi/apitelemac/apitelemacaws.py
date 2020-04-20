import os
import shutil
import uuid
from functools import wraps

from ..dynamodb import DynamoDB
from ..s3dynamodb import S3DynamoDB
from .telemac.telemac_cas import TelemacCas

def check(func):
  @wraps(func)
  def wrapper(self,**kwargs):
    if not "id" in kwargs:raise Exception("id needs to be set")
    if not isinstance(kwargs['id'],str):raise Exception("id needs to be a string")
    return func(self,**kwargs)
  return wrapper


class ApiTelemacAWS(object):
  """
  Class to download/upload telemac files to aws
  
  Parameters
  ----------
  TableCas:str,optional
  TableData:str,optional
  BucketName:str,optional
  projectId:str,optional
  localFolder:str,optional
  
  Examples
  --------
  
  
  """
  def __init__(self,**kwargs):
    self.TableCas =TableCas= kwargs.pop('TableCas',os.environ.get('AWS_TABLECAS',None))
    self.TableData=TableData = kwargs.pop('TableData',os.environ.get('AWS_TABLEDATA',None))
    self.BucketName=BucketName=kwargs.pop('BucketName',os.environ.get('AWS_BUCKETNAME',None))
    self.projectId = kwargs.pop('projectId',"general")
    self.localFolder=kwargs.pop('localFolder',os.environ.get('TELEMAC_LOCALFOLDER',""))
    
    if TableCas is None:raise Exception("Needs TableCas")
    if TableData is None:raise Exception("Needs TableData")
    if BucketName is None:raise Exception("Needs BucketName")
    
    self.cas = DynamoDB(TableName=TableCas)
    self.data = S3DynamoDB(TableName=TableData,BucketName=BucketName)
    
    
  def insert(self,keywords,name="default",module="telemac2d",**kwargs):
    """
    Insert cas keywords to DynamoDB
    
    Parameters
    ----------
    keywords:dict
      Telemac keywords and values
    """
    if not isinstance(keywords,dict):raise Exception("Needs a dict")
    study=TelemacCas(module)
    study.setValues(keywords)
    item=self.cas.insert(projectId=self.projectId,name=name,keywords=study.values,module=module)
    return item
  
  
  @check  
  def update(self,keywords=None,**kwargs):
    """
    Update as keywords to DynamoDB
    
    Parameters
    ----------
    keywords:dict
      Telemac keywords and values
    kwargs:dict
      id:str
        DynamoDB Id
    """
    if keywords is None:raise Exception("Needs keywords")
    item=self.cas.get(id=kwargs["id"])
    if not item:raise Exception("Item does not exist")
    study=TelemacCas(item['module'])
    study.setValues(keywords)
    
    item=self.cas.update(keywords=study.values,**kwargs)
    return item
  
  def updateProgress(self,id,iframe,nframe):
    """ Update cas with iframe and nframe
    """
    item=self.cas.update(id=id,iframe=iframe,nframe=nframe)
    return item
  
  def _uploadFiles(self,study):
    """ Process to upload files(from cas) to S3
    """
    def fupload(file):
      f=self.data.upload(file,projectId=self.projectId)
      return f['id']
    
    for key in study.in_files:
      if key=="FORTRAN FILE":
        study.values[key]=[fupload(file) for file in study.values[key]]
      else:
        study.values[key]=fupload(study.values[key])
    return study
  
  def upload(self,Filename=None,name=None,module="telemac2d",**kwargs):
    """
    Upload cas keywords to DynamoDB and files(as indicated in cas) to S3.
    
    Parameters
    ----------
    Filename:str
      Path to cas file
    name:str, optional
      If not specified, the name is based on the file name
    module:str
      telemac2d,telemac3d,tomawac,sisyphe
    """
    if Filename is None:raise Exception("Needs casFile")
    study=TelemacCas(module,Filename)
    newid=str(uuid.uuid4())
    study=self._uploadFiles(study,newid)
    if name is None:
      name=os.path.splitext(os.path.basename(Filename))[0]  
    item=self.cas.insert(id=newid,projectId=self.projectId,name=name,keywords=study.values,module=module)
    
    return item
  
  @check
  def uploadFile(self,keyword=None,**kwargs):
    """
    Upload file and in cas dynamodb
    
    Parameters
    ----------

    keyword:str
      Telemac keyword
    kwargs:dict
      Filename:str
      id:str
        Cas Id
    """
    if keyword is None:raise Exception("Needs keyword")
    casId=kwargs.pop('id')
    f=self.data.upload(projectId=self.projectId,**kwargs)
    item=self.update(id=casId,keywords={keyword:f['id']})
    return f
  uploadFile.__doc__=S3DynamoDB.upload.__doc__

  def removeFile(self,**kwargs):
    return self.data.delete(**kwargs)
  removeFile.__doc__=S3DynamoDB.delete.__doc__
  
  @check
  def _downloadFile(self,**kwargs):
    """ 
    Download file from s3 to localFolder using name and type of file
    
    Parameters
    ----------
    id:str
      DynamoDB Id in TableData
    """
    item=self.data.get(id=kwargs['id'])
    if not item:raise Exception("File does not exist - {}".format(kwargs['id']))
    
    fileName = "{}.{}".format(item['name'],item['type'])
    filePath=os.path.join(kwargs.get("localFolder",self.localFolder),fileName)
    self.data.download(filePath,**item)
    return "{}".format(fileName)
  
  @check
  def download(self,**kwargs):
    """ 
    Download cas and files to localFolder using name and type of files
    Fortran files are copied in 'user_fortran' folder
    
    Parameters
    ----------
    kwargs:dict
      id:str
        DynamoDB Id in TableCas
      localFolder:str
    Returns
    -------
    casPath,DynamoDB item
    """
    localFolder=kwargs.get('localFolder',self.localFolder)
    
    item=self.cas.get(id=kwargs['id'])
    if not item:raise Exception("Cas does not exist - {}".format(kwargs['id']))
    study=TelemacCas(item['module'])
    study.setValues(item['keywords'])  
    
    for key in study.in_files:
      value=study.values[key]
      if isinstance(value,list):
        # FORTRAN FILE
        fortran_path=os.path.join(localFolder,"user_fortran")
        if os.path.exists(fortran_path):
          shutil.rmtree(fortran_path)
        os.mkdir(fortran_path)
        study.values[key]=[self._downloadFile(id=_value,localFolder=fortran_path) for _value in value]
      else:  
        study.values[key]=self._downloadFile(id=value)
    
    casPath ="{}.cas".format(item['name'])
    casPath = os.path.join(localFolder,casPath)
    study.write(casPath)
    return casPath,item
  
  @check
  def addFortran(self,**kwargs):
    """ 
    Add fortran to cas
    
    Parameters
    ----------
    kwargs:dict
      Filename:str
      id:str,
        CasId
    """
    item=self.cas.get(id=kwargs['id'])
    if not item:raise Exception("Item does not exist")
    casId=kwargs.pop('id')
    f=self.data.upload(projectId=self.projectId,**kwargs)
    farray=item['keywords'].get("FORTRAN FILE",[])
    farray.append(f['id'])
    item=self.update(id=casId,keywords={"FORTRAN FILE":farray})
    return f
  
  @check
  def rmFortran(self,fortranId,**kwargs):
    """ 
    Remove fortran from cas
    
    Parameters
    ----------
    fortranId:str,
      File Id
    kwargs:dict
      id:str,
        CasId
    """
    casId=kwargs.pop('id')
    item=self.cas.get(id=casId)
    if not item:raise Exception("Item does not exist")
    
    farray=item['keywords'].get("FORTRAN FILE",[])
    farray.remove(fortranId)
    item=self.update(id=item['id'],keywords={"FORTRAN FILE":farray})
    self.removeFile(id=fortranId)