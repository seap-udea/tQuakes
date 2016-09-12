from tquakes import *
import spiceypy as sp
sp.furnsh("util/kernels/kernels.mk")
v=False
v=1

# ############################################################
# LOAD DATABASE
# ############################################################
con=mdb.connect('localhost',CONF.DBUSER,CONF.DBPASSWORD,CONF.DBNAME)
db=con.cursor()

# ############################################################
# READ LIST OF QUAKES
# ############################################################
db.execute("select quakeid from QuakesMockTime;")
results=db.fetchall()

# ############################################################
# MODIFY PROPERTIES FOR EARTHQUAKES
# ############################################################
i=-1
for result in results:
    i+=1
    quakeid=result[0]
    if (i%10000)==0:print "Quake %d..."%i
    if i<99:continue

    if v:print "Quake: ",quakeid
    
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # OBTAIN INFORMATION
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    db.execute("select qdatetime,qlon,qlat,qdepth,hsun,hmoon from QuakesMockTime where quakeid='%s';"%quakeid)
    results=db.fetchall()
    qdatetime=results[0][0]
    qlon=float(results[0][1])
    qlat=float(results[0][2])
    qdepth=float(results[0][3])
    hsun=float(results[0][4])
    hmoon=float(results[0][5])

    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # CHANGE TIME
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    if v:print "\tOriginal date:",qdatetime
    qdate=datetime.datetime.strptime(qdatetime,DATETIME_FORMAT)
    dtime=qdate.strftime("%m/%d/%Y %H:%M:%S.%f")
    qet=sp.str2et(dtime)
    qjd=et2jd(qet)

    # RANDOM TIME-LAG
    qlag=1-2*numpy.random.random()
    qlag*=60
    if v:print "\tTimelag (days):",qlag

    # NEW DATE
    qjdnew=qjd+qlag;
    qdatetimenew=datetime.datetime.strftime(jd2date(qjdnew),DATETIME_FORMAT)
    if v:print "\tCorrected date:",qdatetimenew
    dtime=jd2date(qjdnew).strftime("%m/%d/%Y %H:%M:%S.%f")
    qetnew=sp.str2et(dtime)
    hmoon=bodyHA("MOON",qetnew,qlon)
    hsun=bodyHA("SUN",qetnew,qlon)

    # ====================
    # UPDATE DATABASE
    # ====================
    db.execute("update QuakesMockTime set qdatetime='%s',qjd='%.6f',qet='%.3f',hmoon='%.5f',hsun='%.5f' where quakeid='%s';"%(qdatetimenew,qjdnew,qetnew,hmoon,hsun,quakeid))
    con.commit()

    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # CHANGE LOCATION
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    if v:
        print "\tOriginal location (lon,lat,depth):",qlon,qlat,qdepth
    qshift=1-2*numpy.random.random()
    qshift*=100
    qdir=numpy.random.random()
    if qdir<1./3:
        qlat+=qshift*(360.0/4e4)
    elif qdir<2./3:
        qlon+=qshift*(360.0/4e4)
        hmoon=bodyHA("MOON",qet,qlon)
        hsun=bodyHA("SUN",qet,qlon)
    else:
        qdepth+=qshift/2.0
        if qdepth<0:qdepth=0.1
    if v:
        print "\tShift (km):",qshift
        print "\tDirection:",qdir
        print "\tNew location:",qlon,qlat,qdepth

    # ====================
    # UPDATE DATABASE
    # ====================
    db.execute("update QuakesMockSpace set qlon='%.3lf',qlat='%.2lf',qdepth='%.1lf',hmoon='%.5f',hsun='%.5f' where quakeid='%s';"%(qlon,qlat,qdepth,hmoon,hsun,quakeid))
    con.commit()
