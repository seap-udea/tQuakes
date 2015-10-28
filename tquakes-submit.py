from tquakes import *
print "*"*50+"\nRUNNING tquakes-submit\n"+"*"*50
if os.path.lexists("stop"):
    print "Stopping."
    exit(0)

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
# CHECK IF STATION CAN SUBMIT
# ##################################################
qdisabled=False
out=System("links -dump '%s/index.php?action=checkstation&station_id=%s'"%(conf.WEBSERVER,station.station_id))

if int(out)>0:
    print "Station enabled."
elif int(out)==0:
    print "Station disabled."
    qdisabled=True
elif int(out)==-1:
    print "Station not recognized."
    qdisabled=True

# IF STATION IS DISABLED STOP
if qdisabled:exit(0)

System("links -dump '%s/index.php?action=status&station_id=%s&station_status=5'"%(conf.WEBSERVER,station.station_id))
# ##################################################
# GET UNSUBMITED QUAKES
# ##################################################
print "Searching calculated quakes..."
qlist=System("ls data/quakes/*/.analysis 2> /dev/null")
if len(qlist)==0:
    print "\tNo quakes analysed."
    exit(0)
else:
    qlist=qlist.split("\n")
    nquakes=len(qlist)
    print "\t%d analysed quakes found..."%nquakes

# ##################################################
# LOOP OVER QUAKES
# ##################################################
iq=1
for quake in qlist:
    search=re.search("\/(\w+)\/\.analysis",quake)
    quakeid=search.group(1)
    print "Submitting quake %d '%s'"%(iq,quakeid)

    # LOAD QUAKE INFORMATION
    quakedir="data/quakes/%s/"%quakeid
    quake=loadConf(quakedir+"quake.conf")

    if not os.path.lexists(quakedir+".analysis"):
        print "\tQuake already submit by other process..."
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

    # SUBMIT DATA
    system("scp -o 'StrictHostKeyChecking no' -r %s/*.7z tquakes@%s:. 2> scratch/%s.err"%(quakedir,conf.DATASERVER,quakeid))
    if System("cat scratch/%s.err"%quakeid)!="":
        print "\tConnection failed to data server."
        System("rm "+lockfile)
        continue

    # CHANGE STATUS OF QUAKE
    System("date +%%s > %s/.submit"%quakedir)
    System("mv %s/.analysis %s/.states"%(quakedir,quakedir))

    # TIME
    time_end=timeit()
    print "\tEnd time: ",time_end
    deltat=time_end-time_start
    print "\tTime elapsed: ",deltat

    # REPORT END OF ANALYSIS
    print "\tReporting submission..."
    out=System("links -dump '%s/index.php?action=submit&station_id=%s&quakeid=%s&deltat=%.3f'"%(conf.WEBSERVER,station.station_id,quakeid,deltat))
    if 'Not Found' in out:
        print "\tConnection failed to webserver."
        System("rm "+lockfile)
        continue

    # REMOVE RESULT
    System("rm -r %s"%(quakedir))

    # DELETE LOCKFILE
    System("rm "+lockfile)

    print "\tQuake done."

    iq+=1
    # if iq>2*conf.NUMQUAKES:break
