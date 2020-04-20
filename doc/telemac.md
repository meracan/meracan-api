# Telemac Installation
```bash
mkdir ./telemac/v8p1r0
svn co http://svn.opentelemac.org/svn/opentelemac/tags/v8p1r0 ./telemac/v8p1r0 --username=ot-svn-public --password=telemac1*
svn co http://svn.opentelemac.org/svn/opentelemac/tags/v8p1r0/optionals/metis-5.1.0 ./telemac/metis --username=ot-svn-public --password=telemac1*

conda activate meracan

conda install -c anaconda svn
conda install -c conda-forge libgfortran
conda install -c conda-forge openmpi openmpi-mpifort
conda install -c conda-forge make cmake

cd ./telemac/metis
cmake -D .
make && make install

cd $CONDA_PREFIX
vi ./etc/conda/activate.d/env_vars.sh
export METISHOME="/home/ec2-user/environment/telemac/metis"
export SYSTELCFG="/home/ec2-user/environment/telemac/systel.cfg"
export PATH="/home/ec2-user/environment/telemac/v8p1r0/scripts/python3:$PATH"
export HOMETEL="/home/ec2-user/environment/telemac/v8p1r0"
export USETELCFG=gfortranp
export LD_LIBRARY_PATH=$HOMETEL/builds/$USETELCFG/wrap_api/lib
export PYTHONPATH=$HOMETEL/scripts/python3:$PYTHONPATH
export PYTHONPATH=$HOMETEL/builds/$USETELCFG/wrap_api/lib:$PYTHONPATH

vi ./etc/conda/deactivate.d/env_vars.sh
unset SYSTELCFG
unset HOMETEL
unset USETELCFG
unset LD_LIBRARY_PATH
unset PYTHONPATH

COPY ./systel.cfg $SYSTELCFG

conda deactivate
conda activate telemac

compile_telemac.py
```


