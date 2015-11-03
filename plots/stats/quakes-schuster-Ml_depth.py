# ############################################################
# IMPORT TOOLS
# ############################################################
from tquakes import *
from matplotlib import use
use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from mpl_toolkits.basemap import Basemap as map,shiftgrid
confile="%s.conf"%BASENAME
execfile(confile)

# ############################################################
# CONNECT TO DATABASE
# ############################################################
connection=connectDatabase()
db=connection.cursor()

# ############################################################
# GET PHASES
# ############################################################
latb=center[0]-dlat/2;latu=center[0]+dlat/2
lonl=center[1]-dlon/2;lonr=center[1]+dlon/2

search=search+"""and qphases<>'' and 
qdepth>0 and Ml+0>2.0 and 
qdeptherr/1<qdepth and
(cluster1='0' or cluster1 like '-%%') and 
qlat+0>=%.2f and qlat+0<%.2f and qlon+0>=%.2f and qlon+0<%.2f 
limit %d"""%(latb,
             latu,
             lonl,
             lonr,
             limit)
qids,quakes=getPhases(search,component,db)
nquakes=len(qids)

# PHASES
phases=360*quakes[:,phase]
# phases=360*numpy.random.random(nquakes)

# ############################################################
# PREPARE PLOT
# ############################################################
fig,axs=subPlots(plt,[1],w=0.9)

# ############################################################
# CALCULATE CONTOUR
# ############################################################
ndeps=20
nMls=20

Mls=numpy.linspace(2.0,5.0,nMls)
deps=numpy.linspace(numpy.log10(20),numpy.log10(200.0),ndeps)

vvv=1
logp=numpy.zeros((nMls,ndeps))
for i in xrange(nMls):
    if vvv:print >>stderr,"Mls = ",Mls[i]
    for j in xrange(ndeps):
        cond=(quakes[:,ML]<=Mls[i])*(quakes[:,QDEP]<=10**deps[j])
        nphases=len(phases[cond])
        if vvv:print >>stderr,1*"\t","depth = ",10**deps[j]
        if nphases>3000:
            sphases=phases[cond]*DEG
            logp[i,j],dlogp=schusterValue(sphases,qbootstrap=1,bootcycles=50)
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
axs[0].text(0.95,0.05,"N = %d\nlat,lon = %.2f, %.2f\n$\Delta$(lat,lon) = %.2f, %.2f"%(nquakes,
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
md5sum=md5sumFile(confile)
figname="%s/%s__%s.png"%(DIRNAME,BASENAME,md5sum)
print "Saving figure ",figname
fig.savefig(figname)
