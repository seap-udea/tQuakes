from tquakes import *
import spiceypy as sp
import time
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
tstart=time.time()
for result in results:
    i+=1
    quakeid=result[0]
    if (i%10000)==0:
        tend=time.time()
        tperq=tend-tstart
        tstart=tend
        print "Quake %d... (duration %.2f min)"%(i,tperq)

    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # MOCK TIME
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    db.execute("select qdatetime,qlon,qlat,qet from QuakesMockTime where quakeid='%s';"%quakeid)
    results=db.fetchall()
    qdatetime=results[0][0]
    qlon=float(results[0][1])
    qlat=float(results[0][2])
    qet=float(results[0][3])

    qdate=datetime.datetime.strptime(qdatetime,DATETIME_FORMAT)
    dtime=qdate.strftime("%m/%d/%Y %H:%M:%S.%f")
    qetnew=sp.str2et(dtime)
    qjdnew=et2jd(qetnew)
    hmoon=bodyHA("MOON",qetnew,qlon)
    hsun=bodyHA("SUN",qetnew,qlon)

    db.execute("update QuakesMockTime set qjd='%.6f',qet='%.3f',hmoon='%.5f',hsun='%.5f' where quakeid='%s';"%(qjdnew,qetnew,hmoon,hsun,quakeid))
    con.commit()

    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # MOCK SPACE
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    db.execute("select qdatetime,qlon,qlat,qet from QuakesMockSpace where quakeid='%s';"%quakeid)
    results=db.fetchall()
    qdatetime=results[0][0]
    qlon=float(results[0][1])
    qlat=float(results[0][2])
    qet=float(results[0][3])

    hmoon=bodyHA("MOON",qet,qlon)
    hsun=bodyHA("SUN",qet,qlon)
    
    db.execute("update QuakesMockSpace set hmoon='%.5f',hsun='%.5f' where quakeid='%s';"%(hmoon,hsun,quakeid))
    con.commit()
    
