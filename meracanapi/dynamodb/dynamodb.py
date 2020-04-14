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
  def wrapper(kwargs):
    kwargs={**kwargs}
    kwargs['timestamp'] = int(time.time()*1000)
    table = kwargs.pop('TableName')
    kwargs['table'] = dynamodb.Table(table)
    
    return function(kwargs)
  return wrapper

@check
def create(kwargs):
    table=kwargs.pop("table")
    timestamp=kwargs.pop("timestamp")
    item = {
      **kwargs,
      'id': str(uuid.uuid4()),
      'createdAt': timestamp,
      'updatedAt': timestamp,
    }
    table.put_item(Item=item)
    return item

@check
def delete(kwargs):
    table=kwargs.pop("table")
    id=kwargs.pop("id")
    table.delete_item(Key={'id': id})
    return True

@check
def get(kwargs):
    table=kwargs.pop("table")
    id=kwargs.pop("id")
    response = table.get_item(Key={'id': id})
    return response.get("Item",{})
    
@check
def listall(kwargs):
    table=kwargs.pop("table")
    response = table.scan()
    return response.get("Items",[])
    
@check
def update(kwargs):
    table=kwargs.pop("table")
    id=kwargs.pop("id")
    timestamp=kwargs.pop("timestamp")
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
def query(kwargs):
    table=kwargs.pop("table")
    timestamp=kwargs.pop("timestamp")
    response = table.query(**kwargs)
    return response.get("Items",[])

@check
def scan(kwargs):
    table=kwargs.pop("table")
    timestamp=kwargs.pop("timestamp")
    response = table.scan(**kwargs)
    return response.get("Items",[])

def dump(obj):
  return json.dumps(obj, cls=decimalencoder.DecimalEncoder)