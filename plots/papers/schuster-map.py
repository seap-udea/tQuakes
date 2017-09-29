# ############################################################
# IMPORT TOOLS
# ############################################################
from tquakes import *
from matplotlib import use
use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from mpl_toolkits.basemap import Basemap as map,shiftgrid
import matplotlib.patches as patches
confile=prepareScript()
conf=execfile(confile)
import matplotlib as mpl

def logp2color(logp,logpc,logpm):
    if logp>logpc:
        fc=0.5+(logp-logpc)/(logpm-logpc)
    else:
        fc=0.5+(logp-logpc)/logpc
    return fc

# ############################################################
# CONNECT TO DATABASE
# ############################################################
connection=connectDatabase()
db=connection.cursor()
numpy.random.seed(seed)

# ############################################################
# PREPARE PLOTTING REGION
# ############################################################
fig,axs=subPlots(plt,[1])

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
# GET QUAKES
# ############################################################
dl=dlat/10.0
dt=dlon/10.0
latb=center[0]-dlat/2;latu=center[0]+dlat/2
lonl=center[1]-dlon/2;lonr=center[1]+dlon/2
jd1=date2jd(datetime.datetime.strptime(dateini,"%Y-%m-%d %H:%M:%S"))
jd2=date2jd(datetime.datetime.strptime(dateend,"%Y-%m-%d %H:%M:%S"))

search=search+"""and
Ml+0>=%.1f AND Ml+0<%.1f and 
qdepth+0>=%.2f and qdepth+0<%.2f and 
qlat+0>=%.2f and qlat+0<%.2f and 
qlon+0>=%.2f and qlon+0<%.2f and
qjd+0>=%.5f and qjd+0<=%.5f
limit %d"""%(Mlmin,Mlmax,
             depthmin,depthmax,
             latb,latu,
             lonl,lonr,
             jd1,jd2,
             limit)
qids,quakes=getPhases(search,component,db)
nquakes=len(qids)

print "Search: ",search
print "Number of quakes: ",nquakes

# ############################################################
# GLOBAL SCHUSTER P-VALUE
# ############################################################
if random:phases=360*numpy.random.random(nquakes)
else:
    phs=quakes[:,4+phasenum]
    cond=phs<=1
    phs=phs[cond]
    quakes=quakes[cond]
    nquakes=len(phs)
    phases=numpy.array(360*phs)

print "Number of earthquakes with true phases: ",nquakes

logpt,dlogpt=schusterValue(phases*DEG,
                           qbootstrap=qbootstrap,
                           facbootstrap=0.8,
                           bootcycles=nsamples)

print "Global p-value: log(p) = %.1f +/- %.1f"%(logpt,dlogpt)

# ############################################################
# DIVIDE REGION
# ############################################################
m=scatterMap(axs[0],quakes[:,QLAT],quakes[:,QLON],
             resolution=resolution,
             merdict=dict(labels=[False,False,False,True]),
             pardict=dict(labels=[True,False,False,True]),
             limits=[center[0],center[1],dlat,dlon],
             color='k',marker='o',linestyle='none',
             topography=False,lsmask=False,
             markeredgecolor='none',markersize=1,zorder=10)

lats=numpy.linspace(latb,latu,ngrid+1)
lons=numpy.linspace(lonl,lonr,ngrid+1)

qlats=quakes[:,QLAT]
qlons=quakes[:,QLON]
ntot=0
logps=numpy.zeros((ngrid,ngrid))
dlogps=numpy.zeros((ngrid,ngrid))
nphases=numpy.zeros((ngrid,ngrid))
for i in xrange(ngrid):
    for j in xrange(ngrid):
        cond=(qlats>=lats[i])*(qlats<lats[i+1])*\
            (qlons>=lons[j])*(qlons<lons[j+1])
        bphases=phases[cond]
        nphases[i,j]=len(bphases)
        ntot+=nphases[i,j]
        if vvv:print lats[i],lons[j],len(bphases)
        if nphases[i,j]>0:
            logp,dlogp=schusterValue(bphases*DEG,
                                     qbootstrap=1,
                                     bootcycles=50)
            logps[i,j]=logp
            if vvv:print logp,dlogp
        else:
            logp=dlogp=0
            logps[i,j]=logp

logpmax=abs(logps).max()
maxradius=min((lons[1]-lons[0]),
              (lats[1]-lats[0]))/2*DEG*6371e3

#cmap=plt.get_cmap("seismic")
#cmap=plt.get_cmap("bwr")
cmap=plt.get_cmap("Spectral_r")
for i in xrange(ngrid):
    latmed=(lats[i]+lats[i+1])/2
    for j in xrange(ngrid):
        lonmed=(lons[j]+lons[j+1])/2

        fradius=abs(logps[i,j])/logpmax
        
        if fradius==0:continue
        
        fc='y'
        radius=maxradius
        if fradius<1:radius*=fradius
        else:fc='red'

        x,y=m(lonmed,latmed)
        #text="%.1f\n%d"%(logps[i,j],nphases[i,j])
        #text="%.1f"%(logps[i,j])
        text=""
        axs[0].text(x,y,text,
                    zorder=60,fontsize=10,
                    horizontalalignment='center',
                    verticalalignment='center')
        #"""
        fc=cmap(logp2color(abs(logps[i,j]),3.0,abs(logpmax)))
        
        circle=patches.Circle((x,y),radius,zorder=50,
                              fc=fc,ec='k',alpha=0.5)
        axs[0].add_patch(circle)
        #"""

        """
        circle=patches.Rectangle((x,y),width=radius,height=radius,zorder=50,
                              fc=fc,ec='none',alpha=0.5)
        """
        """
        x,y=m(lons[j],lats[i])
        width=(lons[j+1]-lons[j])*DEG*6371e3
        height=(lats[i+1]-lats[i])*DEG*6371e3
        
        fc=cmap(abs(logps[i,j])/5)
        rectangle=patches.Rectangle((x,y),width=width,height=height,zorder=50,
                                 fc=fc,ec='none',alpha=0.5)

        axs[0].add_patch(rectangle)
        #"""

axs+=[fig.add_axes([0.75,0.1,0.03,0.75])]
cbar=mpl.colorbar.ColorbarBase(axs[1],cmap=cmap,orientation='vertical',alpha=0.5)
axs[1].tick_params(labelsize=10)
cbar.set_ticks([0.0,0.5,1.0])
cbar.set_ticklabels([0.0,-3.0,"-%.1f"%logpmax])
cbar.set_label(r"$\log(p)$",fontsize=14)

# ############################################################
# DECORATION
# ############################################################
axs[0].set_title("Wave %s, $d\in[%.1f,%.1f]$, $M_{l}\in[%.1f,%.1f]$"%(phasename,depthmin,depthmax,Mlmin,Mlmax),
                 position=(0.5,1.02))
"""
axs[0].text(0.5,-0.08,r"$d\in[%.1f,%.1f]$, $M_{l}\in[%.1f,%.1f]$"%\
            (depthmin,depthmax,Mlmin,Mlmax),
            horizontalalignment='center',
            verticalalignment='center',
            transform=axs[0].transAxes)
"""

# ############################################################
# SAVING FIGURE
# ############################################################
saveFigure(confile,fig,qwater=False)
