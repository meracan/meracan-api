

## Installation
This package was developed,tested and built using conda.
Me uses shapely,numpy,scipy,fiona and matplotlib.
Only tested with python >=3.6
```bash
conda create -n meracan python=3.8
conda activate meracan
conda install -c conda-forge boto3

pip install -e ./meracan-api
```

## Environment Variables

**dynamodb**
- AWS_TABLENAME

**s3dynamodb**
- AWS_BUCKETNAME
- AWS_TABLENAME

**Telemac**
- TELEMAC_LOCALFOLDER
- AWS_TABLECAS
- AWS_TABLEDATA
- AWS_BUCKETNAME

### APITelemac

#### cas2json
#### folder2aws
#### dico2json
