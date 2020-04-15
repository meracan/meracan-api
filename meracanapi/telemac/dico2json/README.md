# Telemac dico to JSON
Copy Telemac dictionaries to JSON files. The JSON files are used in `api-telemac` to validate steering files (.cas).

## Installation
Telemac needs to be installed.

- Copy `dico2json.py` to `telemac/vxpxrx/scripts/python3`.
- Set working directory to `cd telemac/vxpxrx/scripts/python3`
- Run python script `python3 dico2json.py`

This will create 4 json files: `telemac2d.dico.json`, `telemac3d.dico.json`,`tomawac.dico.json` and `sisyphe.dico.json`