# ############################################################
# IMPORT TOOLS
# ############################################################
from tquakes import *
from matplotlib import use
use('Agg')
import matplotlib.pyplot as plt
from scipy.optimize import leastsq
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
fig,axs=subPlots(plt,[1],l=0.12)
ax=axs[0]

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
latb=center[0]-dlat/2;latu=center[0]+dlat/2
lonl=center[1]-dlon/2;lonr=center[1]+dlon/2

search="""where qphases<>'' and 
qdeptherr/1<qdepth/1 and
Ml+0>=%.1f AND Ml+0<%.1f and 
qdepth+0>=%.2f and qdepth+0<%.2f and 
qlat+0>=%.2f and qlat+0<%.2f and 
qlon+0>=%.2f and qlon+0<%.2f and
(cluster1='0' or cluster1 like '-%%') 
limit %d"""%(Mlmin,Mlmax,
             depthmin,depthmax,
             latb,latu,
             lonl,lonr,
             limit)

# COLUMNS: 
# 0:qjd,1:qlat,2:qlon,3:qdepth,4:Mlq
# Fourier: 5:sd, 6:dn, 7:fn, 8:mn
# Boundaries: 9:sd, 10:fn, 11:mn
qids,phases=getPhases(search,component,db)
nquakes=phases.shape[0]
print "Search:",search
print "Number of quakes found: ",nquakes
phs=phases[:,4+phasenum]
if 'fourier' not in phase:phs*=360

# ############################################################
# HISTOGRAM
# ############################################################
nbins=int(360.0/10)
h,bins=numpy.histogram(phs,nbins,normed=True)
xs=(bins[:-1]+bins[1:])/2
dh=numpy.sqrt(h)

hmax=(h+dh).max()
hmin=(h-dh).min()
hmean=h.mean()

ax.hist(phs,nbins,facecolor='blue',normed=True,alpha=0.2)
# ax.errorbar(xs,h,yerr=dh,linestyle='None',color='r')

# ############################################################
# FIT
# ############################################################
pars,n=leastsq(chisq,[1.0,1.0,1.0],args=(pOsc,xs*DEG,h,dh))
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
hmean=1.0/360.0
ax.set_xlabel("Phase (degrees)",fontsize=14)
ax.set_ylabel("Frequency",fontsize=14)
ax.set_title("%s, %s"%(compname,phasename))
if p<0.05:color="b"
else:color="r"
ax.text(0.95,0.95,r"""p-value = %.3f%%, $\log(p)$ = %.2f $\pm$ %.2f
Fit parameters: Amplitude/$h_{\rm mean}$ = %.3f, Phase = %.1f"""%(p*100,logp,dlogp,pars[1]/hmean,numpy.mod(pars[2]*RAD,360)),
        horizontalalignment='right',verticalalignment='top',
        fontsize=14,color=color,
        transform=ax.transAxes)

axs[0].text(0.95,0.08,"N = %d\nlat,lon = %.2f, %.2f\n$\Delta$(lat,lon) = %.2f, %.2f\n$M_l$$\in$ [%.2f,%.2f)\nDepth$\in$[%.2f,%.2f) km"%\
            (nquakes,
             center[0],center[1],
             dlat,dlon,
             Mlmin,Mlmax,
             depthmin,depthmax,
         ),
            horizontalalignment="right",
            verticalalignment="bottom",
            zorder=50,bbox=dict(fc='w',pad=20),
            transform=axs[0].transAxes)

ax.set_xlim((0,360))
ax.set_ylim((0.5*hmean,1.5*hmean))

# ############################################################
# SAVING FIGURE
# ############################################################
saveFigure(confile,fig)
