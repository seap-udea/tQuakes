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

# ############################################################
# CONNECT TO DATABASE
# ############################################################
connection=connectDatabase()
db=connection.cursor()

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
phases=360*quakes[:,4+phasenum]
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
             limits=[center[0],center[1],dlat,dlon],
             color='k',marker='o',linestyle='none',
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
logpmax=3.0
maxradius=min((lons[1]-lons[0]),
              (lats[1]-lats[0]))/2*DEG*6371e3
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
        
        circle=patches.Circle((x,y),radius,zorder=50,
                              fc=fc,ec='none',alpha=0.5)
        axs[0].add_patch(circle)

        axs[0].text(x,y,"%.1f\n%d"%(logps[i,j],nphases[i,j]),
                    zorder=60,fontsize=10,
                    horizontalalignment='center',
                    verticalalignment='center')

# ############################################################
# DECORATION
# ############################################################
axs[0].set_title("Global $\log(p)$ = %.2f $\pm$ %.2f, %s, phase %s"%(logpt,dlogpt,COMPONENTS_DICT[component][1],phasename),
                 position=(0.5,1.02))
axs[0].text(0.5,-0.08,r"$M_{l,max}=%.1f$, $d_{max}=%.1f$ km, Date = (%s,%s)"%\
            (Mlmax,depthmax,dateini,dateend),
            horizontalalignment='center',
            verticalalignment='center',
            transform=axs[0].transAxes)

# ############################################################
# SAVING FIGURE
# ############################################################
saveFigure(confile,fig)
