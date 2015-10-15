from tquakes import *
print "*"*50+"\nRUNNING tquakes-pipeline\n"+"*"*50

# ##################################################
# CONFIGURATION
# ##################################################
conf=loadConf("configuration")

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
# CHECK IF THERE IS PENDING QUAKES
out=System("ls -d data/quakes/??????? 2> /dev/null")
if out!="":
    print "Processing pending jobs.".upper()
    system("python tquakes-prepare.py")
    system("python tquakes-eterna.py")
    system("python tquakes-analysis.py")
    system("python tquakes-submit.py")

# FETCH
system("python tquakes-fetch.py")

# PROCESS
system("python tquakes-prepare.py")
system("python tquakes-eterna.py")
system("python tquakes-analysis.py")
system("python tquakes-submit.py")

# ##################################################
# STATUS
# ##################################################
out=System("links -dump '%s/index.php?action=status&station_id=%s&station_status=0'"%(conf.WEBSERVER,station.station_id))
