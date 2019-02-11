from tquakes import *
print "*"*50+"\nRUNNING tquakes-fetch\n"+"*"*50
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
# CHECK STATION
# ##################################################
qdisabled=False
out=System("links -dump '%s/action.php?action=checkstation&station_id=%s'"%(conf.WEBSERVER,station.station_id))

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

# ##################################################
# FETCHING EVENTS
# ##################################################
cmd="links -dump '%s/action.php?action=fetch&station_id=%s&numquakes=%d&fquakeid=%s'"%(conf.WEBSERVER,station.station_id,conf.NUMQUAKES,fquakeid)
#print cmd
out=System(cmd)
if 'No quakes' in out:
    print "No quakes available for fetching."
    exit(0)
print "Done."
print out

# SETTING STATION STATUS
System("links -dump '%s/action.php?action=status&station_id=%s&station_status=1'"%(conf.WEBSERVER,station.station_id))

# ##################################################
# CREATE QUAKES
# ##################################################
print "Creating directories of fetched quakes...",
for quake in out.split("\n"):
    quake=eval("dict(%s)"%quake.strip(" ,"))
    quakedir="data/quakes/%s"%quake["quakeid"]
    System("mkdir -p %s/.states"%(quakedir))
    System("cp -rd data/quakes/TEMPLATE/* %s"%(quakedir))
    System("cp -rd data/quakes/TEMPLATE/.[a-z]* %s"%(quakedir))
    if not len(fquakeid):System("date +%%s > %s/.fetch"%quakedir)
    fq=open(quakedir+"/quake.conf","w")
    for key in quake.keys():
        fq.write("%s='%s'\n"%(key,quake[key]))
    fq.close()
print "Fetched done from %s."%conf.WEBSERVER
