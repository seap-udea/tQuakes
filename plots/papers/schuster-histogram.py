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

# COLUMNS: 
# 0:qjd,1:qlat,2:qlon,3:qdepth,4:Mlq
# Fourier: 5:sd, 6:dn, 7:fn, 8:mn
# Boundaries: 9:sd, 10:fn, 11:mn
qids,phases=getPhases(search,component,db)
nquakes=phases.shape[0]
print "Search:",search
print "Number of quakes found: ",nquakes
phs=phases[:,4+phasenum]

if random:
    phs=360*numpy.random.random(nquakes)
else:
    if 'fourier' not in phase:
        cond=phs<=1
        phs=phs[cond]
        nquakes=len(phs)
        phs*=360

print "Number of earthquakes with true phases: ",nquakes

# ############################################################
# HISTOGRAM
# ############################################################
normed=False

nbins=int(360.0/dphase)
h,bins=numpy.histogram(phs,nbins,normed=normed)
xs=(bins[:-1]+bins[1:])/2
dh=numpy.sqrt(h)

hmax=(h+dh).max()
hmin=(h-dh).min()
hmean=h.mean()

ax.hist(phs,nbins,facecolor='blue',normed=normed,alpha=0.2)
ax.errorbar(xs,h,yerr=dh,linestyle='None',color='r')

# ############################################################
# FIT
# ############################################################
pars,n=leastsq(chisq,[1.0,1.0,1.0],args=(pOsc,xs*DEG,h,dh))
xls=numpy.linspace(xs.min(),xs.max(),100)
ht=pOsc(xls*DEG,pars)
ax.plot(xls,ht,'r-')

# ############################################################
# SCHUSTER VALUE
# ############################################################
logp,dlogp=schusterValue(phs*DEG,
                         qbootstrap=qbootstrap,
                         facbootstrap=facbootstrap,
                         bootcycles=nsamples)
p=numpy.exp(logp)
print "Schuster p-value: log(p) = %.2f +/- %.2f, p = %.2f%%"%(logp,dlogp,p*100)

# ############################################################
# PHASES SCATTER PLOT
# ############################################################
Mls=phases[cond,ML]+0.1*(1-2*numpy.random.rand(nquakes))
ichoice=numpy.random.choice(numpy.arange(0,nquakes),nquakes)

Mls=Mls[ichoice]
phs=phs[ichoice]

axs[-2].plot(phs,Mls,'ko',markersize=1)

# ############################################################
# DECORATION
# ############################################################
axs[-2].set_xlim((0.0,360.0))

axs[-2].set_xlabel("Phase (degrees)",fontsize=14)
axs[-2].set_ylabel("$M_l$",fontsize=14)

ax.set_ylabel("Frequency",fontsize=14)
ax.set_title("Wave %s"%(phasename),position=(0.5,1.05),fontsize=18)
if p<0.05:color="b"
else:color="r"

ax.set_xlim((0,360))
ax.set_ylim((0.0*hmin,1.1*hmax))

ax.set_xticklabels([])

# ############################################################
# SAVING FIGURE
# ############################################################
saveFigure(confile,fig)
