from tquakes import *
print "*"*50+"\nRUNNING tquakes-eterna\n"+"*"*50
if os.path.lexists("stop"):
    print "Stopping."
    exit(0)

# ##################################################
# CONFIGURATION
# ##################################################
conf=loadConf("configuration")
updateConf("common",conf)

# ##################################################
# LOAD STATION INFORMATION
# ##################################################
station=loadConf(".stationrc")

# ##################################################
# CHECK IF RUN IS ONLY FOR ONE QUAKE
# ##################################################
fquakeid=""
if len(argv)>1:fquakeid=argv[1]

# ##################################################
# GET UNCALCULATED QUAKES
# ##################################################
if not len(fquakeid):
    print "Searching prepared quakes..."
    qlist=System("ls data/quakes/*/.prepare 2> /dev/null")
    if len(qlist)==0:
        print "\tNo quakes prepared."
        exit(0)
    else:
        qlist=qlist.split("\n")
        nquakes=len(qlist)
        print "\t%d prepared quakes found..."%nquakes

    # SETTING STATUS
    System("links -dump '%s/action.php?action=status&station_id=%s&station_status=3'"%(conf.WEBSERVER,station.station_id))
else:
    qlist=["data/quakes/%s/.prepare"%fquakeid]
    nquakes=1

# ##################################################
# LOOP OVER QUAKES
# ##################################################
iq=1
for quake in qlist:
    search=re.search("\/(\w+)\/\.prepare",quake)
    quakeid=search.group(1)
    lquakeid=quakeid.lower()
    print "Running Gotic2 for quake %d '%s'"%(iq,quakeid)

    # LOAD QUAKE INFORMATION
    quakedir="data/quakes/%s/"%quakeid
    quake=loadConf(quakedir+"quake.conf")

    # CHECK IF THE QUAKE HAVE BEEN ALREADY RAN
    if not len(fquakeid):
        if not os.path.lexists(quakedir+".prepare"):
            print "\tQuake already calculated by other process..."
            continue

    # ONLY PREPARE QUAKES NOT LOCKED
    if not len(fquakeid):
        lockfile=quakedir+".lock"
        if os.path.lexists(lockfile):
            print "\tQuake locked by another process"
            continue
        else:
            print "\tLocking quake"
            System("touch "+lockfile)
        
    # TIME
    time_start=timeit()
    print "\tStarting time: ",time_start

    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # RUN JOB
    #out=System("cd %s;PYTHONPATH=. python quake-gotic2.py %s >> quake.log"%(quakedir,quakeid))
    #print out
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # CHECK IF THE RUN FAIL
    if os.path.lexists("%s/.fail"%quakedir):
        print "\tJob failed."
        System("date +%%s > %s/.failed"%quakedir)
        System("mv %s/.prepare %s/.states"%(quakedir,quakedir))
        print "\tReporting failure..."
        out=System("links -dump '%s/action.php?action=fail&station_id=%s&quakeid=%s'"%(conf.WEBSERVER,station.station_id,quakeid))
        exit(0)
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    # 7ZIP RESULTS
    System("cd %s;tar cf %s-gotic2.tar %s*.out %s*.pre quake.conf quake.log"%(quakedir,
                                                                              quakeid,quakeid,lquakeid))  
    System("cd %s;p7zip %s-gotic2.tar"%(quakedir,quakeid))

    # TIME
    time_end=timeit()
    print "\tEnd time: ",time_end
    deltat=time_end-time_start
    print "\tTime elapsed: ",deltat

    # CHANGE STATUS OF QUAKE
    System("date +%%s > %s/.eterna"%quakedir)
    System("mv %s/.prepare %s/.states"%(quakedir,quakedir))
    
    # REPORT END OF CALCULATIONS
    if not len(fquakeid):
        print "\tReporting calculations..."
        out=System("links -dump '%s/action.php?action=report&station_id=%s&quakeid=%s&deltat=%.3f'"%(conf.WEBSERVER,station.station_id,quakeid,deltat))

        # DELETE LOCKFILE
        System("rm "+lockfile)

    print "\tQuake done."

    iq+=1
    if iq>2*conf.NUMQUAKES:break
