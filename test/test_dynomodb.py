import pytest
from meracanapi import DynamoDB

def test_dynomodb():
  """ Testing dynamodb
  
  """
  dyno=DynamoDB(TableName="TestTableCas")
  
  items=dyno.all()
  for item in items:
    dyno.delete(**item)
  
  dyno.insert(name="TestName1",projectId="id1",keywords={"a":"value","b":"value"})
  dyno.insert(name="TestName2",projectId="id2")
  dyno.insert(name="TestName1",projectId="id2")
  dyno.insert(name="TestName2",projectId="id1",num=0.1)
  dyno.insert(name="TestName1",projectId="id1",other="a")
  items=dyno.all()
  assert len(items)==5
  
  # -----
  # Query
  # -----
  item=items[0]
  with pytest.raises(Exception, match=r"KeyConditionExpression only supports Attribute objects of type Key"):
    dyno.query(KeyConditionExpression={'Attr':'id','con':'eq','value':item['id']})
  with pytest.raises(Exception, match=r"FilterExpression needs a con"):
    dyno.query(KeyConditionExpression={'Key':'id','x':'eq','value':item['id']})  
  with pytest.raises(Exception, match=r"FilterExpression needs a value"):
    dyno.query(KeyConditionExpression={'Key':'id','con':'eq','v':item['id']})
  with pytest.raises(Exception, match=r".*'Key' object has no attribute 'e'.*"):
    dyno.query(KeyConditionExpression={'Key':'id','con':'e','value':item['id']})
  with pytest.raises(Exception, match=r"Query key condition not supported"):
    dyno.query(KeyConditionExpression={'Key':'id','con':'gt','value':item['id']})    
  with pytest.raises(Exception, match=r"Query condition missed key schema element: id"):
    dyno.query(KeyConditionExpression={'Key':'a','con':'eq','value':item['id']})
  with pytest.raises(Exception, match=r"Condition parameter type does not match schema type"):
    dyno.query(KeyConditionExpression={'Key':'id','con':'eq','value':1})
    
  qitem=dyno.query(KeyConditionExpression={'Key':'id','con':'eq','value':item['id']})[0]
  assert qitem==item
  
  qitems=dyno.query(IndexName='projectIndex',KeyConditionExpression={'Key':'projectId','con':'eq','value':"id1"})
  assert len(qitems)==3
  
  qitems=dyno.query(IndexName='projectIndex',
    KeyConditionExpression={'Key':'projectId','con':'eq','value':"id1"},
    FilterExpression={'Key':'id','con':'eq','value':qitems[0]['id']}
    )
  assert len(qitems)==1
  
  qitems=dyno.query(IndexName='projectIndex',
    KeyConditionExpression={'Key':'projectId','con':'eq','value':"id1"},
    FilterExpression={'Attr':'id','con':'eq','value':qitems[0]['id']}
    )
  assert len(qitems)==1

  qitems=dyno.query(IndexName='projectIndex',
    KeyConditionExpression={'Key':'projectId','con':'eq','value':"id1"},
    FilterExpression={'Attr':'other','con':'eq','value':"a"}
    )
  assert len(qitems)==1
  
  qitems=dyno.query(IndexName='projectIndex',
    KeyConditionExpression={'Key':'projectId','con':'eq','value':"id1"},
    FilterExpression={'Attr':'other','con':'eq','value':"b"}
    )
  assert len(qitems)==0
  
  qitems=dyno.query(IndexName='projectIndex',
    KeyConditionExpression={'Key':'projectId','con':'eq','value':"id1"},
    FilterExpression={'Attr':'unknown','con':'eq','value':0}
    )
  assert len(qitems)==0
  qitems=dyno.query(IndexName='projectIndex',
    KeyConditionExpression={'Key':'projectId','con':'eq','value':"id1"},
    FilterExpression=[{'Attr':'name','con':'eq','value':"TestName1"},{'Attr':'other','con':'eq','value':"a"}]
    )
  assert len(qitems)==1
  qitems=dyno.query(IndexName='projectIndex',
    KeyConditionExpression={'Key':'projectId','con':'eq','value':"id1"},
    FilterExpression=[{'Attr':'name','con':'eq','value':"TestName2"},{'ops':"|",'Attr':'other','con':'eq','value':"a"}]
    )
  assert len(qitems)==2
  with pytest.raises(Exception, match=r"Operator does not exist"):
    dyno.query(IndexName='projectIndex',
      KeyConditionExpression={'Key':'projectId','con':'eq','value':"id1"},
      FilterExpression=[{'Attr':'name','con':'eq','value':"TestName2"},{'ops':"v",'Attr':'other','con':'eq','value':"a"}]
      )
  
  # -----
  # Scan
  # -----  
  qitems=dyno.scan(
    FilterExpression=[{'Attr':'name','con':'eq','value':"TestName2"},{'ops':"|",'Attr':'other','con':'eq','value':"a"}]
    )
  assert len(qitems)==3
  qitems=dyno.scan(
    FilterExpression=[{'Attr':'name','con':'eq','value':"TestName1"},{'ops':"&",'Attr':'keywords','con':'exists','value':"a"}],
    ProjectionExpression="id, keywords",
    
    )
  assert len(qitems)==1
  assert qitems[0]['keywords']=={"a":"value","b":"value"}
  
  
  # ------
  # Update
  # ------    

  item=dyno.update(id=qitems[0]['id'],name="TestName1a",keywords={"c":"value"})
  assert item['name']=="TestName1a"
  assert item['keywords']=={"a":"value","b":"value","c":"value"}
  
  item=dyno.get(id=qitems[0]['id'])
  assert item['keywords']=={"a":"value","b":"value","c":"value"}
  
  item=dyno.update(id=qitems[0]['id'],keywords={"c":None})
  assert item['keywords']=={"a":"value","b":"value"}
  
  item=dyno.get(id=qitems[0]['id'])
  assert item['keywords']=={"a":"value","b":"value"}
  

if __name__ == "__main__":
  test_dynomodb()