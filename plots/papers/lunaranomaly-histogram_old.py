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
fig,axs=subPlots(plt,[1,1],l=0.12,b=0.15,dh=[0.02,0.02,0.005],fach=0.7)
ax=axs[-1]

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

qids,phases=getPhases(search,component,db)
phs=phases[:,4+phasenum]
nquakes=len(phs)

results=mysqlArray("select quakeid,qet,qdatetime,qdepth,qjd from Quakes %s"%(search),
                   db)
qnus=[]
dms=[]
fphs=[]
qets=[]
MUEARTH=4.035032355022597e5 # km^3/s^2
k=0
nu0=180.0

for i,result in enumerate(results):
    qid=result[0]
    qet=float(result[1]);
    qjd=float(result[4]);

    cond=(qjd-full)>0
    qfull=full[cond][-1]
    fphase=360.0*(qjd-qfull)/29.53059;
    fphs+=[fphase]
    
    els=bodyElements("MOON",MUEARTH,qet)
    xs=bodyPosition("MOON",MUEARTH,qet)
    emlon=numpy.mod(numpy.arctan2(xs[1],xs[0])*RAD,360.0)
    dm=sp.vnorm(xs[0:3])

    xs=bodyPosition("SUN",MUEARTH,qet)
    eslon=numpy.mod(numpy.arctan2(xs[1],xs[0])*RAD,360.0)
    
    dlon=numpy.abs(eslon-emlon)
    #print(result[2],emlon,eslon,emlon-eslon,dlon)
    #if i>2:exit(0)

    qnu=els[8]*RAD #True anomaly
    #qnu=els[5]*RAD #Mean anomaly
    #qnu=dlon
    qnus+=[qnu]
    dms+=[dm]
    qets+=[qet]
    #print(qnus)
    #exit(0)

    """
    if numpy.abs(qnu-nu0)<30 and numpy.abs(phs[i]-0.9)<0.1:
        print(result[0],result[2],els[8]*RAD,phs[i],result[3])
        k+=1
    break
    """
    #if i>5:break

dms=numpy.array(dms)
dms/=dms.mean()
print("Near to %f: %d/%d (%f%%)"%(nu0,k,nquakes,(k*100.)/nquakes))

tmin=min(qets)
tmax=max(qets)
qrs=tmin+(tmax-tmin)*numpy.random.random(len(qets))
qrnus=[]
drms=[]
for i in range(len(qets)):
    els=bodyElements("MOON",MUEARTH,qrs[i])
    xs=bodyPosition("MOON",MUEARTH,qrs[i])
    emlon=numpy.mod(numpy.arctan2(xs[1],xs[0])*RAD,360.0)
    dm=sp.vnorm(xs[0:3])

    xs=bodyPosition("SUN",MUEARTH,qrs[i])
    eslon=numpy.mod(numpy.arctan2(xs[1],xs[0])*RAD,360.0)
    dlon=numpy.abs(eslon-emlon)
    
    qnu=els[8]*RAD #True anomaly
    #qnu=els[5]*RAD #Mean anomaly
    
    #qnu=dlon
    qrnus+=[qnu]
    drms+=[dm]

drms=numpy.array(drms)
drms/=drms.mean()

# ############################################################
# TRUE ANOMALY AND PHASES
# ############################################################
#axs[-2].plot(phs,qnus,'ko',ms=2)

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

ax.hist(qnus,nbins,facecolor='blue',normed=normed,alpha=0.2)
ax.hist(qrnus,nbins,facecolor='red',normed=normed,alpha=0.2)

ax.errorbar(xs,h,yerr=dh,linestyle='None',color='r')

axs[-2].hist(dms,nbins,facecolor='blue',normed=normed,alpha=0.2)
#axs[-2].hist(drms,nbins,facecolor='red',normed=normed,alpha=0.2)

# ############################################################
# FIT
# ############################################################
pars,n=leastsq(chisq,[1.0,1.0,1.0],args=(pOsc,xs*DEG,h,dh))
xls=numpy.linspace(xs.min(),xs.max(),100)
ht=pOsc(xls*DEG,pars)
ax.plot(xls,ht,'r-')

# ############################################################
# DECORATION
# ############################################################
ax.set_ylabel("Frequency",fontsize=14)
#ax.set_title("Wave %s"%(phasename),position=(0.5,1.05),fontsize=18)
ax.set_title("Lunar true anomaly",position=(0.5,1.05),fontsize=18)
color='r'

ax.set_xlim((0,360))
ax.set_ylim((0.0*hmin,1.1*hmax))

# ############################################################
# SAVING FIGURE
# ############################################################
saveFigure(confile,fig)
exit(0)
# ############################################################
# LUNAR AGE AND PHASES
# ############################################################
qnus=fphs
fig,axs=subPlots(plt,[1,1],l=0.12,b=0.15,dh=[0.02,0.02,0.005],fach=0.7)
ax=axs[-1]
axs[-2].plot(phs,qnus,'ko',ms=2)

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

ax.hist(qnus,nbins,facecolor='blue',normed=normed,alpha=0.2)
ax.errorbar(xs,h,yerr=dh,linestyle='None',color='r')

# ############################################################
# FIT
# ############################################################
pars,n=leastsq(chisq,[1.0,1.0,1.0],args=(pOsc,xs*DEG,h,dh))
xls=numpy.linspace(xs.min(),xs.max(),100)
ht=pOsc(xls*DEG,pars)
ax.plot(xls,ht,'r-')

# ############################################################
# DECORATION
# ############################################################
ax.set_ylabel("Frequency",fontsize=14)
ax.set_title("Wave %s"%(phasename),position=(0.5,1.05),fontsize=18)
color='r'

ax.set_xlim((0,360))
ax.set_ylim((0.0*hmin,1.1*hmax))

# ############################################################
# SAVING FIGURE
# ############################################################
print(confile)
confile=confile.replace(".conf","_age.conf")
print(confile)
saveFigure(confile,fig)
