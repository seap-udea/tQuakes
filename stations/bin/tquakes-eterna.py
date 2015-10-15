from tquakes import *
print "*"*50+"\nRUNNING tquakes-eterna\n"+"*"*50
# ##################################################
# CONFIGURATION
# ##################################################
conf=loadConf("configuration")
predict="util/Eterna/ETERNA34/PREDICT.EXE"

# ##################################################
# LOAD STATION INFORMATION
# ##################################################
station=loadConf(".stationrc")

# ##################################################
# GET UNCALCULATED QUAKES
# ##################################################
print "Searching prepared quakes..."
qlist=System("ls data/quakes/*/.prepare 2> /dev/null")
if len(qlist)==0:
    print "\tNo quakes prepared."
    exit(0)
else:
    qlist=qlist.split("\n")
    nquakes=len(qlist)
    print "\t%d prepared quakes found..."%nquakes

out=System("links -dump '%s/index.php?action=status&station_id=%s&station_status=3'"%(conf.WEBSERVER,station.station_id))
# ##################################################
# LOOP OVER QUAKES
# ##################################################
iq=1
for quake in qlist:
    search=re.search("\/(\w+)\/\.prepare",quake)
    quakeid=search.group(1)
    print "Running Eterna for quake %d '%s'"%(iq,quakeid)

    # LOAD QUAKE INFORMATION
    quakedir="data/quakes/%s/"%quakeid
    quake=loadConf(quakedir+"quake.conf")

    if not os.path.lexists(quakedir+".prepare"):
        print "\tQuake already calculated by other process..."
        continue

    # ONLY PREPARE QUAKES NOT LOCKED
    lockfile=quakedir+".lock"
    if os.path.lexists(lockfile):
        print "\tQuake locked by another process"
        continue
    else:
        print "\tLocking quake"
        System("touch "+lockfile)

    # COPY PREDICT PROGRAM
    System("cp %s %s"%(predict,quakedir))

    # GENERATE ETERNA.INI FILES PER COMPONENT
    lquakeid=quakeid.lower()
    for component in 2,4,5:
        print "\tRunning component %d..."%component
        System("cd %s;cp project%d project"%(quakedir,
                                             component))
        System("cd %s;dosemu -t -quiet PREDICT.EXE &> %s%d.log"%(quakedir,
                                                                 quakeid,
                                                                 component))
        system("cd %s;bash prd2plain.sh %s%d.prd > %s%d.plain"%(quakedir,
                                                                lquakeid,component,
                                                                lquakeid,component))

    # GENERATE DATAFILES
    ic=0
    for component in 2,4,5:
        fileplain="%s/%s%d.plain"%(quakedir,lquakeid,component)
        datacomp=numpy.loadtxt(fileplain)
        System("rm "+fileplain)
        if ic:data=numpy.column_stack((data,datacomp[:,2]))
        else:data=datacomp[:,2]
        ic+=1

    # CALCULATE DATE
    times=[]
    for i in xrange(len(datacomp[:,0])):
        timestr="%d %06d"%(int(datacomp[i,0]),int(datacomp[i,1]))
        timedate=datetime.datetime.strptime(timestr,"%Y%m%d %H%M%S")
        timejd=date2jd(timedate)
        times+=[timejd]
    data=numpy.column_stack((times,data))
    numpy.savetxt("%s/%s.data"%(quakedir,quakeid),data)

    # 7ZIP RESULTS
    System("cd %s;tar cf %s-eterna.tar %s*.* %s*.* .states"%(quakedir,
                                              quakeid,quakeid,lquakeid))  
    System("cd %s;p7zip %s-eterna.tar"%(quakedir,quakeid))
    System("cd %s;rm PREDICT.EXE project* %s*.??? %s*.???"%(quakedir,
                                               quakeid,lquakeid))  
    
    # CHANGE STATUS OF QUAKE
    System("date +%%s > %s/.eterna"%quakedir)
    System("mv %s/.prepare %s/.states"%(quakedir,quakedir))
    
    # REPORT END OF CALCULATIONS
    print "\tReporting calculations..."
    out=System("links -dump '%s/index.php?action=report&station_id=%s&quakeid=%s'"%(conf.WEBSERVER,station.station_id,quakeid))

    # DELETE LOCKFILE
    System("rm "+lockfile)

    print "\tQuake done."

    iq+=1
    if iq>2*conf.NUMQUAKES:break
