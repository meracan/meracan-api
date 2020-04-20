# MERACAN-API
MERACAN-API is an python api (with boto3) to communicate Marine Energy Resource Assessment Canada packages with AWS services.
 
### APIs
MERACAN-API contains several apis:
- [dynamodb](doc/dynamodb.ipynb):This is boto3 wrapper to upload/download to DynamoDB.
- [s3dynamodb](doc/s3dynamodb.ipynb): This is a s3/dynamodb boto3 wrapper to upload files to s3 and dynamodb. Meta data (createBy, comments,etc) and queries are perfomed in DynamoDB and files are stored in S3.
- [apitelemac](doc/apitelemac.ipynb): This is a telemac wrapper to run telemac and upload/download files to/from s3/dynamodb.
- [apiosmgmsh](doc/apiosmgmsh.ipynb): This is a osmgmsh wrapper to run osmgmsh and upload/download files to/from s3/dynamodb.
- [apigis](doc/apigis.ipynb): This is a gis(mshapely) wrapper to manipulate gis data and to upload/download GIS files to/from s3/dynamodb.

### Basic installation
This package was developed,tested and built using conda.
MERACAN-API use boto3,shapely,numpy,scipy,fiona,gdal,etc.

Only tested with python >=3.6
```bash
conda create -n meracan python=3.8
conda activate meracan
conda install -c meracan meracanapi
```

```bash
# Development installation
conda create -n meracan python=3.8
conda activate meracan
conda install -c conda-forge xxxx

git clone https://github.com/meracan/meracan-api.git
pip install -e ./meracan-api
```

#### Installation for apitelemac
Extra steps are required for `apitelemac` since it needs to download/compile [OpenTelemac](http://www.opentelemac.org/).
Please refer [Telemac Installation](doc/telemac.md)


### Lambda Setup
[Docs]()

### Testing
[Docs](test/README.md)

### License
[License](LICENSE)

### Todo
- Upload telemac results to s3
- add apiosmgmsh
- add apigis
- add nca to telemac api