import os
import uuid
import boto3
from ..dynamodb import DynamoDB

class S3DynamoDB(DynamoDB):
  """
  S3-DynamoDB object
  
  Parameters
  ----------
  BucketName:str
  TableName:str
  """
  def __init__(self,**kwargs):
    super().__init__(**kwargs)
    self.BucketName = BucketName = kwargs.pop('BucketName',os.environ.get('AWS_BUCKETNAME',None))
    if BucketName is None:raise Exception("BucketName is not set")
    s3 = boto3.resource('s3')
    self.bucket = s3.Bucket(BucketName)

  def download(self,Filename=None,localFolder="",**kwargs):
    """ 
    Download a file from S3
    
    Parameters
    ----------
    Filename: str
      Path of new local file
    kwargs:dict
      id:str
      TableName:str
    Note
    ----
    item:object
      ObjectKey:str
        Key of the file. This is typically a uuidv4 string key.
    """
    item=self.get(**kwargs)
    if Filename is None:
      Filename=os.path.join(localFolder,"{}.{}".format(item.get('name'),item.get("type")))
    self.bucket.download_file(item['ObjectKey'], Filename)
    return Filename
  
  def delete(self,**kwargs):
    """ 
    Delete s3 file and dynamodb item
    
    Parameters
    ----------
    kwargs:dict
      id:str
    """
    item=self.get(**kwargs)
    response = self.bucket.delete_objects(Delete={'Objects': [{'Key':item['ObjectKey']}]})
    super().delete(**kwargs)
    return True
  
  def upload(self,Filename,Prefix="",projectId="general",**kwargs):
    """ 
    Upload file to S3 and add item in dynamodb
    
    Parameters
    ----------
    Filename: str
      Path of local file
    Prefix:str,optional
      S3 folder
    projectId:str
      Meta data
    kwargs:dict
      id:str
        To update file and item
    """
    
    if not kwargs.get("id"):
      """ New s3 file and dynamodb item
      """
      Key=os.path.join(Prefix, str(uuid.uuid4()))
      self.bucket.upload_file(Filename=Filename,Key=Key)
      name = os.path.splitext(os.path.basename(Filename))[0]
      type = Filename.split(os.extsep).pop()
      item=self.insert(name=name,projectId=projectId,type=type,ObjectKey=Key,**kwargs)
    else:
      """ Update s3 file and dynamodb item
      """
      item=self.get(**kwargs)
      Key=item['ObjectKey']
      self.bucket.upload_file(Filename=Filename,Key=Key)
      item=self.update(**kwargs)
    
    return item
  
  def s3list(self,Prefix="",**kwargs):
    """
    Get list of s3 files.
    This is not very informative since the meta data is stored in the DynamoDB
    
    Parameters
    ----------
    Prefix:str,optional
      S3 folder  
    """
    s3 = boto3.client('s3')
    page_iterator = s3.get_paginator('list_objects_v2').paginate(Bucket=self.BucketName, Prefix=Prefix)
    files=[]
    for page in page_iterator:
      if "Contents" in page:
        files=files+page["Contents"]
    return files