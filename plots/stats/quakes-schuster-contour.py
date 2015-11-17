# ############################################################
# IMPORT TOOLS
# ############################################################
from tquakes import *
from matplotlib import use
use('Agg')
import matplotlib.pyplot as plt
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
fig,axs=subPlots(plt,[1],w=0.9)

# ############################################################
# GET PHASES
# ############################################################
latb=center[0]-dlat/2;latu=center[0]+dlat/2
lonl=center[1]-dlon/2;lonr=center[1]+dlon/2

search=search+"""and
(cluster1='0' or cluster1 like '-%%') and 
qlat+0>=%.2f and qlat+0<%.2f and 
qlon+0>=%.2f and qlon+0<%.2f 
limit %d"""%(latb,
             latu,
             lonl,
             lonr,
             limit)

qids,quakes=getPhases(search,component,db)
nquakes=len(qids)
if random:phases=360*numpy.random.random(nquakes)
else:phases=360*quakes[:,phase]

# ############################################################
# CALCULATE CONTOUR
# ############################################################
Mls=numpy.linspace(2.0,5.0,nMls)
deps=numpy.linspace(numpy.log10(20),numpy.log10(200.0),ndeps)

logp=numpy.zeros((nMls,ndeps))
for i in xrange(nMls):
    if vvv:print >>stderr,"Mls = ",Mls[i]
    for j in xrange(ndeps):
        cond=(quakes[:,ML]<=Mls[i])*(quakes[:,QDEP]<=10**deps[j])
        nphases=len(phases[cond])
        if vvv:print >>stderr,1*"\t","depth = ",10**deps[j]
        if nphases>3000:
            sphases=phases[cond]*DEG
            logp[i,j],dlogp=schusterValue(sphases,qbootstrap=qbootstrap,bootcycles=nsamples)
        else:
            logp[i,j]=0;dlogp=0.0
        if vvv:print >>stderr, 2*"\t","nphases = ",nphases
        if vvv:print >>stderr,2*"\t","log(p) = %.2e +/- %.2e"%(logp[i,j],dlogp)

# ############################################################
# PLOT
# ############################################################
DEPS,MLS=numpy.meshgrid(deps,Mls)
levels=numpy.linspace(logp.min(),logp.max(),100)
# levels=numpy.linspace(-10,0,101)
c=axs[0].contourf(MLS,DEPS,logp,levels=levels,cmap=plt.cm.spectral)
cf=axs[0].contour(MLS,DEPS,logp,levels=[numpy.log(0.05)],colors='k',lw=5)
plt.colorbar(c)

# ############################################################
# DECORATION
# ############################################################
axs[0].set_ylim((deps.max(),deps.min()))
ytl=[]
for y in axs[0].get_yticks():ytl+=["%.1f"%(10**y)]
axs[0].set_yticklabels(ytl)

axs[0].set_xlabel("$M_l$",fontsize=14)
axs[0].set_ylabel("Depth (km)",fontsize=14)
axs[0].set_title("$\log(p)$, %s, phase %s"%(COMPONENTS_DICT[component][1],PHASES[phase]),
                 position=(0.5,1.02))

axs[0].grid(zorder=10)
axs[0].text(0.95,0.05,"N = %d\nlat,lon = %.2f, %.2f\n$\Delta$(lat,lon) = %.2f, %.2f"%\
            (nquakes,
             center[0],
             center[1],
             dlat,dlon),
            horizontalalignment="right",
            verticalalignment="bottom",
            zorder=50,bbox=dict(fc='w',pad=20),
            transform=axs[0].transAxes)

# ############################################################
# SAVING FIGURE
# ############################################################
saveFigure(confile,fig)
