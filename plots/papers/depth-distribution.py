# ############################################################
# IMPORT TOOLS
# ############################################################
from tquakes import *
from matplotlib import use
use('Agg')
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from scipy import signal
confile=prepareScript()
conf=execfile(confile)

# ############################################################
# PREPARE PLOTTING REGION
# ############################################################
fig,axs=subPlots(plt,[1],l=0.15,b=0.15)
ax=axs[0]

# ############################################################
# CONNECT TO DATABASE
# ############################################################
connection=connectDatabase()
db=connection.cursor()

# ############################################################
# GET QUAKES
# ############################################################
limit="10000000"
allqids,allquakes=getQuakes(search+" limit "+limit,db)
nallquakes=len(allqids)
decsearch=search+"and (cluster1='0' or cluster1 like '-%')"
decqids,decquakes=getQuakes(decsearch+" limit "+limit,db)
ndecquakes=len(decqids)

# ############################################################
# CREATING HISTOGRAMS
# ############################################################
# DECLUSTERED EARTH QUAKES
depths=decquakes[:,3]
hd,bins=numpy.histogram(depths,ndecquakes/1000)
Q=numpy.cumsum(hd[::-1])[::-1]/(1.0*ndecquakes)
ds=(bins[:-1]+bins[1:])/2
Qp=Q[::];dsp=ds[::]
Qpi=interp1d(dsp,Qp)

# ############################################################
# DISTRIBUTION
# ############################################################
ax.plot(dsp,Qp,'k-',linewidth=3)
"""
axs[1].plot(Msp,Qp,'k-',label='%d earthquakes'%nallquakes,
            linewidth=3)
axs[1].plot(Mspd,Qpd,'b-',label='%d declustered earthquakes'%ndecquakes,
            linewidth=3)
"""

# ############################################################
# DECORATION
# ############################################################
ax.set_xscale("log")
ax.set_xlabel("Depth (km)")
ax.set_ylabel("N(>M)")

# ############################################################
# SAVING FIGURE
# ############################################################
saveFigure(confile,fig)

