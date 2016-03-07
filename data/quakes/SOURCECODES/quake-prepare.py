from tquakes import *
predict="util/Eterna/ETERNA34/PREDICT.EXE"
quakeid=argv[1]

# ##################################################
# CONFIGURATION
# ##################################################
conf=loadConf("configuration")
updateConf("common",conf)

# ##################################################
# PREPARE QUAKES
# ##################################################
# LOAD QUAKE INFORMATION
quakedir="data/quakes/%s/"%quakeid
quake=loadConf(quakedir+"quake.conf")

# GET INITIAL DATE
qdatetime=quake.qdate+" "+quake.qtime
qdate=datetime.datetime.strptime(qdatetime,DATETIME_FORMAT)
deltat=datetime.timedelta(days=conf.TIMEWIDTH)
qdateini=qdate-deltat
print "\tStarting date: ",qdateini

# TIMESPAN IN HOURS
timespan=2*conf.TIMEWIDTH*24

# COPY PREDICT
System("cp %s %s"%(predict,quakedir))

# GENERATE ETERNA.INI FILES PER COMPONENT
for component in COMPONENTS:
    basename="%s%d"%(quakeid,component)
    fp=open(quakedir+"project%d"%component,"w")
    fp.write("%s"%basename)
    fp.close()

    # COMPONENT 9 IS HORIZONTAL STRAIN AT 90 DEGRESS
    azimut=0
    if component==9:
        component=5
        azimut=90

    eterna=open(quakedir+basename+".INI","w")
    content=genEternaIni(basename,
                         float(quake.qlat),
                         float(quake.qlon),
                         float(quake.qdepth)*-1000,
                         qdateini.year,qdateini.month,qdateini.day,
                         timespan,conf.SAMPLERATE,
                         component,azimut)
    eterna.write(content)
    eterna.close()

print "\tEterna files generated..."
System("touch %s/.prepared"%quakedir)

