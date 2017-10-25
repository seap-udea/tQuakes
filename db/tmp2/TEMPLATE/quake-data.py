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
# RUN ETERNA
# ##################################################
# GENERATE ETERNA.INI FILES PER COMPONENT

lquakeid=quakeid.lower()
for component in COMPONENTS:
    print "\t\tRunning component %d..."%component
    system("bash prd2plain.sh %s%d.prd > %s%d.plain"%(lquakeid,component,
                                                      lquakeid,component))

# GENERATE DATAFILES
print "\tGenerating plain data file..."
ic=0
for component in COMPONENTS:
    fileplain="%s%d.plain"%(lquakeid,component)
    try:
        datacomp=numpy.loadtxt(fileplain)
    except:
        System("touch .fail")
        exit(1)

    System("rm "+fileplain)
    if ic:data=numpy.column_stack((data,datacomp[:,2]))
    else:data=datacomp[:,2]
    ic+=1

# CREATE ADDITIONAL COLUMNS

# MAGNITUDE OF THE HORIZONTAL STRAIN
hsm=numpy.sqrt(data[:,4]**2+data[:,5]**2)

# ANGLE OF THE HORIZONTAL STRAIN (0 IS EAST, 90 NORTH, 180 WEST)
hst=numpy.arctan2(data[:,4],data[:,5])*RAD
data=numpy.column_stack((data,hsm,hst))

# CALCULATE DATE
times=[]
for i in xrange(len(datacomp[:,0])):
    timestr="%d %06d"%(int(datacomp[i,0]),int(datacomp[i,1]))
    timedate=datetime.datetime.strptime(timestr,"%Y%m%d %H%M%S")
    timejd=date2jd(timedate)
    times+=[timejd]

data=numpy.column_stack((times,data))
numpy.savetxt("%s.data"%(quakeid),data)

print "\tQuake done."
