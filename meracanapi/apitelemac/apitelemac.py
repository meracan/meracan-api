import os
from telapy.api.t2d import Telemac2d
from telapy.api.t3d import Telemac3d
from telapy.api.wac import Tomawac
from telapy.api.sis import Sisyphe
from mpi4py import MPI
import numpy as np

from .apitelemacaws import ApiTelemacAWS

modules = {
  "telemac2d":Telemac2d,
  "telemac3d":Telemac3d,
  "tomawac":Tomawac,
  "sisyphe":Sisyphe
}
VARNAMES={
  "U":"VELOCITYU",
  "V":"VELOCITYV",
  "H":"WATERDEPTH",
  "S":"FREESURFACE",
  "B":"BOTTOMELEVATION",
}


class ApiTelemac(ApiTelemacAWS):
  def __ini__(self,**kwargs):
    super().__init__(**kwargs)
  
  def run(self,id,uploadNCA=False):
    """
    Run telemac using cas and files from DynamoDB and S3.
    
    
    Parameters
    ----------
    id:str
      DynamoDB Id
    uploadNCA:bool,False
      Upload results on the fly as NCA to S3
    """
    casFile,item=self.download(id=id)
    
    
    os.chdir(os.path.dirname(casFile))
    basename=os.path.basename(casFile)
    comm = MPI.COMM_WORLD
    
    study=modules[item['module']](basename, user_fortran='user_fortran',comm=comm, stdout=0)
    study.set_case()
    study.init_state_default()
    
    ntimesteps = study.get("MODEL.NTIMESTEPS")
    
    ilprintout = study.cas.values.get("LISTING PRINTOUT PERIOD",study.cas.dico.data["LISTING PRINTOUT PERIOD"])
    igprintout = study.cas.values.get("GRAPHIC PRINTOUT PERIOD",study.cas.dico.data["GRAPHIC PRINTOUT PERIOD"])
    vars = study.cas.values.get("VARIABLES FOR GRAPHIC PRINTOUTS",study.cas.dico.data["VARIABLES FOR GRAPHIC PRINTOUTS"])
    print(vars)
    # nvariables = study.get("MODEL.nvariables")
    def getFrame(istep):
      return int(np.floor(float(istep)/igprintout))
    nframestep= getFrame(ntimesteps)
    
    if study.ncsize>1:
      """ Get npoin and index
      """
      data = np.zeros(study.ncsize,dtype=np.int)
      data[comm.rank]=np.max(study.get_array("MODEL.KNOLG"))
      npoin=np.max(comm.allreduce(data, MPI.SUM))
      index=study.get_array("MODEL.KNOLG").astype(np.int)-1
    else:
      npoin=study.get("MODEL.NPOIN")
      index= np.arange(npoin,dtype=np.int)
    
    for _ in range(ntimesteps):
      study.run_one_time_step()
      if _%ilprintout==0 and comm.rank==0:
        """ Print to console
        """
        print(_)
        
      if _%igprintout==0 and comm.rank==0:
        """ Print to AWS
        """
        self.updateProgress(id=id,iframe=getFrame(_),nframe=nframestep)
      
      if _%igprintout==0 and uploadNCA:
        """ Save frame to AWS
        """
        for var in vars:
          values = np.zeros(npoin)
          name=VARNAMES[var]
          if name=="FREESURFACE":
            
          
          values[index]=study.get_array("MODEL.{}".format(var))    
          values=comm.allreduce(values, MPI.SUM)
          if comm.rank==0:
            None
            # nca["h","s",getFrame(_)]=values
          
        
    if comm.rank==0:
      self.updateProgress(id=id,iframe=nframestep,nframe=nframestep)
    
    # TODO check nframe, save last frame?????
    
    study.finalize()
    del study
    return None
ApiTelemac.__doc__=ApiTelemacAWS.__doc__