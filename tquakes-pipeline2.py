from tquakes import *
print "*"*50+"\nRUNNING tquakes-pipeline\n"+"*"*50

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
# RANDOM START
# ##################################################
tsleep=numpy.random.randint(2,10)
print "Sleeping %d seconds before start..."%tsleep
sleep(tsleep)

# ##################################################
# PIPELINE
# ##################################################

# CHECK STATION
System("rm scratch/*.err &> /dev/null")

# CHECK STATION
qdisabled=False
out=System("links -dump '%s/action.php?action=checkstation&station_id=%s'"%(conf.WEBSERVER,station.station_id))

if int(out)>0:
    print "Station enabled."
elif int(out)==0:

    # REMOVE REMAINING QUAKES
    System("rm -r data/quakes/???????")
    # REMOVE SERVER SIGNATURE
    system("ssh-keygen -f \"$HOME/.ssh/known_hosts\" -R %s"%conf.DATASERVER)

    print "Station disabled."
    qdisabled=True
elif int(out)==-1:
    print "Station not recognized."
    qdisabled=True

# IF STATION IS DISABLED STOP
if qdisabled:exit(0)

# CHECK IF THERE IS PENDING QUAKES
out=System("python tquakes-fetch.py")
quakes=out
System("python tquakes-prepare.py "+quakes)
system("python tquakes-run.py "+quakes)
system("python tquakes-analysis.py "+quakes)
system("python tquakes-submit.py "+quakes)

# ##################################################
# STATUS
# ##################################################
out=System("links -dump '%s/action.php?action=status&station_id=%s&station_status=0'"%(conf.WEBSERVER,station.station_id))
