# ############################################################
# IMPORT CONFIGURATION
# ############################################################
from matplotlib import use
use('Agg')
import matplotlib.pyplot as plt
execfile("phases-schuster.conf")

# ############################################################
# CONNECT TO DATABASE
# ############################################################
connection=connectDatabase()
db=connection.cursor()

# ############################################################
# COMPONENT AND PHASE INFORMATION
# ############################################################
info=COMPONENTS_DICT[component]
compnum=info[0]
compname=info[1]

info=PHASES_DICT[phase]
phasenum=info[0]
phasename=info[1]

# ############################################################
# GET PHASES
# ############################################################
# COLUMNS: 
# 0:qjd,1:qlat,2:qlon,3:qdepth,4:Ml
# Fourier: 5:sd, 6:dn, 7:fn, 8:mn
# Boundaries: 9:sd, 10:fn, 11:mn
qids,phases=getPhases(component,db,criteria=criteria)
nquakes=phases.shape[0]
print "Criterium: ",criteria
print "Number of quakes: ",nquakes

phs=phases[:,4+phasenum]
if 'fourier' not in phase:phs*=360

# ############################################################
# FIGURE
# ############################################################
fig=plt.figure()
ax=fig.gca()

# ############################################################
# HISTOGRAM
# ############################################################
# SEMIDIURNAL PHASE

h,bins=numpy.histogram(phs,nbins)
xs=(bins[:-1]+bins[1:])/2
dh=numpy.sqrt(h)
hmax=h.max()

ax.hist(phs,nbins,facecolor='blue',alpha=0.2)
ax.errorbar(xs,h,yerr=dh,linestyle='None',color='r')

# ############################################################
# SCHUSTER VALUE
# ############################################################
logp=schusterValue(phs*DEG)
p=numpy.exp(logp)
print "Schuster p-value: log(p) = %.2f, p = %.2f%%"%(logp,p*100)

# ############################################################
# DECORATION
# ############################################################
ax.set_xlabel("Phase (degrees)",fontsize=14)
ax.set_ylabel("Number of eqrthquakes",fontsize=14)
ax.set_title("%s, %s, %d earthquakes"%(compname,phasename,nquakes))
ax.text(0.95,0.95,"p-value = %.3f%% ($\log(p)$ = %.2f)"%(p*100,logp),
        horizontalalignment='right',verticalalignment='top',
        fontsize=14,
        transform=ax.transAxes)
ax.text(0.95,0.88,"Criteria: %s"%(criteria[0:50]),
        horizontalalignment='right',verticalalignment='top',
        fontsize=12,
        transform=ax.transAxes)

ax.set_xlim((0,360))
ax.set_ylim((0,1.5*hmax))

# ############################################################
# HISTOGRAM
# ############################################################
figname="%s/%s.png"%(DIRNAME,BASENAME)
print "Saving figure ",figname
fig.savefig(figname)
