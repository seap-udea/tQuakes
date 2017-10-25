from tquakes import *
import spiceypy as sp
sp.furnsh("util/kernels/kernels.mk")

# ############################################################
# LOAD DATABASE
# ############################################################
tQuakes,connection=loadDatabase()
db=connection.cursor()

i=0

for quakeid in tQuakes['Quakes']['rows'].keys():
    quake=tQuakes['Quakes']['rows'][quakeid]
    if ((i%1000)==0):print "Quake %d %s..."%(i,quake["quakeid"])
    i+=1
    #if quake["quakeid"]!="0004H1O":continue
    
    """-

    Determine the hour angle of the Sun and the Moon at the time of
    Earthquake.  This will help us to calculate the diurnal phase.

    """

    # COMPUTE THE POSITION OF THE OBSERVER ON THE SURFACE OF THE EARTH
    #print "Updating %s..."%quakeid
    #print "Date and time: ",quake["qdatetime"]
    qet=float(quake["qet"])
    qlat=float(quake["qlat"])
    qlon=float(quake["qlon"])
    qdepth=float(quake["qdepth"])

    # H of the Moon & Sun
    hmoon=bodyHA("MOON",qet,qlon)
    hsun=bodyHA("SUN",qet,qlon)
    #print "Hour angle of the Moon: ",hmoon
    #print "Hour angle of the Sun: ",hsun

    sql="update Quakes set hmoon='%.5f',hsun='%.5f' where quakeid='%s'"%(hmoon,
                                                                         hsun,
                                                                         quakeid)
    db.execute(sql)
    connection.commit()

    #break

