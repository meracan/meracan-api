# MERACAN-API - Testing
Testing MERACAN-API requires setting up AWS services.

## Installation
- Install pytest `conda install pytest`
- Install [aws cli](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html).
- Install AWS services as shown below
- If testing `apitelemac`, see [docs](../doc/telemac.md)

#### Set Environment variables
```bash
conda activate meracan
cd $CONDA_PREFIX
vi ./etc/conda/activate.d/env_vars.sh
# Copy below to file
export AWS_BUCKETNAME="mercantest"
export AWS_TABLECAS="TestTableCas"
export AWS_TABLEDATA="TestTableData"


vi ./etc/conda/deactivate.d/env_vars.sh
# Copy below to file
unset AWS_TABLECAS
unset AWS_TABLEDATA
unset AWS_BUCKETNAME

conda deactivate
conda activate meracan

```
#### Create Bucket
```bash
aws s3api create-bucket --bucket $AWS_BUCKETNAME --region us-east-1
```

#### Create TableCas
```bash 
aws dynamodb create-table \
    --table-name $AWS_TABLECAS \
    --billing-mode "PAY_PER_REQUEST" \
    --attribute-definitions AttributeName="id",AttributeType="S" AttributeName="projectId",AttributeType="S" \
    --key-schema AttributeName="id",KeyType="HASH" \
    --global-secondary-indexes IndexName=projectIndex,KeySchema=["{AttributeName=projectId,KeyType=HASH}"],Projection="{ProjectionType=ALL}"
```

#### Create TableData
```bash 
aws dynamodb create-table \
    --table-name $AWS_TABLEDATA \
    --billing-mode PAY_PER_REQUEST \
    --attribute-definitions AttributeName=id,AttributeType=S AttributeName=projectId,AttributeType=S AttributeName="type",AttributeType=S \
    --key-schema AttributeName=id,KeyType=HASH \
    --global-secondary-indexes IndexName=projectIndex,KeySchema=["{AttributeName=projectId,KeyType=HASH}"],Projection="{ProjectionType=ALL}" IndexName=typeIndex,KeySchema=["{AttributeName=type,KeyType=HASH}"],Projection="{ProjectionType=ALL}"
```

## Pytest
Testing is done using pytest.
```bash
pytest
```

## Testing during development
```
python3 test/test_dynomodb.py
python3 test/test_s3dynomodb.py
python3 test/test_apitelemac.py
```

## Delete AWS services
```bash
aws s3api delete-bucket --bucket $AWS_BUCKETNAME --region us-east-1
aws dynamodb delete-table --table-name $AWS_TABLEDATA
aws dynamodb delete-table --table-name $AWS_TABLECAS
```