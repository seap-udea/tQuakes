from tquakes import *
# ##################################################
# ARGUMENTS
# ##################################################
quakeid=argv[1]
print "\tRunning ETERNA for quake '%s'..."%quakeid

# ##################################################
# CONFIGURATION
# ##################################################
conf=loadConf("configuration")

# ##################################################
# LOAD STATION INFORMATION
# ##################################################
station=loadConf(".stationrc")
