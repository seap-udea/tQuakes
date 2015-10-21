from tquakes import *
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
quake.qsignal=""
for component in COMPONENTS:
    signal=data[:,ic]
    value=numpy.interp(time,times,signal)
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
    from scipy import signal
    t=data[:,0]-float(quake.qjd)
    s=data[:,ic]
    exit(0)

    ic+=1

print "\tAll phases: ",quake.qphases
saveObject("quake.conf",quake)
