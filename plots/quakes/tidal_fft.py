from tquakes import *
from matplotlib import use
use('Agg')
import matplotlib.pyplot as plt

def plot(quakeid,component):
    # ############################################################
    # COMPONENT
    # ############################################################
    info=COMPONENTS_DICT[component]
    compnum=info[0]
    name=info[1]
    units=info[2]
    nc,np=numComponent(component)
    
    # ############################################################
    # CONNECT TO DATABASE
    # ############################################################
    connection=connectDatabase()
    db=connection.cursor()
    #quake=quakeProperties(quakeid,db)
    quake=loadConf(DIRNAME+"/quake.conf")

    # ############################################################
    # PREPARE FIGURE
    # ############################################################
    fig=plt.figure()
    ax=plt.gca()

    # ############################################################
    # CREATE FIGURE
    # ############################################################ 
    qsignal=quake.qsignal.split(";")
    value=float(qsignal[nc-1])
    qphases=quake.qsignal.split(";")

    qphases=quake.qphases.split(";")
    phase_sd=float(qphases[np-1+1])
    phase_dn=float(qphases[np-1+2])
    phase_fn=float(qphases[np-1+3])
    phase_mn=float(qphases[np-1+4])

    t,ft=loadComplextxt(DIRNAME+"/%s%d-fft.data"%(quakeid,compnum))
    signal=numpy.loadtxt(DIRNAME+"/%s.data"%quakeid)
    t=signal[:,0]-signal[0,0]
    s=signal[:,nc]
    smin=s.min();smax=s.max()

    dt=float(quake.qjd)-signal[0,0]
    T=t[-1]
    N=len(t)
    smean=s.mean()
    smax=numpy.abs(s-smean).max()

    # SIGNAL
    ax.plot(t-dt,s)
    ax.axvline(0,color='r')

    # THEORETICAL SIGNAL
    P=0.5
    w=2*PI/P
    k=omega2k(w,T,N)
    stsd=numpy.array([signal_teo(tval,ft,T,N,k) for tval in t])
    stsdmean=stsd.mean()
    stsdmax=numpy.abs(stsd-stsdmean).max()

    P=1.0
    w=2*PI/P
    k=omega2k(w,T,N)
    stdn=numpy.array([signal_teo(tval,ft,T,N,k) for tval in t])
    stdnmean=stdn.mean()
    stdnmax=numpy.abs(stdn-stdnmean).max()

    P=13.8
    w=2*PI/P
    k=omega2k(w,T,N)
    stfn=numpy.array([signal_teo(tval,ft,T,N,k) for tval in t])
    stfnmean=stfn.mean()
    stfnmax=numpy.abs(stfn-stfnmean).max()

    P=27.6
    w=2*PI/P
    k=omega2k(w,T,N)
    stmn=numpy.array([signal_teo(tval,ft,T,N,k) for tval in t])
    stmnmean=stmn.mean()
    stmnmax=numpy.abs(stmn-stmnmean).max()

    # ############################################################
    # DECORATION
    # ############################################################
    ax.set_xlim((-CONF.TIMEWIDTH,+CONF.TIMEWIDTH))
    ax.set_ylim((smin,smax+(smax-smin)/2))

    ax.set_title(r"%s (fourier analysis) for quake %s"%(name,quakeid))
    ax.set_xlabel(r"Days to/since earthquake")
    ax.set_ylabel(r"%s (%s)"%(name,units))

    # ############################################################
    # INSET PANEL
    # ############################################################
    axi=fig.add_axes([0.172,0.65,0.68,0.22])
    axi.plot(t-dt,s)
    axi.plot([0],[value],marker='o',color='r',markersize=10,markeredgecolor="None")
    axi.axvline(0,color='r')
    axi.set_xlim((-5,5))
    axi.set_yticklabels([])

    for axp in ax,axi:
        axp.plot(t-dt,(stfn-stfnmean)*smax/stfnmax+smean,'k--',
                 label='Fortnightly: %.2f'%phase_fn,alpha=0.7,zorder=-10)
        axp.plot(t-dt,(stmn-stmnmean)*smax/stmnmax+smean,'k:',
                 label='Monthly: %.2f'%phase_mn,alpha=0.9,zorder=-10)
        
    axi.plot(t-dt,(stsd-stsdmean)*smax/stsdmax+smean,'k-',
             label='Semi-diurnal',alpha=0.5,zorder=-10)
    axi.plot(t-dt,(stdn-stdnmean)*smax/stdnmax+smean,'k-.',
             label='Diurnal',alpha=0.5,zorder=-10)

    ax.plot([],[],'k-',label='Semi-diurnal: %.2f'%phase_sd)
    ax.plot([],[],'k-.',label='Diurnal: %.2f'%phase_dn)
    ax.legend(loc="lower right",prop=dict(size=10))

    # ############################################################
    # SAVE FIGURE
    # ############################################################
    figname="%s/%s.png"%(DIRNAME,BASENAME)
    print "Saving figure ",figname
    fig.savefig(figname)
