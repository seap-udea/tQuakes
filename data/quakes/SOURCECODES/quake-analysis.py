from tquakes import *
from scipy import signal
# ##################################################
# ARGUMENTS
# ##################################################
quakeid=argv[1]
print "\tAnalysing quake '%s'..."%quakeid

# ##################################################
# CONFIGURATION
# ##################################################
conf=loadConf("configuration")
periods=[0.5,1.0,13.8,27.6]

# ASTRONOMY EXTREMES 
table=numpy.loadtxt("util/astronomy-extremes-1970_2030.data")
astro=loadExtremesTable(EXTREMES,table)

# ##################################################
# LOAD STATION INFORMATION
# ##################################################
station=loadConf(".stationrc")

# ##################################################
# ANALYSING
# ##################################################
quake=loadConf("quake.conf")

# LOAD DATA
data=numpy.loadtxt("%s.data"%quakeid)

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# INTERPOLATE SIGNAL
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
ic=1
times=data[:,0]
time=float(quake.qjd)
qjd=float(quake.qjd)
hmoon=float(quake.hmoon)

quake.qsignal=""
for component in COMPONENTS:
    sig=data[:,ic]
    value=numpy.interp(time,times,sig)
    quake.qsignal+="%.4lf;"%value
    ic+=1

print "\tSignal: ",quake.qsignal

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# FAST FOURIER TRANSFORM ALL SIGNAL
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
quake.qphases=""
ic=1
table=numpy.array([0,0])
for component in COMPONENTS:

    # PERIGEA
    ps=astro["Perigea"][1:,0]-qjd
    cond=(ps>-40)*(ps<+40)
    ps=ps[cond]

    print "\tPhases for component %d (ETERNA %d)..."%(ic,component)
    t=data[:,0]-data[0,0]
    s=data[:,ic]
    T=t[-1]-t[0]
    N=len(s)
    Nh=N/2

    ft=numpy.fft.fft(s,N)
    ftc=ft[0:Nh]
    ftp=numpy.absolute(ftc[1:])
    ks=numpy.arange(1,Nh)
    Ts=T/ks
    numpy.savetxt("%s%d-fft.data"%(quakeid,component),numpy.column_stack((t,ft)))
    numpy.savetxt("%s%d-ffp.data"%(quakeid,component),numpy.column_stack((Ts[::-1],
                                                                          ftp[::-1])))

    print "\t\tSaving fast fourier transform and power spectrum..."

    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # CALCULATING FFT PHASES
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    qphases=""
    for period in periods:
        print "\t\t\tPeriod = ",period
        timewindow=1.5*period
        cond=(numpy.abs(data[:,0]-time)<timewindow)
        t=data[cond,0]
        timeini=t[0]
        t=t-timeini
        s=data[cond,ic]
        N=len(s)
        if N%2:
            t=t[:-1]
            s=s[:-1]
            N-=1
        T=t[-1]-t[0]
        Nh=N/2
        ft=numpy.fft.fft(s,N)

        # PHASE
        deltatime=time-timeini
        phase=phaseFourier(ft,deltatime,T,N,period)
        print "\t\t\t\tDelta = ",deltatime
        print "\t\t\t\tPhase = ",phase

        qphases+="%.4lf;"%phase

    print "\t\tPhases: ",qphases
    quake.qphases+=qphases

    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # CALCULATING OBSERVED BOUNDARY PHASES
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    t=data[:,0]-float(quake.qjd)
    s=data[:,ic]

    print "\tPhases based on boundaries..."
    qphases=""

    # ==============================
    # FIND MAXIMA AND MINIMA
    # ==============================
    # SEMIDIURNAL LEVEL PEAKS
    tmb,smb,tMb,sMb=signalBoundary(t,s)

    # ==============================
    #STORE MAXIMA AND MINIMA AROUND 40 DAYS
    # ==============================
    cond=abs(tMb)<40
    line=numpy.array([ic,999999999])
    subtable=numpy.column_stack((tMb[cond],sMb[cond]))
    stable=numpy.vstack((line,subtable))
    table=numpy.vstack((table,stable))

    cond=abs(tmb)<40
    line=numpy.array([-ic,999999999])
    subtable=numpy.column_stack((tmb[cond],smb[cond]))
    stable=numpy.vstack((line,subtable))
    table=numpy.vstack((table,stable))
    
    # ==============================
    # SMOOTH MAXIMA & MINIMA
    # ==============================
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

    psgn=PHASESGN[ic-1]

    # ==============================
    # SEMI-DIURNAL FREQUENCY
    # ==============================
    if psgn>0:tb=tMb
    else:tb=tmb

    npeaks=len(tb)
    ipeaks=numpy.arange(npeaks)
    ipeak=ipeaks[tb<0][-1]
    dtmean=tb[ipeak+1]-tb[ipeak]
    if dtmean>0.55:dtmean=0.5

    dt=-tb[tb<0][-1]
    dtphase=dt/dtmean;
    qphases+="%.4f:%.4f;"%(dt,dtphase)
    print "\t\tSemidiurnal (%e): dt = %e, dtphase = %e"%(dtmean,dt,dtphase)

    # &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
    # DIURNAL COMPONENT
    # &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
    vvv=1

    if vvv:print "Hmoon: ",hmoon

    if psgn>0:tp=tMb
    else:tp=tmb
    if vvv:print "Sign: ",psgn

    dprev=hmoon/MOONRATE
    if vvv:print "Expected time: ",dprev
    if vvv:print "t: ",tp[(tp>-2)*(tp<2)]
    tshift=tp+dprev
    if vvv:print "tshift: : ",tshift[(tshift>-2)*(tshift<2)]
    isorts=abs(tshift).argsort()
    iso=0;dt=-1
    while dt<0:
        iprev=isorts[iso]
        dt=-tp[iprev]
        if vvv:print "Choosen peak:",iprev,dt
        iso+=1

    dtmean=tp[iprev+1]-tp[iprev-1]
    if dtmean>1.1:dtmean=1.0

    dtphase=dt/dtmean
    qphases+="%.4f:%.4f;"%(dt,dtphase)
    print "\t\tDiurnal (%e): dt = %e, dtphase = %e"%(dtmean,dt,dtphase)
    
    """
    # ==============================
    # DIURNAL FREQUENCY
    # ==============================
    # CHECK WHICH PEAK IS LARGER
    ipeaks=numpy.arange(npeaks)
    ipeak=ipeaks[tMb<0][-1]
    dpeak1=sMb[ipeak]-smb[ipeak]
    dpeak2=sMb[ipeak+1]-smb[ipeak+1]

    if dpeak1>dpeak2:
        dt=-tMb[ipeak]
        dtmean=tMb[ipeak+2]-tMb[ipeak]
    else:
        dt=-tMb[ipeak-1]
        dtmean=tMb[ipeak+1]-tMb[ipeak-1]
    dtphase=dt/dtmean
    qphases+="%.4f:%.4f;"%(dt,dtphase)
    """

    # ==============================
    # FORTNIGHTLY FREQUENCY
    # ==============================
    npeaks=len(tMF)
    ipeaks=numpy.arange(npeaks)
    ipeak=ipeaks[tMF<0][-1]
    dtmean=tMF[ipeak+1]-tMF[ipeak]
    if dtmean>16:dtmean=14.0
    dt=-tMF[tMF<0][-1]
    dtphase=dt/dtmean;
    qphases+="%.4f:%.4f;"%(dt,dtphase)
    print "\t\tFortnightly (%e): dt = %e, dtphase = %e"%(dtmean,dt,dtphase)

    # &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
    # MONTHLY
    # &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
    # FIND THE PEAK CLOSEST TO PERIGEA
    if psgn>0:tcF=tMF
    else:tcF=tmf
    cond=(tcF>-40)*(tcF<+40)
    tpF=tcF[cond]
    numpeak=len(tpF)
    ds=[]
    for tf in tpF:ds+=[min(abs(ps-tf))]
    iM=numpy.array(ds).argsort()[0]
    if vvv:print "Closest:",iM
    ipeaks=numpy.arange(npeaks)
    ipeak=ipeaks[tpF<0][-1]
    if vvv:print "Previous:",ipeak
    if abs(ipeak-iM)%2!=0:ipeak-=1
    if vvv:print "Choosen iPeak = ",ipeak

    if (ipeak+2)>=numpeak:npeak=ipeak-2
    else:npeak=ipeak+2

    if vvv:print "Number of peaks = ",numpeak
    if vvv:print "Next Peak = ",npeak
    dtmean=abs(tpF[npeak]-tpF[ipeak])
    if dtmean>35:dtmean=30.0

    dt=-tpF[ipeak]
    dtphase=dt/dtmean
    qphases+="%.4f:%.4f;"%(dt,dtphase)
    print "\t\tMonthly (%e): dt = %e, dtphase = %e"%(dtmean,dt,dtphase)

    """
    # ==============================
    # MONTHLY FREQUENCY
    # ==============================
    # CHECK WHICH PEAK IS LARGER
    ipeaks=numpy.arange(npeaks)
    ipeak=ipeaks[tMF<0][-1]
    dpeak1=sMF[ipeak]-smf[ipeak]
    dpeak2=sMF[ipeak+1]-smf[ipeak+1]
    
    if dpeak1>dpeak2:
        dt=-tMF[ipeak]
        dtmean=tMF[ipeak+2]-tMF[ipeak]
    else:
        dt=-tMF[ipeak-1]
        dtmean=tMF[ipeak+1]-tMF[ipeak-1]
    dtphase=dt/dtmean
    qphases+="%.4f:%.4f;"%(dt,dtphase)
    """

    print "\t\tPhases based on boundaries: ",qphases
    quake.qphases+=qphases
    print

    # ==============================
    # ASTRONOMY PHASES
    # ==============================
    quake.aphases=""

    # PERIGEA
    ps=astro["Perigea"][1:,0]-qjd
    dt=-ps[ps<0][-1]
    dtmean=ps[ps<0][-1]-ps[ps<0][-2]
    atphase=dt/dtmean
    quake.aphases+="%.5f:%.5f:%.5f;"%(dt,dtmean,atphase)

    # MIN.PERIGEA
    ms=astro["Min.Perigee"][1:,0]-qjd
    dt=-ms[ms<0][-1]
    dtmean=ms[ms<0][-1]-ms[ms<0][-2]
    atphase=dt/dtmean
    quake.aphases+="%.5f:%.5f:%.5f;"%(dt,dtmean,atphase)
    
    # PERIHELIA
    hs=astro["Perihelia"][1:,0]-qjd
    dt=-hs[hs<0][-1]
    dtmean=hs[hs<0][-1]-hs[hs<0][-2]
    atphase=dt/dtmean
    quake.aphases+="%.5f:%.5f:%.5f;"%(dt,dtmean,atphase)

    ic+=1

numpy.savetxt("%s-max.data"%quakeid,table)

print "\n\tAll phases: ",quake.qphases
print "\n\tAstronomy phases: ",quake.aphases

saveObject("quake.conf",quake)
