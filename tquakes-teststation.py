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
# TESTING IF GOTIC 2 IS RUNNING
# ##################################################
if not qfail:
    print "Testing Gotic2..."
    cmd="cd data/quakes/TEST;./gotic2 < TEST.ini > TEST.pre"
    System(cmd)
    cmd="cd data/quakes/TEST;./gotic2 < TEST.inp > TEST.out"
    System(cmd)
    out=System("cd data/quakes/TEST;cat TEST.out |wc -l")
    System("cd data/quakes/TEST;rm *.pre *.out")
    if int(out)>0:
        print "\tGotic2 is running."
    else:
        print "\tGotic2 is not running properly."
        qfail=1

# ##################################################
# TESTING CONNECTION
# ##################################################
if not qfail:
    print "Testing connection with webserver..."
    out=System("links -dump '%s/action.php?action=testconnection&station_id=%s'"%(conf.WEBSERVER,station.station_id))
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
    out=System("links -dump '%s/action.php?action=testdb&station_id=%s'"%(conf.WEBSERVER,station.station_id))
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
    out=System("links -dump '%s/action.php?action=checkstation&station_id=%s'"%(conf.WEBSERVER,station.station_id))
    if int(out)>0:
        print "\tServer is receiving from this station."
        qrec=1
    else:
        print "\tServer is not receiving from this station.".upper()
        qfail=1
        qrec=0

# ##################################################
# TESTING SSH CONNECTION
# ##################################################
if not qfail and qrec:
    print "Testing ssh connection..."
    cmd="scp -i .keys/tquakes.pem -o 'StrictHostKeyChecking no' .stationrc %s@%s:tQuakes/"%(conf.TQUSER,conf.DATASERVER)
    print "\t\tExecuting:",cmd
    out=System(cmd)
    if "Could not" in out:
        print "\tConnection failed.".upper()
        qfail=1
    else:
        print "\tSuccesful connection."

if not qfail:
    print "ALL TEST PASSED."

exit(qfail)
