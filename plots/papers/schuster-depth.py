# ############################################################
# IMPORT TOOLS
# ############################################################
from tquakes import *
from matplotlib import use
use('Agg')
import matplotlib.pyplot as plt
confile=prepareScript()
conf=execfile(confile)
import matplotlib as mpl

# ############################################################
# CONNECT TO DATABASE
# ############################################################
connection=connectDatabase()
db=connection.cursor()
numpy.random.seed(seed)

# ############################################################
# PREPARE PLOTTING REGION
# ############################################################
fig,axs=subPlots(plt,[1],w=0.9)

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

search=search+"""and
(cluster1='0' or cluster1 like '-%%') and 
Ml+0>2 and
qdeptherr/1<qdepth/1 and
qlat+0>=%.2f and qlat+0<%.2f and 
qlon+0>=%.2f and qlon+0<%.2f and 
qjd+0>=%.5f and qjd+0<=%.5f and
qdepth+0<>32 and qdepth+0<>32.1 and
astatus+0=4
limit %d"""%(latb,latu,
             lonl,lonr,
             jd1,jd2,
             limit)

qids,quakes=getPhases(search,component,db)
nquakes=len(qids)
if random:phases=360*numpy.random.random(nquakes)
else:
    phs=quakes[:,4+phasenum]
    cond=phs<=1
    phs=phs[cond]
    quakes=quakes[cond]
    nquakes=len(phs)
    phases=numpy.array(360*phs)

print "Number of earthquakes with true phases: ",nquakes

# ############################################################
# CALCULATE CONTOUR
# ############################################################
Mls=numpy.linspace(2.0,5.0,nMls)
#Mls=numpy.linspace(numpy.log10(2.0),numpy.log10(5.0),nMls)
deps=numpy.linspace(numpy.log10(20),numpy.log10(200.0),ndeps)

logp=numpy.zeros((nMls,ndeps))
for i in xrange(nMls):
    if vvv:print >>stderr,"Mls = ",Mls[i]
    for j in xrange(ndeps):
        cond=(quakes[:,ML]<=Mls[i])*(quakes[:,QDEP]<=10**deps[j])
        #cond=(quakes[:,ML]<=10**Mls[i])*(quakes[:,QDEP]<=10**deps[j])
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
c=axs[0].contourf(MLS,DEPS,logp,levels=levels,cmap=plt.cm.spectral)
cf=axs[0].contour(MLS,DEPS,logp,levels=[-5.0],colors='k',lw=5)
cbar=plt.colorbar(c,format="%.1f")
cbar.set_label(r"$\log(p)$",fontsize=14)
cax=fig.axes[1]
cax.tick_params(labelsize=10)

# ############################################################
# SCATTER PLOT
# ############################################################
oMls=quakes[:,ML]+0.1*(1-2*numpy.random.rand(len(quakes[:,ML])))
#oMls=numpy.log10(quakes[:,ML]+0.1*(1-2*numpy.random.rand(len(quakes[:,ML]))))
oDeps=numpy.log10(quakes[:,QDEP])


axs[0].plot(oMls,oDeps,'o',mfc='white',ms=2,mec='k',alpha=0.5)

# ############################################################
# DECORATION
# ############################################################
axs[0].set_xlim((Mls.min(),Mls.max()))
axs[0].set_ylim((deps.max(),deps.min()))

ytl=[]
yts=numpy.linspace(numpy.log10(20),numpy.log10(200.0),20)
axs[0].set_yticks(yts)
#for y in axs[0].get_yticks():ytl+=["%.1f"%(10**y)]
for y in yts:ytl+=["%.1f"%(10**y)]
axs[0].set_yticklabels(ytl)

"""
xtl=[]
for x in axs[0].get_xticks():xtl+=["%.1f"%(10**x)]
axs[0].set_xticklabels(xtl)
#"""

axs[0].set_xlabel("$M_l$",fontsize=14)
axs[0].set_ylabel("Depth (km)",fontsize=14)
axs[0].set_title("Wave %s"%(PHASES_DICT[phase][1]),
                 position=(0.5,1.02))

axs[0].grid(zorder=10)
"""
axs[0].text(0.05,0.95,"N = %d\nlat,lon = %.2f, %.2f\n$\Delta$(lat,lon) = %.2f, %.2f\nDate = (%s,%s)"%\
            (nquakes,
             center[0],
             center[1],
             dlat,dlon,
             dateini,dateend),
            horizontalalignment="left",
            verticalalignment="top",
            fontsize=10,
            zorder=50,bbox=dict(fc='w',pad=20),
            transform=axs[0].transAxes)
"""

# ############################################################
# SAVING FIGURE
# ############################################################
saveFigure(confile,fig)
