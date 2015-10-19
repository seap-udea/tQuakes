from tquakes import *
from matplotlib import use
use('Agg')
import matplotlib.pyplot as plt
quakeid=DIRNAME.split("/")[-1]

# ############################################################
# CONNECT TO DATABASE
# ############################################################
connection=connectDatabase()
db=connection.cursor()
quake=quakeProperties(quakeid,db)

# ############################################################
# PREPARE FIGURE
# ############################################################
fig=plt.figure()
ax=plt.gca()

# ############################################################
# CREATE FIGURE
# ############################################################
qsignal=quake.qsignal.split(";")
value=float(qsignal[2])

signal=numpy.loadtxt(DIRNAME+"/%s.data"%quakeid)
t=signal[:,0]-float(quake.qjd)
s=signal[:,3]

ax.plot(t,s)
ax.plot([0],[value],marker='o',color='r',markersize=10,markeredgecolor="None")
ax.axvline(0,color='r')

# ############################################################
# DECORATION
# ############################################################
ax.set_xlim((-5,5))

ax.set_title(r"Vertical strain for quake %s"%quakeid)
ax.set_xlabel(r"Days to/since earthquake")
ax.set_ylabel(r"Horizontal strain ($\times10^{-9}$)")
ax.text(0.02,0.95,r"VS = $%.1f\times 10^{-9}$"%value,transform=ax.transAxes)

# ############################################################
# SAVE FIGURE
# ############################################################
figname="%s/%s.png"%(DIRNAME,BASENAME)
print "Saving figure ",figname
fig.savefig(figname)
