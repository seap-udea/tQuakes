# ############################################################
# IMPORT TOOLS
# ############################################################
from tquakes import *
from matplotlib import use
use('Agg')
import matplotlib.pyplot as plt
execfile("%s.conf"%BASENAME)

# ############################################################
# CONNECT TO DATABASE
# ############################################################
connection=connectDatabase()
db=connection.cursor()

# ############################################################
# READ CLUSTER DATABASE
# ############################################################
icent=19
inicent=1900
jd1=date2jd(datetime.datetime(1900,1,1,0,0,0))
jd2=date2jd(datetime.datetime(2000,1,1,0,0,0))
search="where Ml+0>%.1f and qjd+0>%.5f and qjd+0<%.5f order by qjd+0 desc, Ml+0 desc"%(Mc,jd1,jd2)
qids,quakes=getQuakes(search,db)
nquakes=len(qids)
print "%d earthquakes read..."%nquakes

# ############################################################
# GENERATE CATALOGUE
# ############################################################
print "Preparing catalogue..."
fc=open("catalogue.dat","w")
for iq in xrange(nquakes):
    dt=jd2date(quakes[iq,0])
    # year, month, day, hour, minute, lat, lon, depth, mag
    fc.write("%-5d%-4d%-4d%-4d%-4d%-10.3f%-10.3f%-10.3f%-10.2f\n"%(dt.year,dt.month,dt.day,dt.hour,dt.minute,
                                                                   quakes[iq,1],abs(quakes[iq,2]),quakes[iq,3],quakes[iq,4]))
fc.close()

# ############################################################
# RUN CLUSTER ANALYSIS
# ############################################################
print "Declustering..."
if not qskip:
    if not os.path.lexists("%s.out"%clprog):
        print "Compiling declustering program..."
        system("gfortran %s.f -o %s.out"%(clprog,clprog))

    system("rm cluster.* 2> /dev/null")
    fc=open("cluster.conf","w")
    fc.write("""%d
    %d
    0
    99
    %.1f
    %.1f
    1
    # ##################################################
    # PARAMETERS
    # ##################################################
    ICENT (CENTURY)
    INICENT (INITIAL YEAR OF CENTURY)
    INITIAL YEAR (NO CENTURY, E.G. 93 INSTEAD OF 1993)
    END YEAR (IDEM)
    SPECIFY MINIMUM MAGNITUDE TO ACCEPT
    SPECIFY KEY PARAMETERS
    SPECIFY HANDLING OF EPICENTRAL ERRORS: location errors: (1=IGNORE ERRORS, 2=ADJUST FOR ERRORS)
    """%(icent,inicent,Mc,Rf))
    fc.close()
    system("%s.out"%clprog)

# ############################################################
# READ CLUSTERS
# ############################################################

# ############################################################
# READ EARTHQUAKES
# ############################################################
fc=open("cluster.ano","r")
i=1
clusters=dict()
for line in fc:
    line=line.strip("\r\n")
    props=line.split()

    # BASIC PROPERTIES
    qdatetime=datetime.datetime.strptime(props[0]+props[1],"%y%m%d%H%M")
    qjd=date2jd(qdatetime)
    qlat=s2d(int(props[2]),float(props[3]),0)
    qlon=s2d(int(props[4]),float(props[5]),0)
    qdep=float(props[6])
    Ml=float(props[7])
    cluster=props[-2]

    # """
    print "Quake ",i
    print "\tDate: ",qdatetime
    print "\tJD: ",qjd
    print "\tLat: ",qlat
    print "\tLon: ",qlon
    print "\tDepth: ",qdep
    print "\tMl: ",Ml
    print "\tCluster: ",cluster
    # """
    
    # COMPARE DATETIME
    qcomptime=datetime.datetime.strftime(qdatetime,DATETIME_FORMAT)
    print qcomptime

    # SAVE CLUSTER
    icluster="%05d"%int(cluster)

    if icluster not in clusters.keys():
        q=1
        while q:
            clusterid=randomStr(5,justnumbers=True)
            q=db.execute("select clusterid from Clusters where clusterid='%s';"%clusterid)
        clusters[icluster]=[clusterid,1]
    else:
        clusters[icluster][1]+=1

    i+=1

print clusters
