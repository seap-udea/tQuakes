from tquakes import *
from matplotlib import use
use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap as map

# ############################################################
# CONNECT TO DATABASE
# ############################################################
connection=connectDatabase()
db=connection.cursor()

def plotmap(qlat,qlon):
    nquakes=len(qlon)
    qlatmin=min(qlat)
    qlatmax=max(qlat)
    qlonmin=min(qlon)
    qlonmax=max(qlon)
    qlonmean=(qlonmax+qlonmin)/2
    qlatmean=(qlatmax+qlatmin)/2
    dlat=abs(qlatmax-qlatmin)*PI/180*6780.0e3
    dlon=abs(qlonmax-qlonmin)*PI/180*6780.0e3

    # ############################################################
    # PREPARE FIGURE
    # ############################################################
    fig=plt.figure(figsize=(8,8))
    ax=fig.add_axes([0.05,0.05,0.90,0.85])
    m=map(projection="aea",resolution='c',width=dlon,height=dlat,lat_0=qlatmean,lon_0=qlonmean)
    m.drawlsmask(alpha=0.5)
    m.etopo(zorder=-10)
    m.drawparallels(numpy.arange(-45,45,1),labels=[True,True,False,False],fontsize=10,zorder=10,linewidth=0.5,fmt=lat2str)
    m.drawmeridians(numpy.arange(-90,90,1),labels=[False,False,True,True],fontsize=10,zorder=10,linewidth=0.5,fmt=lon2str)

    # ############################################################
    # PLOT
    # ############################################################
    x,y=m(qlon,qlat)
    ax.plot(x,y,'ok',markersize=1,markeredgecolor='None',alpha=1)

    # ############################################################
    # DECORATION
    # ############################################################
    ax.set_title("Scatter plot of %d Earthquakes"%nquakes,position=(0.5,1.05))

    # ############################################################
    # SAVE FIGURE
    # ############################################################
    figname="%s/%s.png"%(DIRNAME,BASENAME)
    print "Saving figure ",figname
    fig.savefig(figname)

