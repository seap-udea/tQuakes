from tquakes import *
print "*"*50+"\nRUNNING tquakes-fetch\n"+"*"*50

# ##################################################
# CONFIGURATION
# ##################################################
conf=loadConf("configuration")

# ##################################################
# LOAD STATION INFORMATION
# ##################################################
station=loadConf(".stationrc")
out=System("links -dump '%s/index.php?action=status&station_id=%s&station_status=1'"%(conf.WEBSERVER,station.station_id))

# ##################################################
# FECTH EVENTS
# ##################################################
qfetch=True
print "Fecthing %d events..."%conf.NUMQUAKES,
cmd="links -dump '%s/index.php?action=fetch&station_id=%s&numquakes=%d'"%(conf.WEBSERVER,station.station_id,conf.NUMQUAKES)
out=System(cmd)
print "Done."
print out
try:
    if int(out)==0:
        print "\tNo quakes."
        qfetch=False
    elif int(out)<0:
        print "\tThis station has been temporarily disabled."
        qfetch=False
except:
    pass

if not qfetch:exit(0)

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
    System("date +%%s > %s/.fetch"%quakedir)
    fq=open(quakedir+"/quake.conf","w")
    for key in quake.keys():
        fq.write("%s='%s'\n"%(key,quake[key]))
    fq.close()
print "Done."
