# ############################################################
# IMPORT TOOLS
# ############################################################
from tquakes import *
from matplotlib import use
use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap as map,shiftgrid
import matplotlib.patches as patches
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
fig,axs=subPlots(plt,[1,1,1,1],l=0.12,dh=[0.02,0.02,0.005])
ax=axs[-1]

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
jd1=date2jd(datetime.datetime.strptime(dateini,"%Y-%m-%d %H:%M:%S"))
jd2=date2jd(datetime.datetime.strptime(dateend,"%Y-%m-%d %H:%M:%S"))

search="""where qphases<>'' and 
qdeptherr/1<qdepth/1 and
Ml+0>=%.2f AND Ml+0<%.2f and 
qdepth+0>=%.2f and qdepth+0<%.2f and 
qlat+0>=%.2f and qlat+0<%.2f and 
qlon+0>=%.2f and qlon+0<%.2f and
qjd+0>=%.5f and qjd+0<=%.5f and
(cluster1='0' or cluster1 like '-%%') and
astatus+0=4 
limit %d"""%(Mlmin,Mlmax,
             depthmin,depthmax,
             latb,latu,
             lonl,lonr,
             jd1,jd2,
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

"""
i=0
f=open("nocalc.sql","w")
for qid in qids:
    if phs[i]>1:
        print qid,phs[i]
        f.write("update Quakes set astatus='0' where quakeid='%s';\n"%qid)
    i+=1
f.close()
exit(0)
"""

if random:
    phs=360*numpy.random.random(nquakes)
else:
    if 'fourier' not in phase:
        phs=phs[phs<=1]
        nquakes=len(phs)
        phs*=360

print "Number of earthquakes with true phases: ",nquakes

# ############################################################
# HISTOGRAM
# ############################################################
nbins=int(360.0/dphase)
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
logp,dlogp=schusterValue(phs*DEG,
                         qbootstrap=qbootstrap,
                         facbootstrap=facbootstrap,
                         bootcycles=nsamples)
p=numpy.exp(logp)
print "Schuster p-value: log(p) = %.2f +/- %.2f, p = %.2f%%"%(logp,dlogp,p*100)

# ############################################################
# PHASES SCATTER PLOT
# ############################################################
scatter=0.2
axs[-2].plot(phs,
            numpy.cos(phs*DEG)+scatter*(2*numpy.random.random(len(phs))-1),
            'ko',markersize=1,
            markeredgecolor='none',alpha=0.2)
thetas=numpy.linspace(0.0,360.0,100)
axs[-2].plot(thetas,numpy.cos(thetas*DEG)+scatter,'k-')
axs[-2].plot(thetas,numpy.cos(thetas*DEG)-scatter,'k-')

# ############################################################
# MAP
# ############################################################
m=scatterMap(axs[-3],phases[:,QLAT],phases[:,QLON],
             resolution='c',
             merdict=dict(labels=[False,False,False,True]),
             limits=[center[0],center[1],dlat,dlon],
             color='k',marker='o',linestyle='none',
             markeredgecolor='none',markersize=1,zorder=10)

# ############################################################
# SCHUSTER PLOT
# ############################################################
axs[-4].axis('off')

xs,ys=schusterSteps(phs*DEG,
                    qbootstrap=qbootstrap,
                    facbootstrap=facbootstrap)
ds=numpy.sqrt(xs[-1]**2+ys[-1]**2)
phtrend=numpy.arctan2(ys[-1],xs[-1])*RAD

axs[-4].plot(xs,ys,'k-')
axs[-4].plot([xs[0],xs[-1]],[ys[0],ys[-1]],'b-')

ngrid=5
dd=int(ds/5)
dini=dd
dend=int(ds)
dgrid=numpy.arange(dini,dend+dd,dd)
for d in dgrid:
    circle=patches.Circle((0,0),d,
                          fc='none',ec='k')
    axs[-4].add_patch(circle)

for d in dgrid:
    axs[-4].text(d,0.0,r"$%.2f$"%((1.0*d**2)/nquakes),
                 bbox=dict(fc='w',ec='none'),fontsize=8,
                 horizontalalignment='center')

axs[-4].text(0.0,-ds/2,r"Trend phase = $%.1f^o$"%phtrend,
             bbox=dict(fc='w',ec='none'),fontsize=10,
             horizontalalignment='center')

bbox=ax.get_window_extent()
w,h=bbox.width,bbox.height
fac=(1.0*w)/h
axs[-4].set_xlim((-fac*ds,fac*ds))
axs[-4].set_ylim((-ds,ds))
axs[-4].set_title("Schuster Walk",position=(0.5,-0.08))

# ############################################################
# DECORATION
# ############################################################
axs[-2].set_xlim((0.0,360.0))
axs[-2].set_ylim((-1.0-scatter,1.0+scatter))

hmean=1.0/360.0

axs[-2].set_xlabel("Phase (degrees)",fontsize=14)
ax.set_ylabel("Frequency",fontsize=14)
ax.set_title("%s, %s"%(compname,phasename))
if p<0.05:color="b"
else:color="r"
ax.text(0.95,0.95,r"""p-value = %.3f%%, $\log(p)$ = %.2f $\pm$ %.2f
Fit parameters: Amplitude/$h_{\rm mean}$ = %.3f, Phase = %.1f"""%\
        (p*100,logp,dlogp,abs(pars[1])/hmean,numpy.mod(pars[2]*RAD,360)),
        horizontalalignment='right',verticalalignment='top',
        fontsize=14,color=color,
        transform=ax.transAxes)

axs[-2].text(0.5,0.95,"N = %d\nlat,lon = %.2f, %.2f\n$\Delta$(lat,lon) = %.2f, %.2f\n$M_l$$\in$ [%.2f,%.2f)\nDepth$\in$[%.2f,%.2f) km\nDate = (%s,%s)"%\
            (nquakes,
             center[0],center[1],
             dlat,dlon,
             Mlmin,Mlmax,
             depthmin,depthmax,
             dateini,dateend
         ),
            horizontalalignment="center",
            verticalalignment="top",
            zorder=50,bbox=dict(fc='w',pad=20),
            fontsize=10,
            transform=axs[-2].transAxes)

ax.set_xlim((0,360))
ax.set_ylim((0.5*hmean,1.5*hmean))

ax.set_xticklabels([])

# ############################################################
# SAVING FIGURE
# ############################################################
saveFigure(confile,fig)
