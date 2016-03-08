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
fig,axs=subPlots(plt,[1,1],l=0.1,w=0.9,dh=0.08)

# ############################################################
# GET PHASES
# ############################################################
latb=center[0]-dlat/2;latu=center[0]+dlat/2
lonl=center[1]-dlon/2;lonr=center[1]+dlon/2

search=search+"and qphases<>'' and (cluster1='0' or cluster1 like '-%%') and qlat+0>=%.2f and qlat+0<%.2f and qlon+0>=%.2f and qlon+0<%.2f limit %d"%(latb,
                                                                                                                                                      latu,
                                                                                                                                                      lonl,
                                                                                                                                                      lonr,
                                                                                                                                                      limit)
qids,quakes=getPhases(search,"hs",db)
nquakes=len(qids)

# PHASES
phases=360*quakes[:,SD]

# ############################################################
# CALCULATE CONTOUR
# ############################################################
ndeps=10
nMls=10

Mls=numpy.linspace(1.0,7.0,nMls)
deps=numpy.linspace(numpy.log10(0.1),numpy.log10(200.0),ndeps)

logp=numpy.zeros((nMls,ndeps))
fquakes=numpy.zeros((nMls,ndeps))
for i in xrange(nMls):
    if i==nMls-1:maxMl=10.0
    else:maxMl=Mls[i+1]
    for j in xrange(ndeps):
        # CUMMULATIVE
        cond=(quakes[:,ML]<=Mls[i])*(quakes[:,QDEP]<=10**deps[j])
        nphases=len(phases[cond])
        logp[i,j]=(1.0*nphases)/nquakes
        # FREQUENCY
        if j==ndeps-1:maxd=6000.0
        else:maxd=10**deps[j+1]
        cond=(quakes[:,ML]>=Mls[i])*(quakes[:,ML]<maxMl)*\
            (quakes[:,QDEP]>=10**deps[j])*(quakes[:,QDEP]<maxd)
        nphases=len(phases[cond])
        if nphases>0:
            fquakes[i,j]=numpy.log10((1.0*nphases))
        else:
            fquakes[i,j]=0.0

# ############################################################
# PLOT
# ############################################################

DEPS,MLS=numpy.meshgrid(deps,Mls)

#CUMULATIVE
levels=100*numpy.linspace(logp.min(),logp.max(),100)
c=axs[0].contourf(MLS,DEPS,100*logp,levels=levels,cmap=plt.cm.spectral)
cf=axs[0].contour(MLS,DEPS,100*logp,levels=[5.0,50.0,95.0],colors='w',ls='-',lw=10)
axs[0].clabel(cf,inline=True,fmt="%.0f%%",fontsize=10)
levels=100*numpy.logspace(numpy.log10(0.01),numpy.log10(100.0),10)
levels=100*numpy.arange(0.10,0.95,0.05)
cf=axs[0].contour(MLS,DEPS,100*logp,levels=levels,colors='w',ls='-',lw=10)
plt.colorbar(c,ax=axs[0])

#FREQUENCY
levels=numpy.linspace(fquakes.min(),fquakes.max(),100)

# c=axs[1].imshow(fquakes,cmap=plt.cm.spectral)
c=axs[1].contourf(MLS,DEPS,fquakes,levels=levels,cmap=plt.cm.spectral)
cbar=plt.colorbar(c,ax=axs[1])
yts=cbar.ax.get_yticks()
ytl=[]
for yt in yts:
    val=yt*(levels[-1]-levels[0])+levels[0]
    ytl+=["%.0f"%10**(val)]
cbar.ax.set_yticklabels(ytl)

axs[0].set_xticks(Mls)
axs[0].set_yticks(deps)

axs[1].set_xticks(Mls)
axs[1].set_yticks(deps)

# ############################################################
# DECORATION
# ############################################################
for ax in axs:
    ax.set_ylim((deps.max(),deps.min()))
    ytl=[]
    for y in ax.get_yticks():ytl+=["%.1f"%(10**y)]
    ax.set_yticklabels(ytl)
    ax.grid(zorder=10)
    ax.set_ylabel("Depth (km)")

axs[0].set_xlabel("$M_l$")

axs[1].text(0.95,0.95,"N = %d\nlat,lon = %.2f, %.2f\n$\Delta$(lat,lon) = %.2f, %.2f"%(nquakes,
                                                                                      center[0],
                                                                                      center[1],
                                                                                      dlat,dlon),
            horizontalalignment="right",
            verticalalignment="top",
            zorder=50,bbox=dict(fc='w',pad=20),
            transform=axs[0].transAxes)

axs[0].set_title("Earthquakes Cummulative Distribution",position=(0.5,1.02))
axs[1].set_title("Earthquakes Frequency",position=(0.5,1.02))

# ############################################################
# SAVING FIGURE
# ############################################################
saveFigure(confile,fig)
