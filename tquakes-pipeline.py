from tquakes import *
# ##################################################
# CONFIGURATION
# ##################################################
conf=loadConf("configuration")
updateConf("common",conf)
predict="util/Eterna/ETERNA34/PREDICT.EXE"

# ##################################################
# GET UNCALCULATED QUAKES
# ##################################################
print "Searching prepared quakes..."
qlist=System("ls data/quakes/*/.prepared 2> /dev/null")
if len(qlist)==0:
    print "\tNo quakes prepared."
    exit(0)
else:
    qlist=qlist.split("\n")
    nquakes=len(qlist)
    print "\t%d prepared quakes found..."%nquakes

# ##################################################
# LOOP OVER QUAKES
# ##################################################
iq=1
for quake in qlist:
    search=re.search("\/(\w+)\/\.prepared",quake)
    quakeid=search.group(1)
    lquakeid=quakeid.lower()

    # LOAD QUAKE INFORMATION
    quakedir="data/quakes/%s/"%quakeid
    quake=loadConf(quakedir+"quake.conf")

    # COPY PREDICT PROGRAM
    System("cp %s %s"%(predict,quakedir))

    # TIME
    time_start=timeit()
    print "\tStarting time: ",time_start

    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # RUN ETERNA
    print "Running Eterna for quake %d '%s'"%(iq,quakeid)
    out=System("cd %s;python quake-eterna.py %s >> quake.log"%(quakedir,quakeid))
    print out
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    # TIME
    time_end=timeit()
    print "\tEnd time: ",time_end
    deltat=time_end-time_start
    print "\tTime elapsed: ",deltat
    system("echo 'calctime1=\"%.2f\"' >>  %s/quake.conf"%(deltat,quakedir))

    # 7ZIP RESULTS
    System("cd %s;tar cf %s-eterna.tar %s*.* %s*.* quake.conf quake.log"%(quakedir,
                                                             quakeid,quakeid,lquakeid))  
    System("cd %s;p7zip %s-eterna.tar"%(quakedir,quakeid))
    System("cd %s;rm PREDICT.EXE project* %s*.??? %s*.???"%(quakedir,
                                                            quakeid,lquakeid))  

    # TIME
    time_start=timeit()
    print "\tStarting time: ",time_start

    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # RUN ANALYSIS
    print "Analysing results %d '%s'"%(iq,quakeid)
    out=System("cd %s;python quake-analysis.py %s >> quake.log"%(quakedir,quakeid))
    quake=loadConf(quakedir+"quake.conf")
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    # TIME
    time_end=timeit()
    print "\tEnd time: ",time_end
    deltat=time_end-time_start
    print "\tTime elapsed: ",deltat
    system("echo 'calctime2=\"%.4f\"' >>  %s/quake.conf"%(deltat,quakedir))

    # COMPRESS
    System("cd %s;tar cf %s-analysis.tar %s*-ff*.* quake.conf quake.log .states"%(quakedir,
                                                                                  quakeid,quakeid))  
    System("cd %s;p7zip %s-analysis.tar"%(quakedir,quakeid))
    System("cd %s;rm *ff*"%(quakedir))
    System("cd %s;cp quake.conf %s.conf"%(quakedir,quakeid))

    # TIME
    time_start=timeit()
    print "\tStarting time: ",time_start

    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # SUBMIT RESULTS
    # SUBMIT DATA
    print "Copying results %d '%s'"%(iq,quakeid)
    system("cp -r %s/%s.conf %s/*.7z data/tQuakes"%(quakedir,quakeid,quakedir))
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    # TIME
    time_end=timeit()
    print "\tEnd time: ",time_end
    deltat=time_end-time_start
    print "\tTime elapsed: ",deltat
    system("echo 'calctime3=\"%.4f\"' >>  data/tQuakes/%s.conf"%(deltat,quakeid))

    # Removing quake directory
    system("rm -r %s"%quakedir)

    # STORING TIME
    iq+=1
