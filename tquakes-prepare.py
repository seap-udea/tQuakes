from tquakes import *
print "*"*50+"\nRUNNING tquakes-prepare\n"+"*"*50

# ##################################################
# CONFIGURATION
# ##################################################
conf=loadConf("configuration")

# ##################################################
# LOAD STATION INFORMATION
# ##################################################
station=loadConf(".stationrc")

# ##################################################
# GET UNCALCULATED QUAKES
# ##################################################
print "Searching fetched quakes..."
qlist=System("ls data/quakes/*/.fetch 2> /dev/null")
if len(qlist)==0:
    print "\tNo quakes found."
    exit(0)
else:
    nquakes=len(qlist.split("\n"))
    print "\t%d quakes found..."%nquakes

# ##################################################
# LOOP OVER QUAKES
# ##################################################
iq=1
for quake in qlist.split("\n"):
    search=re.search("\/(\w+)\/\.fetch",quake)
    quakeid=search.group(1)

    print "Preparing quake %d '%s'"%(iq,quakeid)

    # LOAD QUAKE INFORMATION
    quakedir="data/quakes/%s/"%quakeid
    quake=loadConf(quakedir+"quake.conf")

    if not os.path.lexists(quakedir+".fetch"):
        print "\tQuake already prepared by other process..."
        continue

    # ONLY PREPARE QUAKES NOT LOCKED
    lockfile=quakedir+".lock"
    if os.path.lexists(lockfile):
        print "\tQuake locked by another process"
        continue
    else:
        print "\tLocking quake"
        System("touch "+lockfile)

    # GET INITIAL DATE
    qdatetime=quake.qdate+" "+quake.qtime
    qdate=datetime.datetime.strptime(qdatetime,DATETIME_FORMAT)
    deltat=datetime.timedelta(days=conf.TIMEWIDTH)
    qdateini=qdate-deltat
    print "\tStarting date: ",qdateini

    # TIMESPAN IN HOURS
    timespan=2*conf.TIMEWIDTH*24

    # GENERATE ETERNA.INI FILES PER COMPONENT
    for component in 2,4,5:
        basename="%s%d"%(quakeid,component)
        eterna=open(quakedir+basename+".INI","w")
        content=genEternaIni(basename,
                             float(quake.qlat),
                             float(quake.qlon),
                             float(quake.qdepth)*-1000,
                             qdateini.year,qdateini.month,qdateini.day,
                             timespan,conf.SAMPLERATE,
                             component)
        eterna.write(content)
        eterna.close()

        fp=open(quakedir+"project%d"%component,"w")
        fp.write("%s"%basename)
        fp.close()

    print "\tEterna files generated..."

    # CHANGE STATUS OF QUAKE
    System("date +%%s > %s/.prepare"%quakedir)
    System("mv %s/.fetch %s/.states"%(quakedir,quakedir))

    # DELETE LOCKFILE
    System("rm "+lockfile)

    iq+=1
    if iq>2*conf.NUMQUAKES:break
