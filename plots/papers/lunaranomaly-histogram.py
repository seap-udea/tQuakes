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

#READ PHASES
qids,phases=getPhases(search,component,db)
phs=phases[:,4+phasenum]
nquakes=len(phs)
results=mysqlArray("select quakeid,qet,qdatetime,qdepth,qjd from Quakes %s"%(search),
                   db)

#COMPUTE LUNAR PROPERTIES
qnus=[]
qets=[]
MUEARTH=4.035032355022597e5 # km^3/s^2
k=0
for i,result in enumerate(results):
    qid=result[0]
    qet=float(result[1]);
    qjd=float(result[4]);
    
    els=bodyElements("MOON",MUEARTH,qet)
    xs=bodyPosition("MOON",MUEARTH,qet)
    qnu=els[8]*RAD #True anomaly

    qnus+=[qnu]
    qets+=[qet]

#RANDOM
tmin=min(qets)
tmax=max(qets)
qrs=tmin+(tmax-tmin)*numpy.random.random(len(qets))
qrnus=[]
for i in range(len(qets)):
    els=bodyElements("MOON",MUEARTH,qrs[i])
    xs=bodyPosition("MOON",MUEARTH,qrs[i])
    qnu=els[8]*RAD #True anomaly
    qrnus+=[qnu]

# ############################################################
# HISTOGRAM
# ############################################################
normed=False

nbins=int(360.0/dphase)
h,bins=numpy.histogram(qnus,nbins,normed=normed)
xs=(bins[:-1]+bins[1:])/2
dh=numpy.sqrt(h)

hmax=(h+dh).max()
hmin=(h-dh).min()
hmean=h.mean()

hr,rbins=numpy.histogram(qrnus,nbins,normed=normed)
xrs=(bins[:-1]+bins[1:])/2

ax.hist(qnus,nbins,facecolor='blue',normed=normed,alpha=0.2)
ax.errorbar(xs,h,yerr=dh,linestyle='None',color='r')
#ax.plot(xrs,hr,'r-')

# ############################################################
# DECORATION
# ############################################################
ax.set_ylabel("Frequency",fontsize=14)
ax.set_title("Lunar true anomaly",position=(0.5,1.05),fontsize=18)
color='r'

ax.set_xlim((0,360))
ax.set_ylim((0.0*hmin,1.1*hmax))

# ############################################################
# SAVING FIGURE
# ############################################################
saveFigure(confile,fig)

