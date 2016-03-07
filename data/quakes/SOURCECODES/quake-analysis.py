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
for component in COMPONENTS:
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

    # ==============================
    # SEMI-DIURNAL FREQUENCY
    # ==============================
    npeaks=len(tMb)
    ipeaks=numpy.arange(npeaks)
    ipeak=ipeaks[tMb<0][-1]
    dtmean=tMb[ipeak+1]-tMb[ipeak]
    dt=-tMb[tMb<0][-1]
    dtphase=dt/dtmean;
    qphases+="%.4f:%.4f;"%(dt,dtphase)
    print "\t\tSemidiurnal (%e): dt = %e, dtphase = %e"%(dtmean,dt,dtphase)

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

    print "\t\tDiurnal (%e): dt = %e, dtphase = %e"%(dtmean,dt,dtphase)

    # ==============================
    # FORTNIGHTLY FREQUENCY
    # ==============================
    npeaks=len(tMF)
    ipeaks=numpy.arange(npeaks)
    ipeak=ipeaks[tMF<0][-1]
    dtmean=tMF[ipeak+1]-tMF[ipeak]
    dt=-tMF[tMF<0][-1]
    dtphase=dt/dtmean;
    qphases+="%.4f:%.4f;"%(dt,dtphase)
    print "\t\tFortnightly (%e): dt = %e, dtphase = %e"%(dtmean,dt,dtphase)

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
    print "\t\tMonthly (%e): dt = %e, dtphase = %e"%(dtmean,dt,dtphase)

    print "\t\tPhases based on boundaries: ",qphases
    quake.qphases+=qphases
    print

    ic+=1

print "\n\tAll phases: ",quake.qphases
saveObject("quake.conf",quake)
