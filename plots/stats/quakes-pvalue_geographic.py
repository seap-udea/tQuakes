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
dl=dlat/10.0
dt=dlon/10.0

# ############################################################
# GET QUAKES
# ############################################################
latb=center[0]-dlat/2;latu=center[0]+dlat/2
lonl=center[1]-dlon/2;lonr=center[1]+dlon/2

search="""where qphases<>'' and 
qdepth+0>0 and Ml+0>1.0 and 
qdeptherr/1<qdepth/1 and
Ml+0<=%.1f and qdepth+0<=%.1f and 
(cluster1='0' or cluster1 like '-%%') and 
qlat+0>=%.2f and qlat+0<%.2f and qlon+0>=%.2f and qlon+0<%.2f 
limit %d"""%(Mlmax,depthmax,
             latb,
             latu,
             lonl,
             lonr,
             limit)
qids,quakes=getPhases(search,component,db)
nquakes=len(qids)

print "Search: ",search
print "Number of quakes: ",nquakes

# ############################################################
# GLOBAL SCHUSTER P-VALUE
# ############################################################
print phase
phases=360*quakes[:,phase]
logpt,dlogpt=schusterValue(phases*DEG,qbootstrap=1,bootcycles=50)

print "Global p-value: log(p) = %.1f +/- %.1f"%(logpt,dlogpt)

# ############################################################
# PREPARE PLOT
# ############################################################
fig,axs=subPlots(plt,[1])

m=scatterMap(axs[0],quakes[:,QLAT],quakes[:,QLON],resolution=resolution,
             merdict=dict(labels=[False,False,False,True]),
             limits=[center[0],center[1],dlat,dlon],
             color='k',marker='o',linestyle='none',
             markeredgecolor='none',markersize=1,zorder=10)

# ############################################################
# DIVIDE REGION
# ############################################################
import matplotlib.patches as patches

ngrid=4
lats=numpy.linspace(latb,latu,ngrid+1)
lons=numpy.linspace(lonl,lonr,ngrid+1)

qlats=quakes[:,QLAT]
qlons=quakes[:,QLON]
ntot=0
for i in xrange(ngrid):
    latmed=(lats[i]+lats[i+1])/2
    for j in xrange(ngrid):
        lonmed=(lons[j]+lons[j+1])/2
        cond=(qlats>=lats[i])*(qlats<lats[i+1])*(qlons>=lons[j])*(qlons<lons[j+1])
        bphases=phases[cond]
        nphases=len(bphases)
        ntot+=nphases
        print lats[i],lons[j],len(bphases)
        if nphases>0:
            logp,dlogp=schusterValue(bphases*DEG,qbootstrap=1,bootcycles=50)
            print logp,dlogp
        else:
            logp=dlogp=0
        x,y=m(lonmed,latmed)
        axs[0].text(x,y,"%.1f\n%d"%(logp,nphases),zorder=60,fontsize=10,
                    horizontalalignment='center',verticalalignment='center')

        radius=(lons[j+1]-lons[j])/2*DEG*6371e3*abs(logp)/4
        circle=patches.Circle((x,y),radius,zorder=50,fc='w',ec='k',alpha=0.5)
        axs[0].add_patch(circle)

# ############################################################
# DECORATION
# ############################################################
axs[0].set_title("Global $\log(p)$ = %.2f $\pm$ %.2f, %s, phase %s"%(logpt,dlogpt,COMPONENTS_DICT[component][1],PHASES[phase]),
                 position=(0.5,1.02))
axs[0].text(0.5,-0.08,r"$M_{l,max}=%.1f$, $d_{max}=%.1f$"%(Mlmax,depthmax),
            horizontalalignment='center',verticalalignment='center',
            transform=axs[0].transAxes)

# ############################################################
# SAVING FIGURE
# ############################################################
md5sum=md5sumFile(confile)
figname="%s/%s__%s.png"%(DIRNAME,BASENAME,md5sum)
print "Saving figure ",figname
fig.savefig(figname)
