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

    # ############################################################
    # CONNECT TO DATABASE
    # ############################################################
    connection=connectDatabase()
    db=connection.cursor()

    # ############################################################
    # PREPARE FIGURE
    # ############################################################
    fig=plt.figure(figsize=(8,8))
    ax=fig.add_axes([0.05,0.05,0.90,0.85])

    # ############################################################
    # CREATE MAP
    # ############################################################
    m=scatterMap(ax,qlat,qlon,
                 color='k',marker='o',linestyle='None',
                 markersize=1,markeredgecolor='None',alpha=1)

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
