from tquakes import *
print "*"*50+"\nRUNNING tquakes-prepare\n"+"*"*50
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
# GET UNCALCULATED QUAKES
# ##################################################
if not len(fquakeid):
    print "Searching fetched quakes..."
    qlist=System("ls data/quakes/*/.fetch 2> /dev/null")
    if len(qlist)==0:
        print "\tNo quakes found."
        exit(0)
    else:
        nquakes=len(qlist.split("\n"))
        print "\t%d quakes found..."%nquakes
else:
    print "Preparing from list ",fquakeid
    qlist=""
    nquakes=0
    for fquake in fquakeid.split("."):
        qlist+="data/quakes/%s/.fetch\n"%fquake
        nquakes+=1
    qlist.strip("\n")

# SETTING STATUS
System("links -dump '%s/action.php?action=status&station_id=%s&station_status=2'"%(conf.WEBSERVER,station.station_id))

# ##################################################
# LOOP OVER QUAKES
# ##################################################
iq=1
for quake in qlist.split("\n"):
    if quake=="":continue
    search=re.search("\/(\w+)\/\.fetch",quake)
    quakeid=search.group(1)

    print "Preparing quake %d '%s'"%(iq,quakeid)

    # LOAD QUAKE INFORMATION
    quakedir="data/quakes/%s/"%quakeid
    quake=loadConf(quakedir+"quake.conf")

    if not os.path.lexists(quakedir+".fetch") and not len(fquakeid):
        print "\tQuake already prepared by other process..."
        continue

    # ONLY PREPARE QUAKES NOT LOCKED
    if not len(fquakeid):
        lockfile=quakedir+".lock"
        if os.path.lexists(lockfile):
            print "\tQuake locked by another process"
            continue
        else:
            print "\tLocking quake"
            System("touch "+lockfile)

    qdatetime=quake.qdate+" "+quake.qtime
    qdate=datetime.datetime.strptime(qdatetime,DATETIME_FORMAT)
    deltat=datetime.timedelta(days=conf.TIMEWIDTH)
    qdateini=qdate-deltat
    qdateend=qdate+deltat
    print "\tStarting date: ",qdateini
    print "\tEnd date: ",qdateend

    # TIMESPAN IN HOURS
    timespan=2*conf.TIMEWIDTH*24

    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # GENERATE INITIAL FILES
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # GENERATE ETERNA.INI FILES PER COMPONENT
    for gcomp,gcompn in GOTIC2.items():

        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        # BASENAME OF FILES
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        basename=quakeid+gcomp

        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        # DISTINGUISH COMPONENTS
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        azimut=0
        if gcomp=="HN":
            gcomp="HD"
        elif gcomp=="HE":
            gcomp="HD"
            azimut=90.0

        for gt,gtn in GOTIC2_TYPES.items():
            basegotic2=basename+gt
            content1,content2=genGotic2Ini(quakeid,
                                           basegotic2,
                                           float(quake.qlat),
                                           float(quake.qlon),
                                           float(quake.qdepth)*-1000,
                                           qdateini,qdateend,
                                           conf.SAMPLERATE,
                                           gcomp,
                                           azimut,
                                           gtn)
            
            # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
            # WRITE CONFIGURATION
            # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
            gotic2=open(quakedir+basename+".ini","w")
            gotic2.write(content1)
            gotic2.close()
            
            gotic2=open(quakedir+basegotic2+".inp","w")
            gotic2.write(content2)
            gotic2.close()
            
    print "\tGotic2 files generated..."

    if not len(fquakeid):
        # CHANGE STATUS OF QUAKE
        System("date +%%s > %s/.prepare"%quakedir)
        System("mv %s/.fetch %s/.states"%(quakedir,quakedir))
        # DELETE LOCKFILE
        System("rm "+lockfile)

    iq+=1
