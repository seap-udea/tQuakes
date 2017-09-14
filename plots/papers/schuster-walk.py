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
fig,axs=subPlots(plt,[1],l=0.12,dh=[0.02,0.02,0.005])
ax=axs[0]

# ############################################################
# COMPONENT AND PHASE INFORMATION
# ############################################################
numpy.random.seed(seed)
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
        phs=phs[phs<=1]
        nquakes=len(phs)
        phs*=360

print "Number of earthquakes with true phases: ",nquakes

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
# SCHUSTER PLOT
# ############################################################
ax.axis('off')

xs,ys=schusterSteps(phs*DEG,
                    qbootstrap=qbootstrap,
                    facbootstrap=facbootstrap)
ds=numpy.sqrt(xs[-1]**2+ys[-1]**2)
phtrend=numpy.arctan2(ys[-1],xs[-1])*RAD

ax.plot(xs,ys,'k-')
ax.plot([xs[0],xs[-1]],[ys[0],ys[-1]],'b-')

ngrid=5
dd=int(ds/5)
dini=dd
dend=int(ds)

dgrid=[]
dini=int(numpy.sqrt(0.5*nquakes))

dini=0.5
dend=19.5
dd=2.0

d=dini
while True:
    dp=numpy.floor(numpy.sqrt(d*nquakes))
    dgrid+=[dp]
    d+=dd
    if d>dend:break

for d in dgrid:
    circle=patches.Circle((0,0),d,
                          fc='none',ec='k')
    ax.add_patch(circle)

for d in dgrid:
    ax.text(0.0,d,r"$%.1f$"%((1.0*d**2)/nquakes),
            bbox=dict(fc='w',ec='none'),fontsize=8,
            horizontalalignment='center')

"""
ax.text(0.0,-ds/2,r"Trend phase = $%.1f^o$"%phtrend,
             bbox=dict(fc='w',ec='none'),fontsize=10,
             horizontalalignment='center')
"""

bbox=ax.get_window_extent()
w,h=bbox.width,bbox.height
fac=(1.0*w)/h
dfin=numpy.floor(numpy.sqrt(dend*nquakes))
ax.set_xlim((-fac*dfin,fac*dfin))
ax.set_ylim((-dfin,dfin))

# ############################################################
# DECORATION
# ############################################################
ax.text(0.5,+1.05,"$-\log\;p$",fontsize=14,transform=ax.transAxes,ha='center')
ax.text(0.5,-0.05,"$N$=%d, $\log\;p=%.1f\pm%.1f$, %s, Wave %s"%(nquakes,logp,dlogp,compname,phasename),
        fontsize=10,transform=ax.transAxes,ha='center')

# ############################################################
# SAVING FIGURE
# ############################################################
saveFigure(confile,fig,qwater=False)
