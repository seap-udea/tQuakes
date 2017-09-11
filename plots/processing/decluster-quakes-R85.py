# ############################################################
# IMPORT TOOLS
# ############################################################
from tquakes import *
from matplotlib import use
use('Agg')
import matplotlib.pyplot as plt
execfile("%s.conf"%BASENAME)

def decluster(inicent):
    # ############################################################
    # CONNECT TO DATABASE
    # ############################################################
    connection=connectDatabase()
    db=connection.cursor()
    
    # ############################################################
    # READ CLUSTER DATABASE
    # ############################################################
    icent="%d"%inicent
    icent=int(icent[:2])
    jd1=date2jd(datetime.datetime(inicent,1,1,0,0,0))
    jd2=date2jd(datetime.datetime(inicent+100,1,1,0,0,0))
    search="where Ml+0>%.1f and qjd+0>%.5f and qjd+0<%.5f and cluster1 is NULL order by qjd+0 asc, Ml+0 desc"%(Mc,jd1,jd2)
    qids,quakes=getQuakes(search,db)
    nquakes=len(qids)
    print "Declustering %d earthquakes from century %d..."%(nquakes,inicent)

    # ############################################################
    # GENERATE CATALOGUE
    # ############################################################
    print "Preparing catalogue..."
    fc=open("catalogue.dat","w")
    for iq in xrange(nquakes):
        dt=jd2date(quakes[iq,0])
        # year, month, day, hour, minute, lat, lon, depth, mag
        fc.write("%-5d%-4d%-4d%-4d%-4d%-10.3f%-10.3f%-10.3f%-10.2f%-10s\n"%(dt.year,dt.month,dt.day,dt.hour,dt.minute,
                                                                            quakes[iq,1],abs(quakes[iq,2]),quakes[iq,3],quakes[iq,4],
                                                                            qids[iq]))
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
    # UPDATE EARTHQUAKES
    # ############################################################
    print>>stderr,"Updating %d earthquakes..."%(nquakes),
    fc=open("cluster.ano","r")
    i=1
    clusters=dict()
    for line in fc:
        iq=i-1
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
        quakeid=qids[iq]

        # CLUSTERID
        if cluster!="0":
            # STORE CLUSTER INFORMATION
            icluster="%05d"%int(cluster)
            if icluster not in clusters.keys():
                q=1
                while q:
                    clusterid=randomStr(5,numbers=False)
                    q=db.execute("select clusterid from Clusters where clusterid='%s';"%clusterid)
                clusters[icluster]=[clusterid,1]
                sql="insert into Clusters (clusterid) values ('%s')"%(clusterid)
                db.execute(sql)
                connection.commit()
            else:
                clusterid=clusters[icluster][0]
                clusters[icluster][1]+=1
        else:clusterid="0"

        """
        if quakeid=='ZISO7IY' and 0:
            print "Quake ",i
            print "\tQuakeid: ",quakeid
            print "\tDate: ",qdatetime
            print "\tJD: ",qjd
            print "\tLat: ",qlat
            print "\tLon: ",qlon
            print "\tDepth: ",qdep
            print "\tMl: ",Ml
            print "\tCluster: ",cluster
            print "\tClusterid: ",clusterid
        # """

        # SAVE QUAKE INFORMATION
        sql="update Quakes set cluster1='%s' where quakeid='%s'"%(clusterid,quakeid)
        db.execute(sql)

        i+=1

    nclusters=len(clusters.keys())
    print "Done."
    # ############################################################
    # UPDATE CLUSTERS
    # ############################################################
    print "Updating %d clusters (this may take a while)..."%(nclusters)
    fc=open("cluster.out","r")
    qstart=False
    i=1
    for line in fc:
        # GET LINE INFORMATION
        line=line.strip("\r\n")
        if '###' not in line and not qstart:continue
        if '###' in line:
            qstart=True
            continue

        if i%10==0:
            print "Storing cluster %d/%d..."%(i,nclusters)

        # GET CLUSTER INFORMATION
        c=dict2obj(dict())
        props=line.split()
        icluster="%05d"%int(props[1])
        c.clusterid=clusters[icluster][0]
        c.cluster_type="R85"
        c.cluster_pars="%.1f;%.1f;"%(Mc,Rf)
        c.numquakes=int(props[5])

        c.qlatequiv=s2d(int(props[6]),float(props[7]),0)
        c.qlonequiv=s2d(int(props[8]),float(props[9]),0)
        c.qdepequiv=float(props[10])
        c.Mlequiv=float(props[11])

        # GET ADDITIONAL INFORMATION
        c.qjdmean=mysqlSimple("select avg(qjd) from Quakes where cluster1='%s'"%c.clusterid,db)
        c.qduration=mysqlSimple("select max(qjd)-min(qjd) from Quakes where cluster1='%s'"%c.clusterid,db)

        # GET IMPORTANT QUAKES IN CLUSTER
        c.firstquakeid=mysqlSimple("select quakeid from Quakes where cluster1='%s' order by qjd+0 asc"%c.clusterid,db)
        c.maxquakeid=mysqlSimple("select quakeid from Quakes where cluster1='%s' order by Ml+0 desc"%c.clusterid,db)
        db.execute("update Quakes set cluster1='-%s' where quakeid='%s'"%(c.clusterid,c.maxquakeid))

        # OTHER RESULTS
        # PCT(F): 
        # DT: time difference between largest and second largest
        # DM: Drop in magnitude between largest and second largest
        c.cluster_results="%d;%.3f;%.2f;"%(int(props[16]),float(props[17]),float(props[18]))

        """
        print "\tiCluster: ",icluster
        print "\tC.Clusterid: ",c.clusterid
        print "\tCluster pars: ",c.cluster_pars
        print "\tNumber of Earthquakes: ",c.numquakes
        print "\tEvent centered at: ",jd2date(c.qjdmean)
        print "\tDuration: ",c.qduration
        print "\tEquivalent properties: "
        print "\t\tqlat: ",c.qlatequiv
        print "\t\tqlon: ",c.qlonequiv
        print "\t\tqdep: ",c.qdepequiv
        print "\t\tMl: ",c.Mlequiv
        print "\tFirst quake: ",c.firstquakeid
        print "\tLargest quake: ",c.maxquakeid
        print "\tAdditional results: ",c.cluster_results
        # """

        # UPDATE DATABASE
        sql="update Clusters set "
        for key in c.__dict__.keys():
            sql+="%s='%s',"%(key,str(c.__dict__[key]))
        sql=sql.strip(",")
        sql+="where clusterid='%s'"%c.clusterid
        db.execute(sql)
        
        print "\n"
        print "Total number of quakes:",nquakes
        print "Total number of clustered quakes:",nclustered


        i+=1

    fc.close()
    connection.commit()
    return db

db=decluster(1900)
db=decluster(2000)
nclustered=mysqlSimple("select count(quakeid) from Quakes where cluster1<>'0'",db)
ndeclustered=mysqlSimple("select count(quakeid) from Quakes where cluster1='0' or cluster1 like '-%'",db)
print>>stderr,"Total number of clustered quakes:",nclustered
print>>stderr,"Total number of declustered quakes:",ndeclustered
