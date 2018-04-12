# ############################################################
# IMPORT TOOLS
# ############################################################
from tquakes import *
from matplotlib import use
use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap as map,shiftgrid
import matplotlib.patches as patches
from scipy.optimize import leastsq
import spiceypy as sp
sp.furnsh("util/kernels/kernels.mk")
confile=prepareScript()
conf=execfile(confile)

# ############################################################
# CONNECT TO DATABASE
# ############################################################
connection=connectDatabase()
db=connection.cursor()

# ############################################################
# PREPARE PLOTTING REGION
# ############################################################
fig,axs=subPlots(plt,[1])
ax=axs[0]

# ############################################################
# COMPONENT AND PHASE INFORMATION
# ############################################################
info=COMPONENTS_DICT[component]
compnum=info[0]
compname=info[1]

info=PHASES_DICT[phase]
phasenum=info[0]
phasename=info[1]

# ############################################################
# GET PHASES
# ############################################################
latb=center[0]-dlat/2;latu=center[0]+dlat/2
lonl=center[1]-dlon/2;lonr=center[1]+dlon/2
jd1=date2jd(datetime.datetime.strptime(dateini,"%Y-%m-%d %H:%M:%S"))
jd2=date2jd(datetime.datetime.strptime(dateend,"%Y-%m-%d %H:%M:%S"))

search="""where qphases<>'' and 
qdeptherr/1<qdepth/1 and
Ml+0>=%.2f AND Ml+0<%.2f and 
qdepth+0>=%.2f and qdepth+0<%.2f and 
qdeptherr/1<qdepth/1 and
qlat+0>=%.2f and qlat+0<%.2f and 
qlon+0>=%.2f and qlon+0<%.2f and
qjd+0>=%.5f and qjd+0<=%.5f and
(cluster1='0' or cluster1 like '-%%') and
astatus+0=4 
limit %d"""%(Mlmin,Mlmax,
             depthmin,depthmax,
             latb,latu,
             lonl,lonr,
             jd1,jd2,
             limit)

#READ FULL MOONS
full=numpy.loadtxt("util/astronomy-fullmoons-1970_2030.data")

qids,phases=getPhases(search,component,db,dbtable=dbtable)
phs=phases[:,4+phasenum]
nquakes=len(phs)

results=mysqlArray("select quakeid,qet,aphases,qphases,qsignal from %s %s"%(dbtable,search),db)

aphs=[]
qphs=[]
qsigs=[]
for i,result in enumerate(results):
    qid=result[0]
    aphases=result[2]
    qphases=result[3]
    qsignal=result[4]

    #Read time-series
    conf=loadConf("/home/tquakes/tQuakes/%s.conf"%quakeid)

    exit(0)


    if qsignal=='':continue
    #Get tidal phases

    #Get astronomical phases
    fases=aphases.split(";")[0].split(":")
    signal=float(qsignal.split(";")[2])
    aph=float(fases[0])

    qphs+=[phs[i]]
    aphs+=[aph]
    qsigs+=[signal]
    
print("%d events selected"%len(qphs))
aphs=numpy.array(aphs)
qphs=numpy.array(qphs)
dmax=aphs.max()
qsigs=numpy.array(qsigs)

#cond=(aphs>15.0)&((360*phs)<90)
#aphs[cond]-=dmax
#cond=(aphs<7.0)&((360*phs)>270)
#aphs[cond]+=dmax

# ############################################################
# HISTOGRAM
# ############################################################
ax.plot(360*qphs,qsigs,'ko',ms=2)
"""
nbins=10
cond=(qphs>0.4)*(qphs<0.6)
ax.hist(qsigs[cond],nbins,color='b',alpha=0.5,normed=True)
nbins=10
cond=(qphs<0.2)|(qphs>0.8)
ax.hist(qsigs[cond],nbins,color='r',alpha=0.5,normed=True)
"""

# ############################################################
# DECORATION
# ############################################################
ax.set_xlabel("Tidal monthly phase",fontsize=14)
ax.set_ylabel("Vertical displacement (mm)",fontsize=14)
ax.set_title(dbtitle,position=(0.5,1.05),fontsize=18)

#ax.set_xlim((0.4,0.6))
#ax.set_xlim((0,0.2))
#ax.set_xlim((0,360))
#ax.set_ylim((0,aphs.max()))

# ############################################################
# SAVING FIGURE
# ############################################################
saveFigure(confile,fig)

