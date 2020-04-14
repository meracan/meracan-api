# Testing Api

## DynamoDB


```bash
aws cloudformation deploy --stack-name TestDynamoDBTableCAS --template-file aws-cloudformation/dynamodb/tableCas.yaml --parameter-overrides TableName=TestTableCas
```