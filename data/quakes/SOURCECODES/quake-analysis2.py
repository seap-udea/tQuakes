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
# CHOOSE COMPONENTS
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
COMPONENTS=[]
for k,gn in GOTIC2.items():
    gname=k
    if k=="HN" or k=="HE":gname="HD"
    g=GOTIC2_COLUMNS[gname]
    for gt,gtn in GOTIC2_TYPES.items():
        if gt=="O":continue
        for f in g:
            COMPONENTS+=["T=%s.L=%s.C=%s"%(k,gt,f)]

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
    ic=GOTIC2_NCOLUMNS[component]
    sig=data[:,ic]
    value=numpy.interp(time,times,sig)
    quake.qsignal+="%.4lf;"%value

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# ANALYSIS OF PHASES
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
quake.qphases=""
table=numpy.array([0,0])
for component in COMPONENTS:

    # PERIGEA
    ps=astro["Perigea"][1:,0]-qjd
    cond=(ps>-40)*(ps<+40)
    ps=ps[cond]

    #Phases component
    ic=GOTIC2_NCOLUMNS[component]
    print "\tPhases for component %d (GOTIC2 %s)..."%(ic,component)
    
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

    # SIGN OF PHASES
    #psgn=PHASESGN[ic-1]
    psgn=+1

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
    vvv=0

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
    ipeaks=numpy.arange(numpeak)
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

numpy.savetxt("%s-max.data"%quakeid,table)

print "\n\tAll phases: ",quake.qphases
print "\n\tAstronomy phases: ",quake.aphases

saveObject("quake.conf",quake)
