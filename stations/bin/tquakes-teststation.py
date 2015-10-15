from tquakes import *
# ##################################################
# CONFIGURATION
# ##################################################
conf=loadConf("configuration")

# ##################################################
# LOAD STATION INFORMATION
# ##################################################
station=loadConf(".stationrc")
print "*"*50+"\nRUNNING tquakes-test\n"+"*"*50

qfail=0

# ##################################################
# TESTING IF ETERNA IS RUNNING
# ##################################################
if not qfail:
    print "Testing Eterna..."
    System("rm data/quakes/TEST/*.prn data/quakes/TEST/*.prd")
    System("cd data/quakes/TEST;dosemu -t PREDICT.EXE &> test.log")
    out=System("cd data/quakes/TEST;cat *.prd |wc -l")
    System("rm data/quakes/TEST/*.prn data/quakes/TEST/*.prd")
    if int(out)>0:
        print "\tEterna is running."
    else:
        print "\tEterna is not running properly."
        qfail=1

# ##################################################
# TESTING CONNECTION
# ##################################################
if not qfail:
    print "Testing connection with webserver..."
    out=System("links -dump '%s/index.php?action=testconnection&station_id=%s'"%(conf.WEBSERVER,station.station_id))
    if 'Not Found' in out:
        print "\tConnection failed.".upper()
        qfail=1
    else:
        print "\tConnection established with server."

# ##################################################
# TESTING DATABASE ACCESS
# ##################################################
if not qfail:
    print "Testing database connection..."
    out=System("links -dump '%s/index.php?action=testdb&station_id=%s'"%(conf.WEBSERVER,station.station_id))
    try:
        if int(out)>0:
            print "\tDatabase query working."
    except:
        print "\tDatabase query not working.".upper()
        qfail=1

# ##################################################
# TESTING IF SERVER IS RECEIVING
# ##################################################
if not qfail:
    print "Testing database connection..."
    out=System("links -dump '%s/index.php?action=checkstation&station_id=%s'"%(conf.WEBSERVER,station.station_id))
    if int(out)>0:
        print "\tServer is receiving from this station."
        qrec=1
    else:
        print "\tServer is not receiving from this station.".upper()
        qrec=0

# ##################################################
# TESTING SSH CONNECTION
# ##################################################
if not qfail and qrec:
    print "Testing ssh connection..."
    out=System("scp .stationrc %s@%s:."%(conf.TQUSER,conf.DATASERVER))
    if "Could not" in out:
        print "\tConnection failed.".upper()
        qfail=1
    else:
        print "\tSuccesful connection."

if not qfail:
    print "ALL TEST PASSED."
