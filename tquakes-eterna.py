from tquakes import *
print "*"*50+"\nRUNNING tquakes-eterna\n"+"*"*50
# ##################################################
# CONFIGURATION
# ##################################################
conf=loadConf("configuration")
predict="util/Eterna/ETERNA34/PREDICT.EXE"

# ##################################################
# LOAD STATION INFORMATION
# ##################################################
station=loadConf(".stationrc")

# ##################################################
# GET UNCALCULATED QUAKES
# ##################################################
print "Searching prepared quakes..."
qlist=System("ls data/quakes/*/.prepare 2> /dev/null")
if len(qlist)==0:
    print "\tNo quakes prepared."
    exit(0)
else:
    qlist=qlist.split("\n")
    nquakes=len(qlist)
    print "\t%d prepared quakes found..."%nquakes

out=System("links -dump '%s/index.php?action=status&station_id=%s&station_status=3'"%(conf.WEBSERVER,station.station_id))
# ##################################################
# LOOP OVER QUAKES
# ##################################################
iq=1
for quake in qlist:
    search=re.search("\/(\w+)\/\.prepare",quake)
    quakeid=search.group(1)
    lquakeid=quakeid.lower()
    print "Running Eterna for quake %d '%s'"%(iq,quakeid)

    # LOAD QUAKE INFORMATION
    quakedir="data/quakes/%s/"%quakeid
    quake=loadConf(quakedir+"quake.conf")

    # CHECK IF THE QUAKE HAVE BEEN ALREADY RAN
    if not os.path.lexists(quakedir+".prepare"):
        print "\tQuake already calculated by other process..."
        continue

    # ONLY PREPARE QUAKES NOT LOCKED
    lockfile=quakedir+".lock"
    if os.path.lexists(lockfile):
        print "\tQuake locked by another process"
        continue
    else:
        print "\tLocking quake"
        System("touch "+lockfile)
        
    # COPY PREDICT PROGRAM
    System("cp %s %s"%(predict,quakedir))

    # TIME
    time_start=timeit()
    print "\tStarting time: ",time_start

    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # RUN JOB
    out=System("cd %s;python quake-eterna.py %s"%(quakedir,quakeid))
    print out
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    # 7ZIP RESULTS
    System("cd %s;tar cf %s-eterna.tar %s*.* %s*.* .states"%(quakedir,
                                                             quakeid,quakeid,lquakeid))  
    System("cd %s;p7zip %s-eterna.tar"%(quakedir,quakeid))
    System("cd %s;rm PREDICT.EXE project* %s*.??? %s*.???"%(quakedir,
                                                            quakeid,lquakeid))  

    # TIME
    time_end=timeit()
    print "\tEnd time: ",time_end
    deltat=time_end-time_start
    print "\tTime elapsed: ",deltat

    # CHANGE STATUS OF QUAKE
    System("date +%%s > %s/.eterna"%quakedir)
    System("mv %s/.prepare %s/.states"%(quakedir,quakedir))
    
    # REPORT END OF CALCULATIONS
    print "\tReporting calculations..."
    out=System("links -dump '%s/index.php?action=report&station_id=%s&quakeid=%s&deltat=%.3e'"%(conf.WEBSERVER,station.station_id,quakeid,deltat))

    # DELETE LOCKFILE
    System("rm "+lockfile)

    print "\tQuake done."

    iq+=1
    if iq>2*conf.NUMQUAKES:break
