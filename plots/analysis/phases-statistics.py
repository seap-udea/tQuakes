from tquakes import *
from matplotlib import use
use('Agg')
import matplotlib.pyplot as plt

# ############################################################
# CONNECT TO DATABASE
# ############################################################
connection=connectDatabase()
db=connection.cursor()

# ############################################################
# PHASE TO ANALYSE
# ############################################################
component='vd'
info=COMPONENTS_DICT[component]
compnum=info[0]
name=info[1]
nc,np=numComponent(component)
# Fourier: 1-Semidiurnal, 2-Diurnal, 3-Fortnightly, 4-Monthly
# Boundary: 5-Semidiurnal, 6-Fortnightly, 7-Monthly
phase=6

# ############################################################
# PERFORM QUERY
# ############################################################
# and quakeid='UTFZQRX'
sql="select SUBSTRING_INDEX(SUBSTRING_INDEX(qphases,';',%d),';',-1) from Quakes where qphases<>''"%(np+phase)
results=mysqlArray(sql,db)
phases=numpy.array([float(phase[0].replace(" ","")) for phase in results])
nphases=len(phases)
nbins=50

# ############################################################
# PREPARE FIGURE
# ############################################################
fig=plt.figure()
ax=plt.gca()

# ############################################################
# PLOT HISTOGRAM
# ############################################################
h,bins=numpy.histogram(phases,nbins)
xs=(bins[:-1]+bins[1:])/2
dh=numpy.sqrt(h)

ax.hist(phases,nbins,facecolor='blue',alpha=0.2)
ax.errorbar(xs,h,yerr=dh,linestyle='None',color='r')

# ############################################################
# DECORATION
# ############################################################
# ax.set_xlim((0,360))
ax.set_xlim((0,1))
ax.axvline(180.0,color='k')
ax.set_xlabel("Phase Semidiurnal Component")
ax.set_ylabel("Number of Earthquakes")

# ############################################################
# SAVE FIGURE
# ############################################################
figname="%s/%s.png"%(DIRNAME,BASENAME)
print "Saving figure ",figname
fig.savefig(figname)
