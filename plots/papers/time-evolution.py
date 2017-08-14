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
fig,axs=subPlots(plt,[1],b=0.15,dh=0.02)
ax=axs[0]

# ############################################################
# GET PHASES
# ############################################################
latb=center[0]-dlat/2;latu=center[0]+dlat/2
lonl=center[1]-dlon/2;lonr=center[1]+dlon/2

# ############################################################
# GET PHASES
# ############################################################
latb=center[0]-dlat/2;latu=center[0]+dlat/2
lonl=center[1]-dlon/2;lonr=center[1]+dlon/2

search="""where 
qdeptherr/1<qdepth/1 and
Ml+0>=%.2f AND Ml+0<%.2f and 
qdepth+0>=%.2f and qdepth+0<%.2f and 
qlat+0>=%.2f and qlat+0<%.2f and 
qlon+0>=%.2f and qlon+0<%.2f and
(cluster1='0' or cluster1 like '-%%') 
limit %d"""%(Mlmin,Mlmax,
             depthmin,depthmax,
             latb,latu,
             lonl,lonr,
             limit)

qids,quakes=getQuakes(search,db)
nquakes=len(qids)
times=quakes[:,QJD]

print "Number of earthquakes:",nquakes

# ############################################################
# PLOTS
# ############################################################
scatter=0.1
ax.plot(times,
        quakes[:,ML]+scatter*(2*numpy.random.random(nquakes)-1),
        'ko',markersize=1,zorder=100)

# ############################################################
# DECORATION
# ############################################################
tmin=min(times)
tmax=max(times)
xts=numpy.linspace(tmin,tmax,20)
ax.set_xticks(xts)
xtl=[]
for xt in xts:
    date=jd2gcal(int(xt),0)
    xtl+=["%d-%d-%d"%(date[0],date[1],date[2])]
ax.set_xticklabels(xtl,rotation=35,
                       fontsize=10,horizontalalignment='right')
ax.set_xlim((tmin,tmax))
ax.grid(color='gray',ls='solid',zorder=-100)

ax.set_ylabel("Local magnitude, $M_l$",fontsize=14)

xt=gcal2jd(2008,3,21)
ax.axvline(xt[0]+xt[1],color='blue',lw=2)

ax.text(0.25,0.8,"A",fontsize=20,color='k',transform=ax.transAxes)
ax.text(0.8,0.8,"B",fontsize=20,color='k',transform=ax.transAxes)

# ############################################################
# SAVING FIGURE
# ############################################################
saveFigure(confile,fig)

