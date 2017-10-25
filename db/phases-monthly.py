from tquakes import *
from matplotlib import use
use('Agg')
import matplotlib.pyplot as plt
import spiceypy as sp
from timeit import default_timer as timer
import sys,time
sp.furnsh("util/kernels/kernels.mk")

# TIME WINDOW FOR MONTHLY PHASES
DT=CONF.TIMEWIDTH/2.0

# VERBOSE
vvv=0
# REPLACE FILES
rrr=0
# MEASURE TIME
ttt=0
# UPDATE DATABASE
iupdb=100

"""

Use this file to update critical information about earthquakes in the database

"""
# ############################################################
# LOAD DATABASE
# ############################################################
tQuakes,connection=loadDatabase()
db=connection.cursor()

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
numquakes=len(tQuakes['Quakes']['rows'].keys())
print "Attempting to update %d earthquakes..."%numquakes

keys=tQuakes['Quakes']['rows'].keys()
#numpy.random.shuffle(keys)

for j,quakeid in enumerate(keys):

    quake=tQuakes['Quakes']['rows'][quakeid]

    qcomplete=100.0*float(i)/float(numquakes)
    #"""
    sys.stdout.write('\r')
    sys.stdout.write("RUNNING ----> %d/%d %.1f%% DONE"%(j,numquakes,qcomplete))
    sys.stdout.flush()
    #"""
    #if quake["quakeid"]!="0004H1O":continue

    status=quake["astatus"]
    aphases=quake["aphases"]

    # TEST IF QUAKE HAS NOT BEEN FULLY ANALYSED
    if status!='4':
        if vvv:print "Quake %s not analysed"%quakeid
        continue

    # TEST IF QUAKE HAS BEEN ALREADY ANALYSED
    if len(aphases)>82:
        if vvv:print "Quake %s already updated"%quakeid
        continue

    if vvv:print "Quake to update ",quakeid

    if ttt:tstart=timer()
    hmoon=float(quake["hmoon"])
    qjd=float(quake["qjd"])

    # PERIGEA
    ps=astro["Perigea"][1:,0]-qjd
    cond=(ps>-40)*(ps<+40)
    ps=ps[cond]
    
    # FULL MOONS
    pfs=full[:]-qjd
    cond=(pfs>-DT)*(pfs<+DT)
    pfs=pfs[cond]

    # READ CONFILE
    conf=loadConf("/home/tquakes/tQuakes/%s.conf"%quakeid)

    # READ PHASES
    qphases=quake["qphases"]
    if vvv:print "Full phases:",qphases
    qphasesvec=qphases.split(";")[:-1]
    if vvv:print "Num. phases:",len(qphasesvec)

    # EXTRACTING FILES
    print "Extracting timeseries..."
    qdir="tmp2/%s-analysis"%quakeid
    System("cd tmp2;cp -r TEMPLATE %s-analysis"%(quakeid))
    cmd="7zr x -so /home/tquakes/tQuakes/%s-eterna.* |tar xf - -C %s %s.data"%(quakeid,qdir,quakeid)
    System(cmd)

    # IF DATA FILE IS NOT PRESENT
    if not os.path.isfile("%s.data"%quakeid):
        print "Data file not recovered for %s..."%quakeid
        cmd="7zr x -so /home/tquakes/tQuakes/%s-eterna.* |tar xf - -C %s"%(quakeid,qdir)
        System(cmd)
        System("cd %s;python quake-data.py %s"%(qdir,quakeid))
        if os.path.isfile("%s/%s.data"%(qdir,quakeid)):
            print "Data file succesfully reconstructed for %s."%quakeid

    # !!!! REPLACE FILES !!!!
    if rrr:
        System("cp /home/tquakes/tQuakes/%s-analysis.* %s"%(quakeid,qdir))
        System("cd %s;p7zip -d %s-analysis.tar.7z;tar xf %s-analysis.tar quake.conf"%(qdir,quakeid,quakeid))
        System("cd %s;mv quake.conf quake.old"%(qdir))


    #READ 
    try:
        tab=numpy.loadtxt("%s/%s.data"%(qdir,quakeid))
        t=tab[:,0]-qjd
    except:
        print "\nEarthquake %s being analysed or is bad..."%quakeid

        # Exclude bad events
        sql="update Quakes set astatus='6' where quakeid='%s'"%(quakeid)
        db.execute(sql)
        connection.commit()
        
        # REMOVE TEMPORAL DIRECTORY
        System("rm -r %s"%(qdir))

        continue

    if vvv:print "Times sample:",t[:5]

    # CORRECT PHASES
    for component in COMPONENTS:
        if vvv:print "*"*60,"\nAnalysing component ",component,"\n","*"*60

        # &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
        # COMPONENT POSITION
        # &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
        nc=COMPONENTS.index(component)+1
        np=NUM_PHASES*(nc-1)
        psgn=PHASESGN[nc-1]
        if vvv:print "Component position and sign: ",nc,np,psgn
        if vvv:print "Old phases:",qphasesvec[np+4:np+4+4]

        # &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
        # CALCULATE PHASES
        # &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
        s=tab[:,nc]
        if vvv:print "Signal sample:",s[:5]
        try:
            qphase=calculatePhases(t,s,psgn,hmoon,pfs,DT=CONF.TIMEWIDTH/2.0,
                                   waves=None,verb=vvv)
        except:
            print "\nError with data of %s..."%quakeid
            continue

        if vvv:print "New phases:",qphase
        qphasevec=qphase.split(";")[:-1]
        if vvv:print "New phase vec:",qphasevec

        # &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
        # REPLACE PHASES
        # &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
        iphase=(nc-1)*8
        if vvv:print "Replacing:",qphasesvec[iphase+4:iphase+8]
        qphasesvec[iphase+4:iphase+8]=qphasevec

    if vvv:print "Final phases:"
    for component in COMPONENTS:
        nc=COMPONENTS.index(component)+1
        iphase=(nc-1)*8
        if vvv:print "\tPhases for component %d:"%component,qphasesvec[iphase+4:iphase+8]

    if vvv:print "Joined old phases:",qphases
    qphases=";".join(qphasesvec)
    if vvv:print "Joined new phases:",qphases
    
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

    # FULL MOON
    ps=full-qjd
    dt=-ps[ps<0][-1]
    dtmean=ps[ps<0][-1]-ps[ps<0][-2]
    atphase=dt/dtmean
    if vvv:print "Full: Dt, Dtmean, atphase:",dt,dtmean,atphase
    aphases+="%.5f:%.5f:%.5f;"%(dt,dtmean,atphase)
    
    # CORRECTING CONFIGURATION FILE
    if rrr:
        if vvv:print "Correcting configuration file..."
        fold=open("%s/quake.old"%qdir,"r")
        fnew=open("%s/quake.conf"%qdir,"w")
        for line in fold.readlines():
            line=line.strip()
            if 'qphases' in line:
                line="qphases = '"+qphases+"'"
            if 'aphases' in line:
                line="aphases = '"+aphases+"'"
            fnew.write(line+"\n")
        fnew.close()
        fold.close()

    # SAVE AND STORE
    if vvv:print "Storing results..."

    # !!!! REPLACE FILES !!!!
    if rrr:
        System("cd %s;tar rf %s-analysis.tar quake.conf;p7zip %s-analysis.tar"%(qdir,quakeid,quakeid))
        System("mv %s/%s-analysis.tar.7z /home/tquakes/tQuakes/"%(qdir,quakeid))
        System("mv %s/quake.conf /home/tquakes/tQuakes/%s.conf"%(qdir,quakeid))

    # REMOVE TEMPORAL DIRECTORY
    System("rm -r %s"%(qdir))

    # UPDATE DATABASE
    if vvv:print "Saving into database..."
    sql="update Quakes set qphases='%s',aphases='%s' where quakeid='%s'"%(qphases,
                                                                          aphases,
                                                                          quakeid)

    if vvv:print "\tSQL: %s"%sql
    while True:
        try:
            db.execute(sql)
            break
        except:
            print "\nWaiting for db unlock..."
            time.sleep(0.5)
    
    if ttt:tend=timer();print "Execution time for %s:"%quakeid,tend-tstart
    if (i and ((i%iupdb)==0)) or True:
        if vvv:print "Quake %d/%d..."%(i,numquakes)
        connection.commit()
        #break
    i+=1

print
