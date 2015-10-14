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
system("python tquakes-fetch.py")
system("python tquakes-prepare.py")
system("python tquakes-eterna.py")
system("python tquakes-analysis.py")
system("python tquakes-submit.py")
