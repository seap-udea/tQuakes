from tquakes import *
import spiceypy as sp
sp.furnsh("util/kernels/kernels.mk")

# ############################################################
# LOAD DATABASE
# ############################################################
tQuakes,connection=loadDatabase()
db=connection.cursor()

i=0
f=open("failed.dat","w")
for quakeid in tQuakes['Quakes']['rows'].keys():
    quake=tQuakes['Quakes']['rows'][quakeid]
    if ((i%1000)==0):print "Quake %d %s..."%(i,quake["quakeid"])
    #if quake["quakeid"]!="0004H1O":continue
    i+=1
    
    """
    GENERATE SUBDATA: A chunk of <quakeid>.data file around the time
    of earthquake occurence.
    """

    quakeid=quake["quakeid"]
    qjd=float(quake["qjd"])
    #print "Quake: ",quakeid

    #tini=timeit()
    #print "Copying files..."
    if not os.path.isfile("/home/tquakes/tQuakes/%s-max.data"%quakeid) or 1:

        System("cp /home/tquakes/tQuakes/%s-eterna.* tmp"%quakeid)
        
        #print "Extracting file..."
        System("cd tmp;p7zip -d %s-eterna.tar.7z;tar xf %s-eterna.tar %s.data"%(quakeid,quakeid,quakeid))
        System("cd tmp;rm %s*.tar"%quakeid)
        
        #print "Reading data..."
        try:
            data=numpy.loadtxt("tmp/%s.data"%quakeid)
        except:
            f.write("%s\n"%quakeid)
            continue
        
        #Getting maxima and minima for components
        ic=0
        t=data[:,0]-qjd

        table=numpy.array([0,0])
        for component in COMPONENTS:
            ic+=1
            #if component!=4 and component!=5:continue
            s=data[:,ic]

            # SEMIDIURNAL LEVEL PEAKS
            tmb,smb,tMb,sMb=signalBoundary(t,s)

            # CHOOSE THE LAST MONTH
            cond=abs(tMb)<40

            # STORE MAXIMA
            line=numpy.array([ic,999999999])
            subtable=numpy.column_stack((tMb[cond],sMb[cond]))
            stable=numpy.vstack((line,subtable))
            table=numpy.vstack((table,stable))

        numpy.savetxt("tmp/%s-max.data"%quakeid,table)
        
        #print "Copying file..."
        System("mv tmp/%s-max.data /home/tquakes/tQuakes/"%quakeid)
        System("rm -r tmp/*")
    
    #tend=timeit()
    #print "Time: ",tend-tini
    #break

    #print "Compute astronomical phases..."
    
    """
    # DATE AND TIME
    qjd=float(quake["qjd"])
    dtime=quake["qdatetime"]
    et=jd2et(qjd)
    print "Original:"
    print "\tDate: ",dtime
    print "\tET: ",et
    print "\tJD: ",qjd

    print "\n...Converting qjd to date...\n"
    
    print "Converted:"
    dtime=jd2date(float(qjd))
    dtime=dtime.strftime("%m/%d/%Y %H:%M:%S.%f")
    et=sp.str2et(dtime)
    qjd=et2jd(et)
    print "\tDate: ",dtime
    print "\tET:",et
    print "\tJD: %.6f"%qjd
    """

    """
    qjd=float(quake["qjd"])
    dtime=quake["qdatetime"]
    print "\tJD: %.6f"%qjd
    print "\tDate time: ",dtime
    """

    """
    # PROCEDURE TO SET ET
    dtime=datetime.datetime.strptime(quake["qdatetime"],DATETIME_FORMAT)
    dtime=dtime.strftime("%m/%d/%Y %H:%M:%S.%f")
    et=sp.str2et(dtime)
    qjd=et2jd(et)
    qet="%.3f"%et
    """

    """
    print "\tDate time SPICE format: ",dtime
    print "\tJD: %.6f"%qjd
    print "\tET: %s"%qet
    """
    
    """
    #print "Updating %s..."%quakeid
    nquakestr=quake2str(float(quake["qlat"]),float(quake["qlon"]),float(quake["qdepth"]),qjd)
    #print "NEW STR:",nquakestr

    sql="update Quakes set quakestr='%s',qet='%s' where quakeid='%s'"%(nquakestr,qet,quakeid)
    db.execute(sql)
    connection.commit()
    """
    #break

f.close()
