# import pytest
import os

from boto3.dynamodb.conditions import Key, Attr
from meracanapi.dynamodb import create,delete,get,listall,update,query,dump,scan

def test_cas():
  """ Testing DynamoDBTableCas
  """
  table={"TableName":"TestTableCas"}
  items=listall(**table)
  for item in items:
    delete(**{**item,**table})
  create(name="TestName1",projectId="id1",keywords={"a":"value","b":"value"},**table)
  create(name="TestName2",projectId="id2",**table)
  items=listall(**table)
  assert len(items)==2
  
  qitems=query(IndexName='projectIndex',KeyConditionExpression=Key('projectId').eq("id1"),**table)
  assert len(qitems)==1
  
  id=qitems[0]['id']
  assert qitems[0]['name']=="TestName1"
  
  item=get(id=id,**table)
  assert item['name']=="TestName1"
  
  item=update(id=id,name="TestName1a",keywords={"c":"value"},**table)
  assert item['name']=="TestName1a"
  assert item['keywords']=={"a":"value","b":"value","c":"value"}
  
  item=update(id=id,keywords={"c":None},**table)
  
  assert item['keywords']=={"a":"value","b":"value"}
  
  item=get(id=id,**table)
  assert item['name']=="TestName1a"
  
  
  qitems=query( 
  IndexName='projectIndex',
  KeyConditionExpression=Key('projectId').eq("id1"),
  FilterExpression=Attr('keywords.a').eq('value'),
  **table
  )
  assert len(qitems)==1
  
  sitems=scan(FilterExpression=Attr('projectId').eq('id1'),**table)
  assert len(sitems)==1
  
  sitems=scan(FilterExpression=Attr('keywords.b').eq('value'),**table)
  assert len(sitems)==1
  
  for item in items:
    delete(**{**table,**item})
  
  item=listall(**table)
  assert len(item)==0

def test_temp():
  """ Temporary testing. Delete when done.
  """
  table={"TableName":"TestTableCas"}
  # create({**table,"name":"TestName1","projectId":"id1","keywords":{"a":"value","b":"value"}})
  items=listall({**table})
  id=items[0]['id']
  item=update({**table,"id":id,"keywords":{"d":"value1","e":"value"}})
  item=get({**table,"id":id})
  print(item)
  
  
  

if __name__ == "__main__":
  test_cas()
  # test_temp()

  