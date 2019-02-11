from tquakes import *
print "*"*50+"\nRUNNING tquakes-analysis\n"+"*"*50
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

# SETTING STATION STATUS
System("links -dump '%s/action.php?action=status&station_id=%s&station_status=4'"%(conf.WEBSERVER,station.station_id))

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

    # TIME
    time_start=timeit()
    print "\tStarting time: ",time_start

    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # RUN JOB
    out=System("cd %s;PYTHONPATH=. python quake-analysis.py %s >> quake.log"%(quakedir,quakeid))
    quake=loadConf(quakedir+"quake.conf")
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    # CHANGE STATUS OF QUAKE
    System("date +%%s > %s/.analysis"%quakedir)
    System("mv %s/.eterna %s/.states"%(quakedir,quakedir))
    System("cp %s/.analysis %s/.states"%(quakedir,quakedir))
    
    # COMPRESS
    System("cd %s;tar cf %s-analysis.tar %s*-ff*.* quake.conf quake.log .states"%(quakedir,
                                                                                  quakeid,quakeid))  
    System("cd %s;p7zip %s-analysis.tar"%(quakedir,quakeid))
    System("cd %s;rm *ff*"%(quakedir))
    System("cd %s;cp quake.conf %s.conf"%(quakedir,quakeid))
    
    # TIME
    time_end=timeit()
    print "\tEnd time: ",time_end
    deltat=time_end-time_start
    print "\tTime elapsed: ",deltat

    # REPORT END OF ANALYSIS
    print "\tReporting calculations..."
    out=System("links -dump '%s/action.php?action=analysis&station_id=%s&quakeid=%s&qsignal=%s&qphases=%s&aphases=%s&deltat=%.3f'"%(conf.WEBSERVER,station.station_id,
                                                                                                                                    quakeid,
                                                                                                                                    quake.qsignal,
                                                                                                                                    quake.qphases,
                                                                                                                                    quake.aphases,
                                                                                                                                    deltat))

    # DELETE LOCKFILE
    System("rm "+lockfile)

    print "\tQuake done."

    iq+=1
    # if iq>2*conf.NUMQUAKES:break
    
