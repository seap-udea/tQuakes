# ############################################################
# IMPORT TOOLS
# ############################################################
from tquakes import *
from matplotlib import use
use('Agg')
import matplotlib.pyplot as plt
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
fig,axs=subPlots(plt,[1,2],b=0.15,dh=0.02)
ax=axs[1]

# ############################################################
# GET PHASES
# ############################################################
latb=center[0]-dlat/2;latu=center[0]+dlat/2
lonl=center[1]-dlon/2;lonr=center[1]+dlon/2

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
Ml+0>=%.2f AND Ml+0<%.2f and 
qdepth+0>=%.2f and qdepth+0<%.2f and 
qlat+0>=%.2f and qlat+0<%.2f and 
qlon+0>=%.2f and qlon+0<%.2f and
(cluster1='0' or cluster1 like '-%%') 
limit %d"""%(Mlmin,Mlmax,
             depthmin,depthmax,
             latb,latu,
             lonl,lonr,
             limit)

qids,quakes=getPhases(search,component,db)
nquakes=len(qids)
if random:phases=360*numpy.random.random(nquakes)
else:phases=360*quakes[:,4+phasenum]

# ############################################################
# GLOBAL
# ############################################################
logpt,dlogpt=schusterValue(phases*DEG,
                           qbootstrap=qbootstrap,
                           facbootstrap=facbootstrap,
                           bootcycles=nsamples)

print "Global p-value: log(p) = %.2f +/- %.2f"%(logpt,dlogpt)

# ############################################################
# FILTER PER TIME
# ############################################################
times=quakes[:,0]
itimes=times.argsort()

tini=times[itimes[0]]
tend=times[itimes[-1]]
deltat=tend-tini

vvv=1
ncut=2000
#qbootstrap=1
#ftype="number"
ftype="time"

if ftype=="time":
    # TIMES
    j=1
    nphases=[]
    ts=[]
    tbs=[]
    tphases=[]
    logps=[]
    dlogps=[]
    tlef=tini
    for i in xrange(nquakes):
        t=times[itimes[i]]
        if t<tini+dt:
            tphases+=[phases[itimes[i]]]
        else:
            nphases+=[len(tphases)]
            ts+=[tini+dt/2]
            logp,dlogp=schusterValue(numpy.array(tphases)*DEG,
                                     qbootstrap=qbootstrap,
                                     facbootstrap=facbootstrap,
                                     bootcycles=nsamples)
            logps+=[logp]
            dlogps+=[dlogp]
            d1=jd2gcal(tlef,0);
            h1=d2s(d1[3]*24)
            t1="%d-%d-%d %d:%d:%d"%\
                (d1[0],d1[1],d1[2],h1[0],h1[1],h1[2])
            d2=jd2gcal(t,0)
            h2=d2s(d2[3]*24)
            t2="%d-%d-%d %d:%d:%d"%\
                (d2[0],d2[1],d2[2],h2[0],h2[1],h2[2])
            if vvv:
                print "Window %d, t = (%s,%s), dt = %.1f, logp = %.2f +/- %.2f, %d quakes..."%\
                    (j,t1,t2,t-tlef,logp,dlogp,len(tphases))
            tbs+=[tlef]
            tlef=t
            tbs+=[tlef]
            j+=1
            tini=t
            tphases=[phases[itimes[i]]]
    j-=1

elif ftype=="number":
    # NUMBER
    j=1
    ts=[]
    tbs=[]
    tphases=[]
    nphases=[]
    logps=[]
    dlogps=[]
    tlef=tini
    for i in xrange(nquakes):
        t=times[itimes[i]]
        if len(tphases)<ncut:
            tphases+=[phases[itimes[i]]]
        else:
            twin=(t+tlef)/2
            logp,dlogp=schusterValue(numpy.array(tphases)*DEG,
                                     qbootstrap=qbootstrap,
                                     facbootstrap=facbootstrap,
                                     bootcycles=nsamples)
            logps+=[logp]
            dlogps+=[dlogp]
            ts+=[twin]
            nphases+=[len(tphases)]
            d1=jd2gcal(tlef,0);
            h1=d2s(d1[3]*24)
            t1="%d-%d-%d %d:%d:%d"%\
                (d1[0],d1[1],d1[2],h1[0],h1[1],h1[2])
            d2=jd2gcal(t,0)
            h2=d2s(d2[3]*24)
            t2="%d-%d-%d %d:%d:%d"%\
                (d2[0],d2[1],d2[2],h2[0],h2[1],h2[2])
            if vvv:
                print "Window %d, t = (%s,%s), dt = %.1f, logp = %.2f +/- %.2f, %d quakes..."%\
                    (j,t1,t2,t-tlef,logp,dlogp,len(tphases))
            tbs+=[tlef]
            tlef=t
            tbs+=[tlef]
            tphases=[phases[itimes[i]]]
            j+=1

    #LAST WINDOW 
    twin=(t+tlef)/2
    ts+=[twin]
    tbs+=[tlef]
    nphases+=[len(tphases)]
    logp,dlogp=schusterValue(numpy.array(tphases)*DEG,
                             qbootstrap=qbootstrap,
                             facbootstrap=facbootstrap,
                             bootcycles=nsamples)
    logps+=[logp]
    dlogps+=[dlogp]
    if vvv or True:
        print "Window %d, t = (%.1f,%.1f), dt = %.1f, logp = %.2f +/- %.2f, %d quakes..."%\
            (j,tlef,t,t-tini,logp,dlogp,len(tphases))
    print "Done."
    print nphases

# ############################################################
# SELECTION
# ############################################################
jini=0
jend=j
rang="%d:%d"%(jini,jend);rangb="%d:%d"%(jini,2*jend)
ts=eval("ts[%s]"%rang)
logps=eval("logps[%s]"%rang)
dlogps=eval("dlogps[%s]"%rang)
tbs=eval("tbs[%s]"%rangb)
j=len(ts)

# ############################################################
# PLOTS
# ############################################################
ax.plot(ts,logps,'ko')
ax.errorbar(ts,logps,yerr=dlogps,linestyle='none',color='k')

scatter=0.1
axs[0].plot(quakes[:,QJD]-times.min(),
            quakes[:,ML]+scatter*(2*numpy.random.random(nquakes)-1),
            'ko',markersize=1)

# ############################################################
# DECORATION 1
# ############################################################
ax.set_xticks(numpy.unique(tbs))
axs[0].set_xticks(numpy.unique(tbs)-times.min())

for i in xrange(j):
    if i>=0:
        sgn=+1
        hal="left"
    if i==j-1:
        sgn=-1
        hal="right"
    ax.text(ts[i]+sgn*deltat/100,logps[i],"%d,%d"%(i+1,nphases[i]),
                horizontalalignment=hal,
                verticalalignment="center",
                rotation=90,fontsize=8)
    ax.text(ts[i],0,"%d"%(i+1),
            horizontalalignment="center",
            verticalalignment="bottom")

xts=axs[1].get_xticks()
xtl=[]
for xt in xts:
    date=jd2gcal(xt,0)
    xtl+=["%d-%d-%d"%(date[0],date[1],date[2])]
axs[0].set_xticklabels(xtl,rotation=35,
                       fontsize=10,horizontalalignment='right')
axs[1].set_xticklabels([])

# ############################################################
# DECORATION 2
# ############################################################
axs[0].set_xlim((min(tbs)-times.min(),max(tbs)-times.min()))
axs[0].set_ylim((Mlmin-scatter,Mlmax+scatter))
axs[0].set_ylabel("$M_l$",fontsize=16)

ymin,ymax=ax.get_ylim()
ax.set_ylim((ymin,0.0))
ax.set_xlim((min(tbs),max(tbs)))
ax.axhspan(ymin,-3.0,color='green',alpha=0.2)
ax.axhspan(-3.0,0.0,color='red',alpha=0.2)
ax.set_ylabel(r'$\log(p)$',fontsize=16)
ax.set_title("p-value time-windows",position=(0.5,1.05))

ax.grid()
axs[0].grid(color='r',linestyle='-',zorder=10)

# ############################################################
# SAVING FIGURE
# ############################################################
saveFigure(confile,fig)

