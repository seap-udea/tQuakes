# ############################################################
# IMPORT TOOLS
# ############################################################
from tquakes import *
from matplotlib import use
use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from mpl_toolkits.basemap import Basemap as map,shiftgrid
confile=prepareScript()
conf=execfile(confile)
quake=loadConf("quake.conf")

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
# GET QUAKES
# ############################################################
dl=dlat/10.0
dt=dlon/10.0
latb=center[0]-dlat/2;latu=center[0]+dlat/2
lonl=center[1]-dlon/2;lonr=center[1]+dlon/2

search=search+"and (cluster1='0' or cluster1 like '-%%') and qlat+0>=%.2f and qlat+0<%.2f and qlon+0>=%.2f and qlon+0<%.2f limit %d"%(latb,latu,lonl,lonr,limit)
qids,quakes=getQuakes(search,db)
nquakes=len(qids)

# ############################################################
# GET QUAKE MAP
# ############################################################


# ############################################################
# CREATE MAPS
# ############################################################
ms=scatterMap(axs[0],quakes[:,QLAT],quakes[:,QLON],resolution=resolution,
              limits=[center[0],center[1],dlat,dlon],
              merdict=dict(labels=[False,False,True,False]),
              color='k',marker='o',linestyle='none',
              markeredgecolor='none',markersize=1,zorder=10)

slon=float(quake.qlon);slat=float(quake.qlat);
x,y=ms(slon,slat)
ms.plot(x,y,'wo',markersize=20,zorder=50000)

# ############################################################
# DECORATION
# ############################################################
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
saveFigure(confile,fig)
