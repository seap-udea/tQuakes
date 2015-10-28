from tquakes import *
from scipy import signal
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
    quake=quakeProperties(quakeid,db)
    quakestr=quake.quakestr
    quake=loadConf(DIRNAME+"/quake.conf")

    # ############################################################
    # PREPARE FIGURE
    # ############################################################
    fig=plt.figure()
    ax=plt.gca()

    # ############################################################
    # CREATE FIGURE
    # ############################################################
    # GET SIGNAL VALUE
    qsignal=quake.qsignal.split(";")
    value=float(qsignal[nc-1])

    # GET PHASES
    qphases=quake.qphases.split(";")
    phtime=qphases[np+3+1].split(":")
    phase_sd=float(phtime[1])
    phtime=qphases[np+3+2].split(":")
    phase_fn=float(phtime[1])
    phtime=qphases[np+3+3].split(":")
    phase_mn=float(phtime[1])

    # READ SIGNAL
    sign=numpy.loadtxt(DIRNAME+"/%s.data"%quakeid)
    t=sign[:,0]-float(quake.qjd)
    s=sign[:,nc]
    smin=s.min();smax=s.max()

    # ==============================
    # FIND MAXIMA AND MINIMA
    # ==============================
    # SEMIDIURNAL LEVEL PEAKS
    tmb,smb,tMb,sMb=signalBoundary(t,s)

    # SMOOTH MAXIMA & MINIMA
    b,a=signal.butter(8,0.125)
    sMs=signal.filtfilt(b,a,sMb,padlen=100)
    tMs=tMb
    b,a=signal.butter(8,0.125)
    sms=signal.filtfilt(b,a,smb,padlen=100)
    tms=tmb

    # FORTNIGHTLY LEVEL PEAKS (MAXIMA)
    tmF,smF,tMF,sMF=signalBoundary(tMs,sMs)
    # FORTNIGHTLY LEVEL PEAKS (MINIMA)
    tmf,smf,tMf,sMf=signalBoundary(tms,sms)

    # PEAKS SEMIDIURNAL
    npeaks=len(tMb)
    ipeaks=numpy.arange(npeaks)
    ipeak=ipeaks[tMb<0][-1]
    tminb=tMb[ipeak];tmaxb=tMb[ipeak+1]

    # PEAKS FORTNIGHTLY
    npeaks=len(tMF)
    ipeaks=numpy.arange(npeaks)
    ipeak=ipeaks[tMF<0][-1]
    tminf=tMF[ipeak];tmaxf=tMF[ipeak+1]

    # PEAKS MONTHLY
    npeaks=len(tMF)
    ipeaks=numpy.arange(npeaks)
    ipeak=ipeaks[tMF<0][-1]
    dpeak1=sMF[ipeak]-smf[ipeak]
    dpeak2=sMF[ipeak+1]-smf[ipeak+1]
    if dpeak1<dpeak2:ipeak=ipeak+1
    tminm=tMF[ipeak];tmaxm=tMF[ipeak+2]

    # ############################################################
    # DECORATION
    # ############################################################
    ax.set_xlim((-CONF.TIMEWIDTH,+CONF.TIMEWIDTH))
    ax.set_ylim((smin,smax+(smax-smin)/2))

    ax.set_title(r"%s for quake %s"%(name,quakeid))
    ax.set_xlabel(r"Days to/since earthquake")
    ax.set_ylabel(r"%s (%s)"%(name,units))

    # ############################################################
    # INSET PANEL
    # ############################################################
    axi=fig.add_axes([0.172,0.65,0.68,0.22])

    for axp in ax,axi:

        # SIGNAL
        axp.plot(t,s,'k-',alpha=0.2)
        # TIME OF EARTHQUAKE
        axp.axvline(0,color='k')
        # VALUE OF SIGNAL
        axp.plot([0],[value],marker='s',color='w',
                 markersize=10,markeredgecolor='k')
        # MAXIMA AND MINIMA
        axp.plot(tMb,sMb,'ro',markersize=3,markeredgecolor='none',label='Semidiurnal:%.4f'%float(phase_sd))
        axp.plot(tmb,smb,'ro',markersize=3,markeredgecolor='none')
        # SOFTED SIGNAL
        axp.plot(tMs,sMs,'b-',)
        axp.plot(tms,sms,'b-',)
        # MAXIMA AND MINIMA LONGTERM
        axp.plot(tMF,sMF,'g^',markersize=8,markeredgecolor='none',label='Fortnightly:%.4f'%float(phase_fn))
        axp.plot(tmf,smf,'gv',markersize=8,markeredgecolor='none')
        # PEAKS
        axp.plot(tMF[ipeak::2],sMF[ipeak::2],'cs',markersize=10,markeredgecolor='none',label='Monthly:%.4f'%float(phase_mn))
        axp.plot(tMF[ipeak::-2],sMF[ipeak::-2],'cs',markersize=10,markeredgecolor='none')
        axp.plot(tmf[ipeak::2],smf[ipeak::2],'cs',markersize=10,markeredgecolor='none')
        axp.plot(tmf[ipeak::-2],smf[ipeak::-2],'cs',markersize=10,markeredgecolor='none')


    axi.axvspan(tminb,tmaxb,color='r',alpha=0.2)
    ax.axvspan(tminf,tmaxf,color='g',alpha=0.2)
    ax.axvspan(tminm,tmaxm,color='c',fill=False,hatch="/")

    ax.legend(loc='lower right',prop=dict(size=10))
    axi.set_xlim((-10,10))
    axi.set_yticklabels([])

    # ############################################################
    # SAVE FIGURE
    # ############################################################
    ax.text(1.02,0.5,quakestr,
            horizontalalignment='center',verticalalignment='center',
            rotation=90,fontsize=10,color='k',alpha=0.2,
            transform=ax.transAxes)
    
    figname="%s/%s.png"%(DIRNAME,BASENAME)
    print "Saving figure ",figname
    fig.savefig(figname)
