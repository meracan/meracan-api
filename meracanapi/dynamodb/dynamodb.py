import json
import os
import time
import uuid
import decimal
import boto3
from functools import wraps
from boto3.dynamodb.conditions import Key, Attr,ConditionBase
import operator

ops = { 
  r"&": operator.and_,
  r"|": operator.or_,
  "!": operator.invert,
  "+": operator.add, 
  "-": operator.sub,
}

class DecimalEncoder(json.JSONEncoder):
  """ DecimalEncoder to transform DynamoDB object to Python Object
  """
  def default(self, obj):
    if isinstance(obj, decimal.Decimal):
      n=float(obj)
      if n.is_integer():n=int(n)
      return n
    return super(DecimalEncoder, self).default(obj)

def clean_empty(d):
  """ Remove keys with None or empty list throughout dictionary
  """
  if not isinstance(d, (dict, list)):
    return d
  if isinstance(d, list):
    return [v for v in (clean_empty(v) for v in d) if v]
  return {k: v for k, v in ((k, clean_empty(v)) for k, v in d.items()) if v}

def _formatD2P(obj):
  """ Format DynamoDB object to python object
  """
  return json.loads(json.dumps(obj,cls=DecimalEncoder))

def _formatP2D(obj):
  """ Format python object to DynamoDB object
  """
  return json.loads(json.dumps(obj), parse_float=decimal.Decimal)

def _build(fe):
  """ Build filter expression from dict
  """
  if not fe.get("con"):raise Exception("FilterExpression needs a con")
  if fe.get("value",None) is None:raise Exception("FilterExpression needs a value")
  con=fe.get("con")
  value=fe.get("value")
  if con=="between" and not isinstance(value,tuple):raise Exception("Between condition needs a tuple")
  if fe.get("Key"):return getattr(Key(fe.get("Key")),con)(value)
  if fe.get("Attr"):
    if con=="exists":return getattr(Attr(fe.get("Attr")),con)()
    return getattr(Attr(fe.get("Attr")),con)(value)
  raise Exception("FilterExpression needs Key or Attr")

def getFilterExpression(fe):
  """ Build filter expression from list,dict or ConditionBase
  """
  if isinstance(fe,ConditionBase):
    pass
  elif isinstance(fe,dict):
    fe=_build(fe)
  elif isinstance(fe,list) and len(fe)>0:
    new=_build(fe[0])
    for i in range(1,len(fe)):
      _=fe[i]
      op=ops.get(_.get('ops',"&"),None)
      if op is None:raise Exception("Operator does not exist")
      new = op(new,_build(_))
    fe=new
  else:
    raise Exception("FilterExpression needs to be ConditionBase,dict or list")
  return fe

# def check(checkId):
#   """
#   Decorator to:
#     1. check input parameters: `TableName` and `id`(if required).  
#     2. Transform attributes to DynamoDB capatible values: float to Decimal
#     2. create boto3.dynamodb.Table object
#   """
#   def decorator(func):
#     @wraps(func)
#     def wrapper(**kwargs):
#       TableName = kwargs.pop('TableName',os.environ.get('AWS_TABLENAME',None))
#       if TableName is None:raise Exception("TableName is not set")
      
#       if checkId:
#         if not "id" in kwargs:raise Exception("id needs to be set")
#         if not isinstance(kwargs['id'],str):raise Exception("id needs to be a string")
      
#       kwargs = _formatP2D(kwargs)
      
#       dynamodb = boto3.resource('dynamodb')
#       table = dynamodb.Table(TableName)
      
#       return func(table,**kwargs)
#     return wrapper
#     wrapper.__doc__=func.__doc__
#   return decorator

def check(checkId):
  """
  Decorator to:
    1. Transform attributes to DynamoDB capatible values: float to Decimal
    2. create boto3.dynamodb.Table object
  """
  def decorator(func):
    @wraps(func)
    def wrapper(self,*args,**kwargs):
      if checkId:
        if not "id" in kwargs:raise Exception("id needs to be set")
        if not isinstance(kwargs['id'],str):raise Exception("id needs to be a string")
      kwargs = _formatP2D(kwargs)
      return func(self,*args,**kwargs)
    return wrapper
  return decorator

class DynamoDB(object):
  """
  Parameters
  ----------
  TableName:str
    Name of DynamoDB Table
  """
  def __init__(self,**kwargs):
    TableName = kwargs.pop('TableName',os.environ.get('AWS_TABLENAME',None))
    if TableName is None:raise Exception("TableName is not set")
    dynamodb = boto3.resource('dynamodb')
    self.table = dynamodb.Table(TableName)
  
  @check(False)
  def insert(self,**kwargs):
    """
    Insert new item in DynamoDB.
    
    Parameters
    ----------
    kwargs:object,optional
      Item attributes
    
    Notes
    -----
    float are automatically transform to decimal.
    id,createdAt,updatedAt are automatically created.
    
    Returns
    -------
    object:The new item in DynamoDB
    """
    timestamp = int(time.time()*1000)
    item = {
      **kwargs,
      'id': kwargs.get("id",str(uuid.uuid4())),
      'createdAt': timestamp,
      'updatedAt': timestamp,
    }
    self.table.put_item(Item=item)
    return item

  @check(True)
  def delete(self,**kwargs):
    """ 
    Delete item in DynamoDB. 
    Parameters
    ----------
    TableName:str
      Name of DynamoDB Table
    id:str,required
    """
    self.table.delete_item(Key={'id': kwargs['id']})
    return True

  @check(True)
  def get(self,**kwargs):
    """ 
    Get an item in DynamoDB. 
    Parameters
    ----------
    TableName:str
      Name of DynamoDB Table
    id:str,required
    """
    response = self.table.get_item(Key={'id': kwargs['id']})
    return _formatD2P(response.get("Item",{}))
    
  @check(True)
  def update(self,**kwargs):
    """ 
    Update item in DynamoDB.
    
    Parameters
    ----------
    TableName:str
      Name of DynamoDB Table
    id:str,required
    """
    id=kwargs.pop('id')
    new={}
    exp=["#updatedAt=:updatedAt"]
    ExpressionAttributeNames={"#updatedAt":"updatedAt"}
    for key in kwargs:
      ExpressionAttributeNames['#'+key]=key
      if isinstance(kwargs[key],dict):
        """ Update object. If the attribute is object, it needs to download 
            the object from DynamoDB and updates it properties.
        """
        response = self.table.get_item(Key={'id': id})
        item=response.get("Item",{})
        if key in item and isinstance(item[key],dict):
          kwargs[key]=clean_empty({**item[key],**kwargs[key]})
        
      new[":"+key]=kwargs[key]
      exp.append("#{0}=:{0}".format(key))
    exp=",".join(exp)
    
    timestamp = int(time.time()*1000)
    ExpressionAttributeValues={':updatedAt': timestamp,**new}
    
    response = self.table.update_item(
        Key={'id': id},
        ExpressionAttributeNames=ExpressionAttributeNames,
        ExpressionAttributeValues=ExpressionAttributeValues,
        UpdateExpression='SET {}'.format(exp),
        ReturnValues='ALL_NEW',
        
    )
    return _formatD2P(response.get('Attributes',{}))

  @check(False)
  def all(self,**kwargs):
    """ 
    List all items
    
    Parameters
    ----------
    TableName:str
      Name of DynamoDB Table
    """
    response = self.table.scan()
    return _formatD2P(response.get("Items",[]))



  @check(False)
  def query(self,**kwargs):
    """ 
    Query/Scan DynamoDB
    
    Parameters
    ----------
    KeyConditionExpression:dict or list of dict
    FilterExpression:dict or list of dict
      dict:
        ops:str
        Key:str,required/optional
        Attr:str,optional/required
        con:Key operator (begins_with,between,eq,gt,gte,lt,lte)
        con:Attr operator (attribute_type,begins_with,between,contains,exists,is_in,ne,not_exists,size,eq,gt,gte,lt,lte)
        value:*
    ProjectionExpression:str,
    ExpressionAttributeNames=dict,
    IndexName:str
    
    Examples
    --------
    FilterExpression=[{"Key":"year","con":"between","value":(1950,1959)}]
    ProjectionExpression="#yr, title, info.rating"
    ExpressionAttributeNames= { "#yr": "year", }
    """
    
    if not kwargs.get("KeyConditionExpression"):raise Exception("Query needs KeyConditionExpression")
    kwargs["KeyConditionExpression"]=getFilterExpression(kwargs.get("KeyConditionExpression"))
    return self._queryscan("query",**kwargs)

  @check(False)
  def scan(self,**kwargs):
    return self._queryscan("scan",**kwargs)
  scan.__doc__=query.__doc__
  
  def _queryscan(self,action='query',**kwargs):
    """ Query and scan general functions
    """
    if kwargs.get("FilterExpression"):
      kwargs["FilterExpression"]=getFilterExpression(kwargs.get("FilterExpression"))
    
    response = getattr(self.table,action)(**kwargs)
    data=response.get("Items",[])
    while response.get('LastEvaluatedKey', False):
      response = getattr(self.table,action)(**kwargs,ExclusiveStartKey=response['LastEvaluatedKey'])
      data.extend(response['Items'])
    return _formatD2P(data)