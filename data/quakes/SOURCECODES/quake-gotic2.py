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

#HEADER
header=""
n=1
for k,gn in GOTIC2.items():
    gname=k
    if k=="HN" or k=="HE":gname="HD"
    g=GOTIC2_COLUMNS[gname]
    for gt,gtn in GOTIC2_TYPES.items():
        for f in g:
            header+="%d:%s/%s/%s "%(n,k,gt,f)
            n+=1
 
# ##################################################
# RUN ETERNA
# ##################################################
i=0
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
numpy.savetxt("%s.data"%(quakeid),data,header=header)
System("gzip %s.data"%quakeid)
print "Quake done."
