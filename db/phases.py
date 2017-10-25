from tquakes import *
from matplotlib import use
use('Agg')
import matplotlib.pyplot as plt
import spiceypy as sp
sp.furnsh("util/kernels/kernels.mk")

# ############################################################
# LOAD DATABASE
# ############################################################
tQuakes,connection=loadDatabase()
db=connection.cursor()

vvv=1

extremes=[]
i=1
for ncomp in COMPONENTS:
    for key in COMPONENTS_DICT.keys():
        if COMPONENTS_DICT[key][0]==ncomp:
            extremes+=[[i,key]]
    i+=1

# ASTRONOMY EXTREMES 
table=numpy.loadtxt("astronomy-extremes-1970_2030.data")
astro=loadExtremesTable(EXTREMES,table)
full=numpy.loadtxt("util/astronomy-fullmoons-1970_2030.data")

i=0
for quakeid in tQuakes['Quakes']['rows'].keys():

    quake=tQuakes['Quakes']['rows'][quakeid]
    status=quake["astatus"]
    if status!='4':
        print "Quake %s not analysed"%quakeid
        continue

    #if ((i%1000)==0):print "Quake %d %s..."%(i,quake["quakeid"])
    i+=1
    
    #if quake["quakeid"]!="0004H1O":continue
    if vvv:print "Quake ",quakeid

    """-

    Determine the hour angle of the Sun and the Moon at the time of
    Earthquake.  This will help us to calculate the diurnal phase.

    """

    # COMPUTE THE POSITION OF THE OBSERVER ON THE SURFACE OF THE EARTH
    #if vvv:print "Updating %s..."%quakeid
    #if vvv:print "Date and time: ",quake["qdatetime"]
    qet=float(quake["qet"])
    qlat=float(quake["qlat"])
    qlon=float(quake["qlon"])
    qjd=float(quake["qjd"])
    qdepth=float(quake["qdepth"])
    hmoon=float(quake["hmoon"])
    hsun=float(quake["hsun"])
    ps=astro["Perigea"][1:,0]-qjd
    cond=(ps>-40)*(ps<+40)
    ps=ps[cond]
    
    # READ CONFILE
    conf=loadConf("/home/tquakes/tQuakes/%s.conf"%quakeid)

    # READ MAXFILE
    table=numpy.loadtxt("/home/tquakes/tQuakes/%s-max.data"%quakeid)
    data=loadExtremesTable(extremes,table)

    # READ PHASES
    qphases=quake["qphases"]
    qphasesvec=qphases.split(";")[:-1]
    
    # CORRECT PHASES
    qphasesnew=qphasesvec+[]
    for component in data.keys():
        #if component!="hs" and component!="vd":continue
        if component!="grav":continue

        if vvv:print "*"*60,"\nAnalysing component ",component,"\n","*"*60

        qphase=""

        # &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
        # DETERMINE WHICH PART OF PHASES
        # &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
        nc,np=numComponent(component)
        if vvv:print "Component position: ",nc,np

        # &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
        # SEMIDIURNAL COMPONENT
        # &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
        tab=data[component][1:]
        t=tab[:,0]
        s=tab[:,1]

        npeaks=len(t)
        ipeaks=numpy.arange(npeaks)
        ipeak=ipeaks[t<0][-1]
        dtmean=t[ipeak+1]-t[ipeak]
        dt=-t[t<0][-1]
        dtphase=dt/dtmean;
        qphase+="%.4f:%.4f;"%(dt,dtphase)
        if vvv:print "Semidiurnal time and phase: ",dt,dtphase

        # &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
        # DIURNAL COMPONENT
        # &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
        if vvv:print "Hmoon = ",hmoon
        dprev=hmoon/MOONRATE
        if vvv:print "Expected time: ",dprev
        if vvv:print "t: : ",t[(t>-2)*(t<2)]
        tshift=t+dprev
        if vvv:print "tshift: : ",tshift[(tshift>-2)*(tshift<2)]
        iprev=abs(tshift).argsort()[0]
        dtmean=t[iprev+1]-t[iprev-1]
        dt=-t[iprev]
        dtphase=dt/dtmean
        qphase+="%.4f:%.4f;"%(dt,dtphase)
        if vvv:print "Diurnal time and phase: ",dt,dtphase

        # &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
        # FORNIGHTLY
        # &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
        # SMOOTH
        b,a=signal.butter(8,0.125)
        sM=signal.filtfilt(b,a,s,padlen=50)
        tM=t
        # FORTNIGHTLY LEVEL PEAKS (MAXIMA)
        tmF,smF,tMF,sMF=signalBoundary(tM,sM)

        npeaks=len(tMF)
        ipeaks=numpy.arange(npeaks)
        ipeak=ipeaks[tMF<0][-1]
        dtmean=tMF[ipeak+1]-tMF[ipeak]
        dt=-tMF[tMF<0][-1]
        dtphase=dt/dtmean;
        qphase+="%.4f:%.4f;"%(dt,dtphase)
        if vvv:print "Fornightly time and phase: ",dt,dtphase

        # &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
        # MONTHLY
        # &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
        # FIND THE PEAK CLOSEST TO PERIGEA
        ds=[]
        for tf in tMF:ds+=[min(abs(ps-tf))]
        iM=numpy.array(ds).argsort()[0]
        if vvv:print "Closest:",iM
        ipeaks=numpy.arange(npeaks)
        ipeak=ipeaks[tMF<0][-1]
        if vvv:print "Previous:",ipeak
        if abs(ipeak-iM)%2!=0:ipeak-=1
        if vvv:print "Choosen iPeak = ",ipeak
        dtmean=tMF[ipeak+2]-tMF[ipeak]
        if vvv:print "dtmean = ",dtmean
        dt=-tMF[ipeak]
        if vvv:print "dt= ",dt
        dtphase=dt/dtmean
        qphase+="%.4f:%.4f;"%(dt,dtphase)
        if vvv:print "Monthly time and phase: ",dt,dtphase
                    
        # PLOT
        #"""
        fig,axs=subPlots(plt,[1])
        axs[0].plot(t,s,'ro')
        axs[0].plot(tM,sM,'b-')
        axs[0].plot(tMF,sMF,'gs')
        axs[0].set_ylabel("%s"%component)
        axs[0].set_title("%s"%quakeid)
        axs[0].grid()
        for tp in ps:axs[0].axvline(tp,color='k',zorder=-1000,alpha=0.1,linewidth=3)
        fig.savefig("extremes-%s.png"%component)
        # """
        break

        # &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
        # SAVE
        # &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
        iphase=(nc-1)*8
        qphasevec=qphase.split(";")[:-1]
        if vvv:print "New: ",qphasevec
        if vvv:print "Old: ",qphasesvec[iphase:iphase+8]
        qphasesnew[iphase+4:iphase+8]=qphasevec
        if vvv:print "New full:",qphasesnew[iphase:iphase+8]

    break
    
    # ASTRONOMY PHASES
    aphases=""

    # PERIGEA
    ps=astro["Perigea"][1:,0]-qjd
    dt=-ps[ps<0][-1]
    dtmean=ps[ps<0][-1]-ps[ps<0][-2]
    atphase=dt/dtmean
    if vvv:print "Perigea: Dt, Dtmean, atphase:",dt,dtmean,atphase
    aphases+="%.5f:%.5f:%.5f;"%(dt,dtmean,atphase)

    # MIN.PERIGEA
    ms=astro["Min.Perigee"][1:,0]-qjd
    dt=-ms[ms<0][-1]
    dtmean=ms[ms<0][-1]-ms[ms<0][-2]
    atphase=dt/dtmean
    if vvv:print "Minimum perigea: Dt, Dtmean, atphase:",dt,dtmean,atphase
    aphases+="%.5f:%.5f:%.5f;"%(dt,dtmean,atphase)
    
    # PERIHELIA
    hs=astro["Perihelia"][1:,0]-qjd
    dt=-hs[hs<0][-1]
    dtmean=hs[hs<0][-1]-hs[hs<0][-2]
    atphase=dt/dtmean
    if vvv:print "Perihelia: Dt, Dtmean, atphase:",dt,dtmean,atphase
    aphases+="%.5f:%.5f:%.5f;"%(dt,dtmean,atphase)
    
    # EXTRACTING FILES
    if vvv:print "Reconfiguring files..."
    qdir="tmp2/%s-analysis"%quakeid
    System("mkdir -p %s"%qdir)
    System("cp /home/tquakes/tQuakes/%s-analysis.* %s"%(quakeid,qdir))
    System("cd %s;p7zip -d %s-analysis.tar.7z;tar xf %s-analysis.tar quake.conf"%(qdir,quakeid,quakeid))
    System("cd %s;mv quake.conf quake.old"%(qdir))
    
    # CORRECTING CONFIGURATION FILE
    if vvv:print "Correcting configuration file..."
    fold=open("%s/quake.old"%qdir,"r")
    fnew=open("%s/quake.conf"%qdir,"w")
    qphases=";".join(qphasesnew)
    for line in fold.readlines():
        line=line.strip()
        if 'qphases' in line:
            line="qphases = '"+qphases+"'"
        fnew.write(line+"\n")
    fnew.write("hmoon = '%.5f'\n"%hmoon) 
    fnew.write("hsun = '%.5f'\n"%hsun) 
    fnew.write("aphases = '%s'\n"%aphases) 
    fnew.close()
    fold.close()

    # SAVE AND STORE
    if vvv:print "Storing results..."
    System("cd %s;tar rf %s-analysis.tar quake.conf;p7zip %s-analysis.tar"%(qdir,quakeid,quakeid))
    System("mv %s/%s-analysis.tar.7z /home/tquakes/tQuakes/"%(qdir,quakeid))
    System("mv %s/quake.conf /home/tquakes/tQuakes/%s.conf"%(qdir,quakeid))
    System("rm -r %s"%(qdir))

    # UPDATE DATABASE
    if vvv:print "Saving into database..."
    sql="update Quakes set qphases='%s',aphases='%s' where quakeid='%s'"%(qphases,
                                                                          aphases,
                                                                          quakeid)

    if vvv:print "\tSQL: %s"%sql
    db.execute(sql)
    connection.commit()


