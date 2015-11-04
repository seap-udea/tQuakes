# ############################################################
# IMPORT CONFIGURATION
# ############################################################
from matplotlib import use
use('Agg')
import matplotlib.pyplot as plt
from tquakes import *
from scipy.optimize import leastsq
confile="%s.conf"%BASENAME
execfile(confile)

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
# 0:qjd,1:qlat,2:qlon,3:qdepth,4:Mlq
# Fourier: 5:sd, 6:dn, 7:fn, 8:mn
# Boundaries: 9:sd, 10:fn, 11:mn

latb=center[0]-dlat/2;latu=center[0]+dlat/2
lonl=center[1]-dlon/2;lonr=center[1]+dlon/2

search="""where qphases<>'' and 
qdepth>0 and Ml+0>2 and 
qdeptherr/1<qdepth/1 and
Ml+0<=%.1f and qdepth+0<=%.1f and 
(cluster1='0' or cluster1 like '-%%') and 
qlat+0>=%.2f and qlat+0<%.2f and qlon+0>=%.2f and qlon+0<%.2f 
limit %d"""%(Mlmax,depthmax,
             latb,
             latu,
             lonl,
             lonr,
             limit)
qids,phases=getPhases(search,component,db)
nquakes=phases.shape[0]
print "Search: ",search
print "Number of quakes: ",nquakes

print 4+phasenum
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

nbins=int(360/10)
h,bins=numpy.histogram(phs,nbins)
xs=(bins[:-1]+bins[1:])/2
dh=numpy.sqrt(h)

hmax=(h+dh).max()
hmin=(h-dh).min()
hmean=h.mean()

ax.hist(phs,nbins,facecolor='blue',alpha=0.2)
ax.errorbar(xs,h,yerr=dh,linestyle='None',color='r')

# ############################################################
# FIT
# ############################################################
pars,n=leastsq(chisq,[1.0,1.0,1.0],args=(pOsc,xs*DEG,h,dh))
print pars
ht=pOsc(xs*DEG,pars)
ax.plot(xs,ht,'r-')



# ############################################################
# SCHUSTER VALUE
# ############################################################
logp,dlogp=schusterValue(phs*DEG,qbootstrap=1)
p=numpy.exp(logp)
print "Schuster p-value: log(p) = %.2f +/- %.2f, p = %.2f%%"%(logp,dlogp,p*100)

# ############################################################
# DECORATION
# ############################################################
ax.set_xlabel("Phase (degrees)",fontsize=14)
ax.set_ylabel("Number of eqrthquakes",fontsize=14)
ax.set_title("%s, %s, %d earthquakes"%(compname,phasename,nquakes))
ax.text(0.95,0.95,"""p-value = %.3f%%, $\log(p)$ = %.2f $\pm$ %.2f
Fit parameters: Amplitude = %.1f, Phase = %.1f"""%(p*100,logp,dlogp,pars[1],numpy.mod(pars[2]*RAD,360)),
        horizontalalignment='right',verticalalignment='top',
        fontsize=14,
        transform=ax.transAxes)
"""
ax.text(0.95,0.88,"Criterium: %s"%(search[0:50]+"..."),
        horizontalalignment='right',verticalalignment='top',
        fontsize=12,
        transform=ax.transAxes)
"""

ax.set_xlim((0,360))
ax.set_ylim((hmean-100,hmean+100))
# ax.set_ylim((0,1.5*hmax))

# ############################################################
# HISTOGRAM
# ############################################################
md5sum=md5sumFile(confile)
figname="%s/%s__%s.png"%(DIRNAME,BASENAME,md5sum)
print "Saving figure ",figname
fig.savefig(figname)
