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
system("python %s/tquakes-fetch.py"%conf.BINDIR)
system("python %s/tquakes-prepare.py"%conf.BINDIR)
system("python %s/tquakes-eterna.py"%conf.BINDIR)
system("python %s/tquakes-analysis.py"%conf.BINDIR)
system("python %s/tquakes-submit.py"%conf.BINDIR)

# ##################################################
# STATUS
# ##################################################
out=System("links -dump '%s/index.php?action=status&station_id=%s&station_status=0'"%(conf.WEBSERVER,station.station_id))
