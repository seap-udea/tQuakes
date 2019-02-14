from tquakes import *
# ##################################################
# ARGUMENTS
# ##################################################
quakeid=argv[1]
print "Running GOTIC2 for quake '%s'..."%quakeid

# ##################################################
# CONFIGURATION
# ##################################################
conf=loadConf("configuration")
gotic2="./gotic2"

# ##################################################
# LOAD STATION INFORMATION
# ##################################################
station=loadConf(".stationrc")
 
# ##################################################
# RUN ETERNA
# ##################################################
i=0
System("rm -rf %s.*"%quakeid)
for gcomp,gcompn in GOTIC2.items():

    print "\tRunning component %s:"%gcomp
    basename=quakeid+gcomp

    print "\t\tRunning gotic2..."
    cmd="%s < %s.ini > %s.pre &> %s.log"%(gotic2,basename,basename,basename)
    System(cmd)

    #BODY, OCEANIC AND BOTH
    for gt,gtn in GOTIC2_TYPES.items():

        #Create output file
        basegotic2=basename+gt
        system("cp %s.pre %s.pre"%(basename,basegotic2))

        print "\t\tPreparing the output for component %s"%gt
        cmd="%s < %s.inp &> %s.log"%(gotic2,basegotic2,basegotic2)
        System(cmd)

        #Reading file
        table=readPlain(basegotic2+".out")
        if i==0:data=table[:,0]
        data=numpy.column_stack((data,table[:,1:]))
        i+=1

# ##################################################
# SAVE DATA
# ##################################################
numpy.savetxt("%s.data"%(quakeid),data,fmt="%25.17e",header="0:jd "+GOTIC2_HEADER)
System("gzip %s.data"%quakeid)
print "Quake done."
