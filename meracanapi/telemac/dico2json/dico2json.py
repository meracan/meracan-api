import json
from execution.telemac_dico import TelemacDico
modules=['telemac2d','telemac3d','tomawac','sisyphe']
for module in modules:
  with open('{}.dico.json'.format(module), 'w') as outfile:
    dico=TelemacDico("../../sources/{0}/{0}.dico".format(module))
    json.dump(dico.data, outfile, indent=2)
