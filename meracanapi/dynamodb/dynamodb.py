import json
import logging
import os
import time
import uuid
from . import decimalencoder
import boto3
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb')

def clean_empty(d):
  """ Remove keys with None or empty list throughout dictionary
  """
  if not isinstance(d, (dict, list)):
    return d
  if isinstance(d, list):
    return [v for v in (clean_empty(v) for v in d) if v]
  return {k: v for k, v in ((k, clean_empty(v)) for k, v in d.items()) if v}


def check(function):
  """
  Decorator for static methods to check input
  """
  def wrapper(**kwargs):
    TableName = kwargs.pop('TableName',os.environ.get('AWS_TABLENAME',None))
    if TableName is None:raise Exception("TableName is not set")
    table = dynamodb.Table(TableName)
    return function(table,**kwargs)
  return wrapper

@check
def create(table,**kwargs):
    timestamp = int(time.time()*1000)
    item = {
      **kwargs,
      'id': str(uuid.uuid4()),
      'createdAt': timestamp,
      'updatedAt': timestamp,
    }
    table.put_item(Item=item)
    return item

@check
def delete(table,**kwargs):
    id=kwargs.pop("id")
    table.delete_item(Key={'id': id})
    return True

@check
def get(table,**kwargs):
    id=kwargs.pop("id")
    response = table.get_item(Key={'id': id})
    return response.get("Item",{})
    
@check
def listall(table,**kwargs):
    response = table.scan()
    return response.get("Items",[])
    
@check
def update(table,**kwargs):
    id=kwargs.pop("id")
    response=table.get_item(Key={'id': id})
    item=response.get("Item",{})
    
    new={}
    exp=["#updatedAt=:updatedAt"]
    ExpressionAttributeNames={"#updatedAt":"updatedAt"}
    for key in kwargs:
      ExpressionAttributeNames['#'+key]=key
      if isinstance(kwargs[key],dict) and key in item and isinstance(item[key],dict):
        """ Update object. It replaces the entire object and not child itmes
        """
        kwargs[key]=clean_empty({**item[key],**kwargs[key]})
        
      new[":"+key]=kwargs[key]
      exp.append("#{0}=:{0}".format(key))
    exp=",".join(exp)
    
    timestamp = int(time.time()*1000)
    ExpressionAttributeValues={':updatedAt': timestamp,**new}
    
    response = table.update_item(
        Key={'id': id},
        ExpressionAttributeNames=ExpressionAttributeNames,
        ExpressionAttributeValues=ExpressionAttributeValues,
        UpdateExpression='SET {}'.format(exp),
        ReturnValues='ALL_NEW',
    )
    return response['Attributes']

@check
def query(table,**kwargs):
    response = table.query(**kwargs)
    return response.get("Items",[])

@check
def scan(table,**kwargs):
    response = table.scan(**kwargs)
    return response.get("Items",[])

def dump(obj):
  return json.dumps(obj, cls=decimalencoder.DecimalEncoder)