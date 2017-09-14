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
# LOAD STATION INFORMATION
# ##################################################
station=loadConf(".stationrc")

# ##################################################
# RUN ETERNA
# ##################################################
# GENERATE ETERNA.INI FILES PER COMPONENT

lquakeid=quakeid.lower()
for component in COMPONENTS:
    print "\t\tRunning component %d..."%component
    System("cp project%d project"%(component))
    System("dosemu -t -quiet PREDICT.EXE &> %s%d.log"%(quakeid,component))
    #os.popen("dosemu -t -quiet PREDICT.EXE &> %s%d.log"%(quakeid,component)).read()
    #os.popen("python a.py").read()
    #system("python a.py")
    system("bash prd2plain.sh %s%d.prd > %s%d.plain"%(lquakeid,component,
                                                      lquakeid,component))

# GENERATE DATAFILES
print "\tGenerating plain data file..."
ic=0
for component in COMPONENTS:
    fileplain="%s%d.plain"%(lquakeid,component)
    datacomp=numpy.loadtxt(fileplain)
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
