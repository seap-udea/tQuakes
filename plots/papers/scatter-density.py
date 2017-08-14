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

# ############################################################
# CONNECT TO DATABASE
# ############################################################
connection=connectDatabase()
db=connection.cursor()

# ############################################################
# PREPARE PLOTTING REGION
# ############################################################
fig,axs=subPlots(plt,[1,1])

"""
fig=plt.figure(figsize=(14,6))

axs=[]
axs+=[fig.add_axes([0.5,0.1,0.5,0.8])]
axs+=[fig.add_axes([0.05,0.1,0.5,0.8])]
"""
# ############################################################
# GET QUAKES
# ############################################################
dl=dlat/10.0
dt=dlon/10.0
latb=center[0]-dlat/2;latu=center[0]+dlat/2
lonl=center[1]-dlon/2;lonr=center[1]+dlon/2

# and (cluster1='0' or cluster1 like '-%%') 
search=search+"and qlat+0>=%.2f and qlat+0<%.2f and qlon+0>=%.2f and qlon+0<%.2f and (cluster1='0' or cluster1 like '-%%') limit %d"%(latb,latu,lonl,lonr,limit)
qids,quakes=getQuakes(search,db)
nquakes=len(qids)

# ############################################################
# CALCULATE CONTOUR
# ############################################################
# GRID COORDINATES
H,xe,ye=numpy.histogram2d(quakes[:,QLON],quakes[:,QLAT],bins=100)
lons=(xe[:-1]+xe[1:])/2;nlons=len(lons)
lats=(ye[:-1]+ye[1:])/2;nlats=len(lats)
field=H

# ############################################################
# CREATE MAPS
# ############################################################
md=scatterMap(axs[0],[],[],resolution=resolution,
              merdict=dict(labels=[False,False,True,True]),
              pardict=dict(labels=[False,True,False,False]),
              limits=[center[0],center[1],dlat,dlon])
ms=scatterMap(axs[1],quakes[:,QLAT],quakes[:,QLON],resolution=resolution,
              limits=[center[0],center[1],dlat,dlon],
              merdict=dict(labels=[False,False,True,True]),
              pardict=dict(labels=[True,False,False,False]),
              color='k',marker='o',linestyle='none',
              markeredgecolor='none',markersize=1,zorder=10)

# ############################################################
# PLOT CONTOUR
# ############################################################
field,lons=shiftgrid(lons[0],field,lons,start=False)
LATS,LONS=numpy.meshgrid(lats,lons)
LN,LT=md(LONS,LATS)

# CONTOUR
levels=numpy.concatenate(([0],numpy.logspace(0.0,numpy.log10(H.max()),20)))
c=md.contourf(LN,LT,field,levels=levels,alpha=0.3,zorder=20,
              cmap=plt.cm.jet,norm=LogNorm(),
              edgecolors='none',lw=0)

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
