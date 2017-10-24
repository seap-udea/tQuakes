# ############################################################
# IMPORT TOOLS
# ############################################################
from tquakes import *
from matplotlib import use
use('Agg')
import matplotlib.pyplot as plt
confile=prepareScript()
conf=execfile(confile)
quake=loadConf("quake.conf")

# ############################################################
# CONNECT TO DATABASE
# ############################################################
connection=connectDatabase()
tQuakes,connection=loadDatabase()
db=connection.cursor()

DT=CONF.TIMEWIDTH/2.0
# ############################################################
# ROUTINE
# ############################################################
def plotBoundaries(quakeid,component,plt):

    # ############################################################
    # ASTRONOMY EXTREMES 
    # ############################################################
    table=numpy.loadtxt("util/astronomy-extremes-1970_2030.data")
    astro=loadExtremesTable(EXTREMES,table)
    full=numpy.loadtxt("util/astronomy-fullmoons-1970_2030.data")

    # ############################################################
    # COMPONENT
    # ############################################################
    info=COMPONENTS_DICT[component]
    compnum=info[0]
    name=info[1]
    units=info[2]
    nc,np=numComponent(component)

    # ############################################################
    # QUAKE PROPERTIES
    # ############################################################
    quake=loadConf(DIRNAME+"/quake.conf")
    quakestr=quake2str(float(quake.qlat),
                       float(quake.qlon),
                       float(quake.qdepth),
                       float(quake.qjd))
    quakedb=tQuakes['Quakes']['rows'][quakeid]
    hmoon=float(quakedb["hmoon"])
    qjd=float(quakedb["qjd"])

    # PERIGEA
    ps=astro["Perigea"][1:,0]-qjd
    cond=(ps>-DT)*(ps<+DT)
    ps=ps[cond]

    # FULL MOONS
    pfs=full[:]-qjd
    cond=(pfs>-DT)*(pfs<+DT)
    pfs=pfs[cond]

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
    phase_dn=float(phtime[1])
    phtime=qphases[np+3+3].split(":")
    phase_fn=float(phtime[1])
    phtime=qphases[np+3+4].split(":")
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

    # SIGN OF PHASES
    psgn=PHASESGN[nc-1]

    # PEAKS SEMIDIURNAL
    if psgn>0:tb=tMb
    else:tb=tmb

    npeaks=len(tb)
    ipeaks=numpy.arange(npeaks)
    ipeak=ipeaks[tb<0][-1]
    tminb=tb[ipeak];tmaxb=tb[ipeak+1]

    # PEAKS DIURNAL
    if psgn>0:tp=tMb
    else:tp=tmb
    dprev=hmoon/MOONRATE
    tshift=tp+dprev
    isorts=abs(tshift).argsort()
    iso=0;dt=-1
    while dt<0:
        iprev=isorts[iso]
        dt=-tp[iprev]
        iso+=1
    ipeak=iprev
    tmind=tp[ipeak];tmaxd=tp[ipeak+2]

    # CREATE ARRAY OF MINIMUM AND MAXIMA
    tMd=numpy.concatenate((tMb[ipeak::-2],tMb[ipeak::+2]))
    sMd=numpy.concatenate((sMb[ipeak::-2],sMb[ipeak::+2]))

    tmd=numpy.concatenate((tmb[ipeak::-2],tmb[ipeak::+2]))
    smd=numpy.concatenate((smb[ipeak::-2],smb[ipeak::+2]))

    # PEAKS FORTNIGHTLY
    npeaks=len(tMF)
    ipeaks=numpy.arange(npeaks)
    ipeak=ipeaks[tMF<0][-1]
    tminf=tMF[ipeak];tmaxf=tMF[ipeak+1]

    # PEAKS MONTHLY
    if psgn>0:tcF=tMF
    else:tcF=tmf
    cond=(tcF>-DT)*(tcF<+DT)
    tpF=tcF[cond]
    
    #DETECT INITIAL INDEX OF PEAK
    ipeaks=numpy.arange(len(tcF))
    cond=tcF<=-DT
    inipeak=ipeaks[cond][-1]+1

    numpeak=len(tpF)
    ds=[]
    for tf in tpF:ds+=[min(abs(ps-tf))]

    iM=numpy.array(ds).argsort()[0]
    ipeaks=numpy.arange(npeaks)
    ipeak=ipeaks[tpF<0][-1]
    if abs(ipeak-iM)%2!=0:ipeak-=1
    if (ipeak+2)>=numpeak:npeak=ipeak-2
    else:npeak=ipeak+2
    tminm=tcF[inipeak+ipeak];tmaxm=tcF[inipeak+ipeak+2]

    # ############################################################
    # ASTRONOMY TIMES
    # ############################################################
    table=numpy.loadtxt("astronomy-extremes-1970_2030.data")
    astro=loadExtremesTable(EXTREMES,table)
    qjd=float(quake.qjd)
    
    # GET THE PERIGEA POSITION
    ps=astro["Perigea"][1:,0]
    ps=ps-qjd
    cond=(ps>-CONF.TIMEWIDTH)*(ps<+CONF.TIMEWIDTH)

    # PLOT THE PERIGEA
    for tp in ps[cond]:ax.axvline(tp,color='k',zorder=-1000,alpha=0.1,linewidth=3)
    
    # GET THE FULL MOONS
    pfs=full[:]-qjd
    cond=(pfs>-CONF.TIMEWIDTH)*(pfs<+CONF.TIMEWIDTH)
    pfs=pfs[cond]

    # PLOT THE FULL MOONS
    for tp in pfs:ax.axvline(tp,color='b',ls='dashed',zorder=-1000,alpha=0.1,linewidth=3)

    # ############################################################
    # DECORATION
    # ############################################################
    ax.set_xlim((-CONF.TIMEWIDTH/1,+CONF.TIMEWIDTH/1))
    ax.set_ylim((smin,smax+(smax-smin)/2))

    ax.set_title(r"%s for quake %s"%(name,quakeid))
    ax.set_xlabel(r"Days to /since earthquake")
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
        
        axp.plot(tMd,sMd,marker='s',markersize=5,markerfacecolor='none',markeredgecolor='b',linewidth=0,
                 label='Diurnal:%.4f'%float(phase_dn))
        axp.plot(tmd,smd,marker='s',markersize=5,markerfacecolor='none',markeredgecolor='b',linewidth=0)

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
    axi.axvspan(tmind,tmaxd,color='k',alpha=0.2)
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
            rotation=90,fontsize=8,color='k',alpha=0.2,
            transform=ax.transAxes)
    
    figname="%s/%s.png"%(DIRNAME,BASENAME)
    print "Saving figure ",figname
    fig.savefig(figname)
    return fig

# ############################################################
# PLOT
# ############################################################
fig=plotBoundaries(quake.quakeid,component,plt)

# ############################################################
# SAVING FIGURE
# ############################################################
saveFigure(confile,fig)
