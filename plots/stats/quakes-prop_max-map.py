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
# GET QUAKES
# ############################################################
nregions=30
dl=dlat/nregions
dt=dlon/nregions
latb=center[0]-dlat/2;latu=center[0]+dlat/2
lonl=center[1]-dlon/2;lonr=center[1]+dlon/2

search=search+"and (cluster1='0' or cluster1 like '-%%') and qlat+0>=%.2f and qlat+0<%.2f and qlon+0>=%.2f and qlon+0<%.2f limit %d"%(latb,latu,lonl,lonr,limit)
qids,quakes=getQuakes(search,db)
nquakes=len(qids)

# ############################################################
# PREPARE PLOT
# ############################################################
fig,axs=subPlots(plt,[1,1],dh=0.05,w=0.7)

# ############################################################
# CALCULATE CONTOUR
# ############################################################
# GRID COORDINATES
latb=center[0]-dlat/2;latu=center[0]+dlat/2
lonl=center[1]-dlon/2;lonr=center[1]+dlon/2
lats=numpy.arange(latb,latu+dt,dt);nlats=len(lats)
lons=numpy.arange(lonl,lonr+dl,dl);nlons=len(lons)

qlats=quakes[:,QLAT]
qlons=quakes[:,QLON]
Mls=quakes[:,ML]
qdeps=quakes[:,QDEP]

Ml_field=numpy.zeros((nlons,nlats))
qdep_field=numpy.zeros((nlons,nlats))
function=max
for i in xrange(nlons-1):
    for j in xrange(nlats-1):
        cond=(qlons>=lons[i])*(qlons<lons[i+1])*(qlats>=lats[j])*(qlats<=lats[j+1])
        if len(Mls[cond]):
            Mlval=Mls[cond].max()
            qdepval=qdeps[cond].max()
            if qdepval==0:qdepval=1E-3
        else:
            Mlval=0
            qdepval=1E-3

        Ml_field[i,j]=Mlval
        qdep_field[i,j]=qdepval

# ############################################################
# CREATE MAPS
# ############################################################
mMl=scatterMap(axs[0],[],[],resolution=resolution,
               merdict=dict(labels=[False,False,True,True]),
               limits=[center[0],center[1],dlat,dlon])
mdep=scatterMap(axs[1],[],[],resolution=resolution,
                merdict=dict(labels=[False,False,True,False]),
                limits=[center[0],center[1],dlat,dlon])

# ############################################################
# PLOT CONTOUR
# ############################################################
# ========================================
# MAGNITUDE
# ========================================
Ml_field,lonsp=shiftgrid(lons[0],Ml_field,lons,start=False)
LATS,LONS=numpy.meshgrid(lats,lonsp)

# CONTOUR
LN,LT=mMl(LONS,LATS)
levels=numpy.linspace(0,Mls.max(),10)
c=mMl.contourf(LN,LT,Ml_field,levels=levels,
               cmap=plt.cm.jet,
               alpha=0.5,zorder=20)

# BAR
cr=mMl.ax.get_position().corners()
lb=cr[0,:];lu=cr[1,:];rb=cr[2,:];ru=cr[3,:]
cax=fig.add_axes([rb[0]+0.05,rb[1],0.05,(ru[1]-rb[1])])
cbar=plt.colorbar(c,drawedges=False,cax=cax,orientation='vertical',
                  format='%.1f')

# ========================================
# DEPTH
# ========================================
qdep_field,lonsp=shiftgrid(lons[0],qdep_field,lons,start=False)
LATS,LONS=numpy.meshgrid(lats,lonsp)

# CONTOUR
LN,LT=mdep(LONS,LATS)
levels=numpy.concatenate(([0],numpy.logspace(0.0,numpy.log10(qdeps.max()),20)))
c=mdep.contourf(LN,LT,qdep_field,levels=levels,alpha=0.3,zorder=20,
                cmap=plt.cm.spectral,norm=LogNorm(),
                edgecolors='none',lw=0)

# BAR
cr=mdep.ax.get_position().corners()
lb=cr[0,:];lu=cr[1,:];rb=cr[2,:];ru=cr[3,:]
cax=fig.add_axes([rb[0]+0.05,rb[1],0.05,(ru[1]-rb[1])])
cbar=plt.colorbar(c,drawedges=False,cax=cax,orientation='vertical',
                  format='%.1f')

# ############################################################
# DECORATION
# ############################################################
axs[0].set_title("Maximum Magnitude",position=(0.5,1.05))
axs[1].set_title("Maximum Depth",position=(0.5,1.05))

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
