# ############################################################
# IMPORT TOOLS
# ############################################################
from tquakes import *
from matplotlib import use
use('Agg')
import matplotlib.pyplot as plt
import spiceypy as sp

# ############################################################
# PARAMETERS
# ############################################################
yini=int(argv[1])
yend=int(argv[2])
fname="astronomy-extremes-%s_%s"%(yini,yend)

# ############################################################
# SPICE INITIALIZATION
# ############################################################
sp.furnsh("util/kernels/kernels.mk")

# ############################################################
# LOAD DATA
# ############################################################
def loadExtremesTable(extremes,table):
    n=table.shape[0]
    data=dict()
    for i in xrange(n):
        if i==0:continue
        line=table[i]
        if line[1]>1E8:
            ncomp=int(line[0])
            name=extremes[ncomp-1][1]
            data[name]=numpy.array([0,0])
            continue
        data[name]=numpy.vstack((data[name],line))
    return data

table=numpy.loadtxt(fname+".data")
data=loadExtremesTable(EXTREMES,table)

tmin=min(data["Perigea"][1:,0])
tmax=max(data["Perigea"][1:,0])

# ############################################################
# PLOT OF EXTREMES
# ############################################################
fig,axs=subPlots(plt,[1,1],dh=0)

# LUNAR
subdata=data["Perigea"]
axs[0].plot(subdata[1:,0],subdata[1:,1],'r+-')
subdata=data["Apogea"]
axs[0].plot(subdata[1:,0],subdata[1:,1],'b+')

subdata=data["Min.Perigee"]
axs[0].plot(subdata[1:,0],subdata[1:,1],'ro')
subdata=data["Max.Apogee"]
axs[0].plot(subdata[1:,0],subdata[1:,1],'bo')

# SOLAR
subdata=data["Perihelia"]
axs[1].plot(subdata[1:,0],subdata[1:,1],'r+-')
subdata=data["Aphelia"]
axs[1].plot(subdata[1:,0],subdata[1:,1],'b+-')

# ############################################################
# DECORATION
# ############################################################
i=0
for ax in axs:
    ax.grid()
    ax.axvline(0.0,color='r')
    ax.set_xlim((tmin,tmax))
    if i>0:
        ax.set_xticklabels([])
        yt=ax.get_yticks()
        ax.set_yticks(yt[1:])
    i+=1

# ############################################################
# SAVING FIGURE
# ############################################################
fig.savefig(fname+".png")
