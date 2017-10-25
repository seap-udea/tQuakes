from tquakes import *
from matplotlib import use
use('Agg')
import matplotlib.pyplot as plt
import spiceypy as sp
sp.furnsh("util/kernels/kernels.mk")

# ############################################################
# LOAD DATABASE
# ############################################################
tQuakes,connection=loadDatabase()
db=connection.cursor()

vvv=0

i=0
for quakeid in tQuakes['Quakes']['rows'].keys():

    quake=tQuakes['Quakes']['rows'][quakeid]
    if int(quake["astatus"])<4 or quake["aphases"]!='':continue
    if ((i%1000)==0):print "Quake %d %s..."%(i,quake["quakeid"])
    i+=1

    quakeid=quake["quakeid"]
    cquake=loadConf("/home/tquakes/tQuakes/%s.conf"%quakeid)

    try:
        aphases=cquake.aphases
        sql="update Quakes set aphases='%s' where quakeid='%s'"%(cquake.aphases,quakeid)
        db.execute(sql)
        connection.commit()
    except:
        print "No aphases for quake '%s'..."%quakeid
        sql="update Quakes set astatus='0',stationid='',adatetime='',calctime1='',calctime2='',calctime3='',qsignal='',qphases='',aphases='' where quakeid='%s'"%(quakeid)
        db.execute(sql)
        connection.commit()

