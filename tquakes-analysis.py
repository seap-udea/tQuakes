from tquakes import *
print "*"*50+"\nRUNNING tquakes-analysis\n"+"*"*50

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
# GET NOT ANALYSED QUAKES
# ##################################################
print "Searching calculated quakes..."
qlist=System("ls data/quakes/*/.eterna 2> /dev/null")
if len(qlist)==0:
    print "\tNo quakes calculated."
    exit(0)
else:
    qlist=qlist.split("\n")
    nquakes=len(qlist)
    print "\t%d calculated quakes found..."%nquakes

# ##################################################
# LOOP OVER QUAKES
# ##################################################
iq=1
for quake in qlist:
    search=re.search("\/(\w+)\/\.eterna",quake)
    quakeid=search.group(1)
    print "Analysing quake %d '%s'"%(iq,quakeid)

    # LOAD QUAKE INFORMATION
    quakedir="data/quakes/%s/"%quakeid
    quake=loadConf(quakedir+"quake.conf")

    if not os.path.lexists(quakedir+".eterna"):
        print "\tQuake already analysed by other process..."
        continue

    # ONLY PREPARE QUAKES NOT LOCKED
    lockfile=quakedir+".lock"
    if os.path.lexists(lockfile):
        print "\tQuake locked by another process"
        continue
    else:
        print "\tLocking quake"
        System("touch "+lockfile)

    # LOAD DATA
    data=numpy.loadtxt(quakedir+"%s.data"%quakeid)

    # INTERPOLATE SIGNAL
    ic=1
    times=data[:,0]
    time=float(quake.qjd)
    quake.qsignal=""
    for component in 2,4,5:
        signal=data[:,ic]
        value=numpy.interp(time,times,signal)
        quake.qsignal+="%.4lf;"%value
        ic+=1

    print "\tSignal: ",quake.qsignal

    # ALL SIGNAL
    t=data[:,0]-data[0,0]
    s=data[:,2]
    T=t[-1]-t[0]
    N=len(s)
    Nh=N/2

    # FAST FOURIER TRANSFORM
    ft=numpy.fft.fft(s,N)
    ftc=ft[0:Nh]
    ftp=numpy.absolute(ftc[1:])
    ks=numpy.arange(1,Nh)
    Ts=T/ks
    numpy.savetxt("%s/%s-fft.data"%(quakedir,quakeid),numpy.column_stack((t,ft)))
    numpy.savetxt("%s/%s-ffp.data"%(quakedir,quakeid),numpy.column_stack((Ts[::-1],
                                                                          ftp[::-1])))

    print "\tSaving fast fourier transform and power spectrum..."

    quake.qphases=""
    for period in periods:
        print "\tPeriod = ",period
        timewindow=1.5*period
        cond=(numpy.abs(data[:,0]-time)<timewindow)
        t=data[cond,0]
        timeini=t[0]
        t=t-timeini
        s=data[cond,2]
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
        print "\t\tDelta = ",deltatime
        print "\t\tPhase = ",phase

        quake.qphases+="%.4lf;"%phase
        
    print "\tPhases: ",quake.qphases

    # COMPRESS
    System("cd %s;tar cf %s-analysis.tar %s-ff*.*"%(quakedir,
                                                    quakeid,quakeid))  
    System("cd %s;p7zip %s-analysis.tar"%(quakedir,quakeid))
    System("cd %s;rm *ff*"%(quakedir))  
    
    # CHANGE STATUS OF QUAKE
    System("date +%%s > %s/.analysis"%quakedir)
    System("mv %s/.eterna %s/.states"%(quakedir,quakedir))
    
    # REPORT END OF ANALYSIS
    print "\tReporting calculations..."
    out=System("links -dump '%s/index.php?action=analysis&station_id=%s&quakeid=%s&qsignal=%s&qphases=%s'"%(conf.WEBSERVER,station.station_id,
                                                                                                                    quakeid,
                                                                                                                    quake.qsignal,
                                                                                                                    quake.qphases))

    # DELETE LOCKFILE
    System("rm "+lockfile)

    print "\tQuake done."

    iq+=1
    if iq>2*conf.NUMQUAKES:break
    
