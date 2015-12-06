import MySQLdb as mdb
import csv,datetime,commands,re,os,numpy,cmath,time as timing
from sys import exit,argv,stderr
from util.jdcal import *

# ######################################################################
# MACROS
# ######################################################################
system=os.system
PI=numpy.pi
sleep=timing.sleep
timeit=timing.time
DEG=PI/180
RAD=180/PI

# ######################################################################
# GLOBAL
# ######################################################################
FIELDS_CSV2DB={'Fecha':'qdate','Hora UTC':'qtime','Latitud':'qlat','Longitud':'qlon','Profundidad':'qdepth',
               'Magnitudl':'Ml','Magnitudw':'Mw','Departamento':'departamento','Municipio':'municipio',
               '# Estaciones':'numstations','Rms':'timerms','Gap':'gap','Error Latitud (Km)':'qlaterr',
               'Error Longitud (Km)':'qlonerr','Error Profundidad (Km)':'qdeptherr','Estado':'status'};

FIELDS_CSV=['Fecha','Hora UTC','Latitud','Longitud','Profundidad','Magnitudl','Magnitudw','Departamento',
            'Municipio','# Estaciones','Rms','Gap','Error Latitud (Km)','Error Longitud (Km)',
            'Error Profundidad (Km)','Estado']

FIELDS_DB=[]
FIELDS_DB2CSV=dict()
for field in FIELDS_CSV:
    dbfield=FIELDS_CSV2DB[field]
    FIELDS_DB+=[dbfield]
    FIELDS_DB2CSV[dbfield]=field
FIELDS_DB+=["quakeid","quakestr",
            "qdatetime","qjd",
            "astatus","adatetime","stationid"]

FIELDSTXT="("
FIELDSUP=""
for field in FIELDS_DB:
    FIELDSTXT+="%s,"%field
    FIELDSUP+="%s=VALUES(%s),"%(field,field)
FIELDSTXT=FIELDSTXT.strip(",")+")"
FIELDSUP=FIELDSUP.strip(",")

DATETIME_FORMAT="%d/%m/%y %H:%M:%S"

"""
ETERNA COMPONENTS:
-1: for tidal potential in m**2/s**2.
0: for tidal gravity in nm/s**2.
1: for tidal tilt in mas, at azimuth STATAZIMUT.
2: for tidal vertical displacement in mm.
3: for tidal horizontal displacement in mm at azimuth 0 deg.
4: for tidal vertical strain in 10**-9 = nstr.
5: for tidal horizontal strain in 10**-9 = nstr, at azimuth 0 deg.
6: for tidal areal  strain in 10**-9 = nstr.
7: for tidal shear  strain in 10**-9 = nstr.
8: for tidal volume strain in 10**-9 = nstr.
9: for tidal horizontal displacement in mm at azimuth 90 deg.
"""

# NAME    :  g  tilt  vd vs hs0 hs90   areal shear volume
# IN FILE :  1  2     3  4  5   6      7     8     9
COMPONENTS=[ 0, 1,    2, 4, 5,  9]#,     6,    7,    8]
COMPONENTS_LONGTERM=[0]
COMPONENTS_DICT=dict(pot=[-1,"Tidal potential",r"m$^2$/s$^2$"],
                     grav=[0,"Tidal gravity",r"nm/s$^2$"],
                     tilt=[1,"Tidal tilt",r"mas"],
                     vd=[2,"Vertical displacement","mm"],
                     hd=[3,"Horizontal displacement","mm"],
                     vs=[4,"Vertical strain","nstr"],
                     hs=[5,"Horizontal strain","nstr"],
                     areal=[6,"Areal strain","nstr"],
                     shear=[7,"Shear","nstr"],
                     volume=[8,"Volume strain","nstr"],
                     ocean=[9,"Horizontal strain (Az = 90)","nstr"]
                 )

PHASES_DICT=dict(sd_fourier=[1,"Semidiurnal (Fourier)"],
                 dn_fourier=[2,"Diurnal (Fourier)"],
                 fn_fourier=[3,"Fornightly (Fourier)"],
                 mn_fourier=[4,"Monthly (Fourier)"],
                 sd=[5,"Semidiurnal"],
                 fn=[6,"Fornightly"],
                 mn=[7,"Monthly"])

# ######################################################################
# CORE ROUTINES
# ######################################################################
class dict2obj(object):
    def __init__(self,dic={}):self.__dict__.update(dic)
    def __add__(self,other):
        for attr in other.__dict__.keys():
            exec("self.%s=other.%s"%(attr,attr))
        return self

def saveObject(filename,obj):
    fo=open(filename,"w")
    for key in obj.__dict__.keys():
        fo.write("%s = '%s'\n"%(key,obj.__dict__[key]))
    fo.close()

def updateConf(filename,conf):
    d=dict()
    if os.path.lexists(filename):
        execfile(filename,{},d)
        for key in d.keys():
            if d[key]==-1 or d[key]=="":del d[key]
        conf.__dict__.update(d)
    else:print "Configuration file '%s' does not found."%filename

def loadConf(filename):
    """Load configuration file
    Parameters:
    ----------
    filename: string
       Filename with configuration values.
    Returns:
    -------
    conf: dictobj
       Object with attributes as variables in configuration file
    Examples:
    --------
    >> loadconf('input.conf')
    """
    d=dict()
    conf=dict2obj()
    if os.path.lexists(filename):
        execfile(filename,{},d)
        conf+=dict2obj(d)
    else:print "Configuration file '%s' does not found."%filename
    return conf

def fileBase(filename):
    dirs=filename.split("/")
    search=re.search("([^\/]+)\.[^\/]+",filename)
    basename=search.group(1)
    dirname="/".join(dirs[:-1])
    return dirname,basename

# ######################################################################
# CONFIGURATION
# ######################################################################
CONF=loadConf("configuration")
DIRNAME,BASENAME=fileBase(argv[0])
if DIRNAME=="":DIRNAME="."

# ######################################################################
# REGULAR ROUTINES
# ######################################################################
def connectDatabase(server='localhost',
                 user=CONF.DBUSER,
                 password=CONF.DBPASSWORD,
                 database=CONF.DBNAME):
    con=mdb.connect(server,user,password,database)
    return con

def loadDatabase(server='localhost',
                 user=CONF.DBUSER,
                 password=CONF.DBPASSWORD,
                 database=CONF.DBNAME):
    con=mdb.connect(server,user,password,database)
    with con:
        dbdict=dict()
        db=con.cursor()
        db.execute("show tables;")
        tables=db.fetchall()
        for table in tables:
            table=table[0]
            dbdict[table]=dict()
            
            db.execute("show columns from %s;"%table)
            fields=db.fetchall()
            dbdict[table]['fields']=[]
            for field in fields:
                fieldname=field[0]
                fieldtype=field[3]
                dbdict[table]['fields']+=[fieldname]
                if fieldtype=='PRI':
                    dbdict[table]['primary']=fieldname

            db.execute("select * from %s;"%table)
            rows=db.fetchall()

            dbdict[table]['rows']=dict()
            for row in rows:
                rowdict=dict()
                i=0
                for field in dbdict[table]['fields']:
                    rowdict[field]=row[i]
                    if field==dbdict[table]['primary']:
                        primary=row[i].strip()
                    i+=1
                dbdict[table]['rows'][primary]=rowdict

    return dbdict,con

def updateDatabase(dbdict,con):
    with con:
        db=con.cursor()
        for table in dbdict.keys():
            print "Actualizando tabla ",table
            for row in dbdict[table]['rows'].keys():
                sql="update %s set "%table;
                for field in dbdict[table]['fields']:
                    if field==dbdict[table]['primary']:
                        suffix="where %s='%s'"%(field,dbdict[table]['rows'][row][field])
                        continue
                    sql+="%s = '%s',"%(field,dbdict[table]['rows'][row][field])
                sql=sql.strip(",")+" %s;"%suffix
                db.execute(sql);
    con.commit()

def randomStr(N,numbers=True,letters=True):
    import string,random
    characters=""
    if numbers:characters+=string.digits
    if letters:characters+=string.ascii_uppercase
    string=''.join(random.SystemRandom().choice(characters) for _ in range(N))
    return string

def mysqlSimple(sql,db):
    db.execute(sql)
    result=db.fetchone()
    return result[0]

def mysqlArray(sql,db):
    db.execute(sql)
    result=db.fetchall()
    return result

def customdate2jd(mydate):
    """
    Calculate julian day at a given date in Greenwich
    
    Parameters:
    
      mydate: date of calculation (float)
      
         mydate format: MM/DD/CCYY HH:MM:SS.dcm [UTC-<D>]

    Returns:

      Julian day in Greenwich.
    """

    # SPLIT DATE STRING
    parts=mydate.split()

    # COMPONENTS OF DATE
    month,day,year=parts[0].split("/")
    hours,minutes,seconds=parts[1].split(":")
    try:utc,lag=parts[2].split("-")
    except:lag=0

    # GET CENTURY AND MJD
    century,mjd=gcal2jd(int(year),int(month),int(day))
    jd=century+mjd+(int(hours)+int(minutes)/60.+float(seconds)/3600.+float(lag))/24
    return jd

def date2jd(mydatetime):
    """
    Calculate julian day at a given date in Greenwich
    
    Parameters:
    
      mydatetime: date of calculation (datetime object)

    Returns:

      Julian day.
    """
    # GET CENTURY AND MJD
    century,mjd=gcal2jd(mydatetime.year,mydatetime.month,mydatetime.day)
    jd=century+mjd+(mydatetime.hour+mydatetime.minute/60.+\
                    (mydatetime.second+mydatetime.microsecond/1e6)/3600.)/24
    return jd

def d2s(d,fac=1):
    d*=fac
    hd=int(d)
    m=(d-hd)*60
    md=int(m)
    s=(m-md)*60
    sd=int(s)
    return hd,md,sd

def s2d(h,m,s,fac=1):
    d=numpy.sign(h)*(abs(h)+abs(m)/60.0+abs(s)/3600.0)
    return d

def jd2date(jd):
    d=jd2gcal(0,jd)
    h,m,s=d2s(d[3],fac=24)
    datetq=datetime.datetime.strptime("%02d/%02d/%s %02d:%02d:%02d"%(d[2],
                                                                     d[1],
                                                                     str(d[0])[2:],
                                                                     h,m,s),
                                      DATETIME_FORMAT)
    return datetq

def System(cmd,out=True):
    """
    Execute a command
    """
    if not out:
        system(cmd)
        output=""
    else:
        output=commands.getoutput(cmd)
    return output

def genEternaIni(basename,
                 qlat,qlon,qdepth,
                 year,month,day,
                 timespan,samplerate,
                 component):
    
    content="""# This file %s.INI status 2006.04.25 containing control parameters
# for programs DETIDE 3.30 and PREGRED 3.30

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# ! NOTE: The datalines have to start with their names.       !
# !       An additional comment may follow after the values,  !
# !       delimited by a whitespace                           !
# ! Values of 0 or less causes PREGRED to calculate the       !
# ! range(s) automatically resp. to use default values        !
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# a commentline starts with an '#', it may appear at any position
# in this file. Empty lines may appear too

# The next control parameters are used by DETIDE/DESPIKE/DECIMATE:

SENSORNAME=PREDICT         # earth tide sensor name
NUMRAWCHAN=      2         # number of recorded channels
NUMBCHANEL=      2         # number of channels after DETIDE
INPFILNAME=%s.dat    # DETIDE input data filename
#CALFILNAME=%s.cal    # calibration parameters
OUTFILNAME=%s.xxx    # DECIMATE output filename
SAMPLERATE=     %d         # sampling interval in seconds
DECIMATION=     12         # decimation factor for DECIMATE
#DECFILNAME=n60s5m02.nlf    # decimation filter 1 min to  5 min 
DECFILNAME=n14h5m01.nlf    # decimation filter 5 min to 1 h
STATLATITU=     %.3f    # stations latitude  in degree
STATLONITU=     %.3f       # stations longitude in degree
STATELEVAT=     %.3f       # stations elevation in meter
STATGRAVIT=      0.        # stations gravity in m/s**2
STATAZIMUT=      0.        # stations azimuth in degree from north
INITIALEPO= %d  %d   %d    # initial epoch in year,month,day
PREDICSPAN=     %d         # prediction time span in hours for PREDICT
TIDALCOMPO=     %d         # tidal component, see manual
TIDALPOTEN=      7         # tidal potential development
AMTRUNCATE=  1.D-6         # amplitude threshold    
POLTIDECOR=   0.00         # pole tide amplitude factor
LODTIDECOR=   0.00         # LOD  tide amplitude factor
STEPDETLIM=      5.        # DESPIKE limit for step detection  (nm/s**2) 
SPIKDETLIM=      2.        # DESPIKE limit for spike detection (nm/s**2)

#TIDALPARAM=  0.000000  0.600000   1.15000    0.0000 long   #tidal param. 
#TIDALPARAM=  0.600001  0.910000   1.14673   -0.2474 Q1     #tidal param.
#TIDALPARAM=  0.910001  0.949000   1.14882    0.0804 O1     #tidal param.
#TIDALPARAM=  0.949001  0.980000   1.13070    0.2132 M1     #tidal param.
#TIDALPARAM=  0.980001  1.012000   1.13599    0.2062 K1     #tidal param.
#TIDALPARAM=  1.012001  1.050000   1.15354    0.0801 J1     #tidal param.
#TIDALPARAM=  1.050001  1.500000   1.14851   -0.0251 OO1    #tidal param.
#TIDALPARAM=  1.500001  1.875000   1.15205    2.4463 2N2    #tidal param.
#TIDALPARAM=  1.875001  1.910000   1.17054    2.5425 N2     #tidal param.
#TIDALPARAM=  1.910001  1.950000   1.18705    2.0327 M2     #tidal param.
#TIDALPARAM=  1.950001  1.985000   1.22450    4.1630 L2     #tidal param.
#TIDALPARAM=  1.985001  2.500000   1.18963    0.6271 S2     #tidal param.
#TIDALPARAM=  2.500001  3.500000   1.06234    0.3783 M3     #tidal param.
#TIDALPARAM=  3.500001  7.000000   1.02000    0.0000 M4M6   #tidal param.

                                                                             
TIDALPARAM=  0.000000  0.501369   1.16000    0.0000 long   #tidal param. 
TIDALPARAM=  0.501370  0.842147   1.16000    0.0000 SGQ1   #tidal param.                                
TIDALPARAM=  0.842148  0.860293   1.16000    0.0000 2Q1    #tidal param.  
TIDALPARAM=  0.860294  0.878675   1.16000    0.0000 SGM1   #tidal param.  
TIDALPARAM=  0.878676  0.896968   1.16000    0.0000 Q1     #tidal param.  
TIDALPARAM=  0.896969  0.911390   1.16000    0.0000 RO1    #tidal param.  
TIDALPARAM=  0.911391  0.931206   1.16000    0.0000 O1     #tidal param.  
TIDALPARAM=  0.931207  0.947991   1.16000    0.0000 TAU1   #tidal param.  
TIDALPARAM=  0.947992  0.967660   1.16000    0.0000 NO1    #tidal param.  
TIDALPARAM=  0.967661  0.981854   1.16000    0.0000 CHI1   #tidal param.  
TIDALPARAM=  0.981855  0.996055   1.16000    0.0000 PI1    #tidal param.  
TIDALPARAM=  0.996056  0.998631   1.16000    0.0000 P1     #tidal param.  
TIDALPARAM=  0.998632  1.001369   1.16000    0.0000 S1     #tidal param.  
TIDALPARAM=  1.001370  1.004107   1.16000    0.0000 K1     #tidal param.  
TIDALPARAM=  1.004108  1.006845   1.16000    0.0000 PSI1   #tidal param.  
TIDALPARAM=  1.006846  1.023622   1.16000    0.0000 PHI1   #tidal param.  
TIDALPARAM=  1.023623  1.035379   1.16000    0.0000 TET1   #tidal param.  
TIDALPARAM=  1.035380  1.057485   1.16000    0.0000 J1     #tidal param.  
TIDALPARAM=  1.057486  1.071833   1.16000    0.0000 SO1    #tidal param.  
TIDALPARAM=  1.071834  1.090052   1.16000    0.0000 OO1    #tidal param.  
TIDALPARAM=  1.090053  1.470243   1.16000    0.0000 NU1    #tidal param.  
TIDALPARAM=  1.470244  1.845944   1.16000    0.0000 EPS2   #tidal param.  
TIDALPARAM=  1.845945  1.863026   1.16000    0.0000 2N2    #tidal param.  
TIDALPARAM=  1.863027  1.880264   1.16000    0.0000 MU2    #tidal param.    
TIDALPARAM=  1.880265  1.897351   1.16000    0.0000 N2     #tidal param.    
TIDALPARAM=  1.897352  1.914128   1.16000    0.0000 NU2    #tidal param.  
TIDALPARAM=  1.914129  1.950419   1.16000    0.0000 M2     #tidal param.  
TIDALPARAM=  1.950420  1.964767   1.16000    0.0000 LAM2   #tidal param.  
TIDALPARAM=  1.964768  1.984282   1.16000    0.0000 L2     #tidal param.  
TIDALPARAM=  1.984283  1.998996   1.16000    0.0000 T2     #tidal param.  
TIDALPARAM=  1.998997  2.002736   1.16000    0.0000 S2     #tidal param.  
TIDALPARAM=  2.002737  2.022488   1.16000    0.0000 K2     #tidal param.  
TIDALPARAM=  2.022489  2.057484   1.16000    0.0000 ETA2   #tidal param.  
TIDALPARAM=  2.057485  2.451943   1.16000    0.0000 2K2    #tidal param.  
TIDALPARAM=  2.451944  2.881176   1.16000    0.0000 MN3    #tidal param.  
TIDALPARAM=  2.881177  3.381378   1.16000    0.0000 M3     #tidal param.  
TIDALPARAM=  3.381379  4.347615   1.16000    0.0000 M4     #tidal param. 
                                           
                                                                     
# End of file %s.INI                                          
                                          
                                    
"""%(basename,basename,basename,basename,
     samplerate,
     qlat,qlon,qdepth,
     year,month,day,
     timespan,component,
     basename)
    
    content=content.replace("\n","\r\n")
    return content

# ######################################################################
# FOURIER ANALYSIS
# ######################################################################
def signal_teo(t,ft,T,N,k):
    w=2*PI*k/T
    serie=ft[0]+2*ft[k]*cmath.exp(1j*w*t)
    serie=serie/N
    return numpy.real(serie)

def all_signal_teo(t,ft,T,N,ko,dk):
    serie=ft[0]
    for k in xrange(ko,ko+dk):
        w=2*PI*k/T
        serie+=2*ft[k]*cmath.exp(1j*w*t)
    serie=serie/N
    return numpy.real(serie)

def omega2k(wo,T,N):
    w1=2*PI/T
    k=round((wo-w1)*N*T/(2*PI*(N-2))+1)
    return int(k)

def phaseFourier(ft,to,T,N,periodo):
    wo=2*PI/periodo
    k=omega2k(wo,T,N)
    x=numpy.real(ft[k])
    y=numpy.imag(ft[k])
    phase=(numpy.arctan2(y,x)*180/PI)
    phase=numpy.mod(phase,360.0)
    wk=2*PI*k/T
    wkt=(wk*to)*180/PI
    phasek=wkt+phase
    phasek=numpy.mod(phasek,360.0)
    return phasek

def quakeProperties(quakeid,db):
    quake=dict2obj(dict())
    keys=mysqlArray("describe Quakes;",db)
    props=mysqlArray("select * from Quakes where quakeid='%s';"%quakeid,db)
    for i in xrange(len(keys)):
        key=keys[i][0]
        value=props[0][i]
        if value is not None:
            value=value.replace("\n","")
        exec("quake.%s='%s'"%(key,value))
    return quake

def loadComplextxt(filename):
    f=open(filename,"r")
    ts=[]
    zs=[]
    for line in f:
        t,z=line.strip().split()
        exec("ts+=[numpy.real(%s)]"%t)
        exec("zs+=[%s]"%z)
    return numpy.array(ts),numpy.array(zs)

def signalBoundary(t,s):
    ds=numpy.sign((s[1:]-s[:-1]))
    n=len(ds)
    
    tM=[];sM=[]
    tm=[];sm=[]
    for i in xrange(1,n):
        if ds[i]<ds[i-1]:
            tM+=[t[i]]
            sM+=[s[i]]
        if ds[i]>ds[i-1]:
            tm+=[t[i]]
            sm+=[s[i]]

    tM=numpy.array(tM);sM=numpy.array(sM)
    tm=numpy.array(tm);sm=numpy.array(sm)
    return tm,sm,tM,sM

def numComponent(namecomponent):
    """
    Determine position in signal, phases and datafile of <component>
    """
    # GET INDEX OF COMPONENT
    component=COMPONENTS_DICT[namecomponent][0]

    # COLUMN IN DATAFILE AND QSIGNAL
    numcol=COMPONENTS.index(component)+1

    # PHASES IN QPHASES
    numphases=7*(numcol-1)
    
    return numcol,numphases

def lat2str(lat):
    return "%g"%lat

def lon2str(lon):
    if lon>270:lon-=360
    return "%g"%lon

def scatterMap(ax,qlat,qlon,
               m=None,
               resolution='c',
               limits=None,
               pardict=dict(),
               merdict=dict(),
               zoom=1,
               **formats):
    """
    Create a scatter 
    """
    from mpl_toolkits.basemap import Basemap as map

    if m is None:
        if limits is None:
            qlatmin=min(qlat)
            qlatmax=max(qlat)
            qlonmin=min(qlon)
            qlonmax=max(qlon)
            qlonmean=(qlonmax+qlonmin)/2
            qlatmean=(qlatmax+qlatmin)/2
            dlat=zoom*abs(qlatmax-qlatmin)*PI/180*6371.0e3
            dlon=zoom*abs(qlonmax-qlonmin)*PI/180*6371.0e3
            if dlat==0:dlat=1E5
            if dlon==0:dlon=1E5
        else:
            qlatmean=limits[0]
            qlonmean=limits[1]
            dlat=limits[2]*PI/180*6371.0e3
            dlon=limits[3]*PI/180*6371.0e3

        # ############################################################
        # MAP OPTIONS
        # ############################################################
        fpardict=dict(labels=[True,True,False,False],
                      fontsize=10,zorder=10,linewidth=0.5,fmt=lat2str)
        fmerdict=dict(labels=[False,False,True,True],
                      fontsize=10,zorder=10,linewidth=0.5,fmt=lon2str)

        fpardict.update(pardict)
        fmerdict.update(merdict)

        # ############################################################
        # PREPARE FIGURE
        # ############################################################
        m=map(projection="aea",resolution=resolution,width=dlon,height=dlat,
              lat_0=qlatmean,lon_0=qlonmean,ax=ax)

        m.drawlsmask(alpha=0.5)
        m.etopo(zorder=-10)
        m.drawparallels(numpy.arange(-45,45,1),**fpardict)
        m.drawmeridians(numpy.arange(-90,90,1),**fmerdict)

    # ############################################################
    # PLOT
    # ############################################################
    x,y=m(qlon,qlat)
    ax.plot(x,y,**formats)

    return m

QJD=0
QLAT=1
QLON=2
QDEP=3
ML=4
def getQuakes(search,db,vvv=True):
    # ############################################################
    # GET BASIC INFO EARTHQUAKES
    # ############################################################
    i=0
    sql="select quakeid,qjd,qlat,qlon,qdepth,Ml from Quakes %s"%(search)
    if vvv:print "Searching quakes with the criterium:\n\t%s"%sql
    results=mysqlArray(sql,db)
    nquakes=len(results)
    table=numpy.zeros((nquakes,5))
    qids=[]
    for i in xrange(nquakes):
        qids+=[results[i][0]]
        for j in xrange(5):
            table[i,j]=float(results[i][j+1])
    if vvv:print "%s quakes found."%len(qids)
    return qids,table

SDF=5
DNF=6
FNF=7
MNF=8
SD=9
FN=10
MN=11
PERIODS=[0]*5+[0.5,1.0,14.8,29.6,0.5,14.8,29.6]
PHASES=[0]*5+["Semidiurnal Fourier","Diurnal Fourier",
              "Fornightly Fourier","Monthly Fourier",
              "Semidiurnal","Fornightly","Monthly"]

def getPhases(search,component,db,vvv=True):
    # COLUMNS: 
    """
    0:qjd,1:qlat,2:qlon,3:qdepth,4:Mlq
    Fourier: 5:sd, 6:dn, 7:fn, 8:mn
    Boundaries: 9:sd, 10:fn, 11:mn
    """
    # ############################################################
    # COMPONENT INFORMATION
    # ############################################################
    info=COMPONENTS_DICT[component]
    compnum=info[0]
    name=info[1]
    nc,np=numComponent(component)

    # ############################################################
    # GET BASIC INFO EARTHQUAKES
    # ############################################################
    i=0
    sql="select quakeid,qjd,qlat,qlon,qdepth,Ml from Quakes %s"%(search)
    if vvv:print "Searching quakes' phases with the criterium:\n\t%s"%sql
    results=mysqlArray(sql,db)
    nquakes=len(results)
    table=numpy.zeros((nquakes,5))
    qids=[]
    for i in xrange(nquakes):
        qids+=[results[i][0]]
        for j in xrange(5):
            table[i,j]=float(results[i][j+1])

    for ip in xrange(1,7+1):
        sql="select SUBSTRING_INDEX(SUBSTRING_INDEX(qphases,';',%d),';',-1) from Quakes %s"%(np+ip,search)
        results=mysqlArray(sql,db)
        phases=[]
        for ph in results:
            try:
                phtime=ph[0].split(":")
                phases+=[float(phtime[1])]
            except:
                phases+=[float(phtime[0])]
        phases=numpy.array(phases)
        table=numpy.column_stack((table,phases))
        
    if vvv:print "%s quakes found."%len(qids)
    return qids,table

def schusterValue(phases,qbootstrap=False,
                  facbootstrap=0.5,bootcycles=50,
                  qsteps=0):
    if len(phases)<int(1/facbootstrap):return 0,0
    if qbootstrap:
        nbootstrap=facbootstrap*len(phases)
        logps=[]
        i=0
        while i<bootcycles:
            bphases=numpy.random.choice(phases,nbootstrap)
            N=len(bphases)
            D2=numpy.cos(bphases).sum()**2+numpy.sin(bphases).sum()**2
            ilogp=-D2/N
            logps+=[ilogp]
            i+=1
        logp=numpy.mean(logps)
        dlogp=numpy.std(logps)
    else:
        N=len(phases)
        D2=numpy.cos(phases).sum()**2+numpy.sin(phases).sum()**2
        logp=-D2/N
        dlogp=1E-17
    return logp,dlogp

def schusterSteps(phases,
                  qbootstrap=0,
                  facbootstrap=1):

    if qbootstrap:
        nbootstrap=facbootstrap*len(phases)
        phases=numpy.random.choice(phases,nbootstrap)

    xstep=[0.0];ystep=[0.0]
    x=0;y=0
    for phase in phases:
        x=x+numpy.cos(phase)
        y=y+numpy.sin(phase)
        xstep+=[x]
        ystep+=[y]
    return xstep,ystep

def tdWindow(M,fit="GK74"):
    """
    See: http://www.corssa.org/articles/themev/van_stiphout_et_al

    Test:
    # fit="U86"
    # fit="G12"
    fit="GK74"
    for M in numpy.arange(2.5,8.5,0.5):
        t,d=tdWindow(M,fit=fit)
        print "M = %.2f, dt = %.2f days, d = %.2f km"%(M,t,d)
    exit(0)
    """
    if fit=="GK74":
        """Eq1"""
        d=10**(0.1238*M+0.983)
        if M<6.5:t=10**(0.5409*M-0.5407)
        else:t=10**(0.032*M+2.7389)
    elif fit=="G12":
        """Eq2"""
        d=numpy.exp(1.77+(0.037+1.02*M)**2)
        if M<6.5:t=10**(2.8+0.024*M)
        else:t=numpy.exp(-3.95+(0.62+17.32*M)**2)
    elif fit=="U86":
        """Eq3"""
        d=numpy.exp(-1.024+0.804*M)
        t=numpy.exp(-2.87+1.235*M)
    
    return t,d

def distancePoints(latOrigin,lonOrigin,latDestination,lonDestination):
    """
    Adapted from:
    http://www.corssa.org/articles/themev/van_stiphout_et_al
    """
    
    a = 6378.137;
    b = 6356.7523142;
    f = (a - b) / a;
    
    latOrigin *= DEG
    lonOrigin *= DEG
    latDestination *= DEG
    lonDestination *= DEG

    L = lonOrigin - lonDestination;
    U_1 = numpy.arctan((1 - f) * numpy.tan(latOrigin));
    U_2 = numpy.arctan((1 - f) * numpy.tan(latDestination));

    lamb = L;
    lambPrime = 2 * PI;
    cosSquaredAlpha = 0;
    sinSigma = 0;
    cosSigma = 0;
    cos2Sigma_m = 0;
    sigma = 0;
    epsilon = 1e-7;

    while (numpy.abs(lamb - lambPrime) > epsilon):
        temp1 = numpy.cos(U_2) * numpy.sin(lamb);
        temp2 = numpy.cos(U_1) * numpy.sin(U_2) - numpy.sin(U_1) * numpy.cos(U_2) * numpy.cos(lamb);
        sinSigma = numpy.sqrt(temp1 * temp1 + temp2 * temp2);
        cosSigma = numpy.sin(U_1) * numpy.sin(U_2) + numpy.cos(U_1) * numpy.cos(U_2) * numpy.cos(lamb);
        sigma = numpy.arctan2(sinSigma, cosSigma);
        sinAlpha = numpy.cos(U_1) * numpy.cos(U_2) * numpy.sin(lamb) / (sinSigma + 1e-16);
        cosSquaredAlpha = 1 - sinAlpha * sinAlpha;
        cos2Sigma_m = numpy.cos(sigma) - 2 * numpy.sin(U_1) * numpy.sin(U_2) / (cosSquaredAlpha + 1e-16);
        C = f / 16 * cosSquaredAlpha * (4 + f * (4 - 3 * cosSquaredAlpha));
        lambPrime = lamb;
        lamb = L + (1 - C) * f * sinAlpha * (sigma + C * sinSigma * \
                    (cos2Sigma_m + C * cosSigma * (-1 + 2 * cos2Sigma_m * \
                                                   cos2Sigma_m)));

    uSquared = cosSquaredAlpha * (a * a - b * b) / (b * b);
    A = 1 + uSquared / 16384 * (4096 + uSquared * (-768 + uSquared * \
                                                   (320 - 175 * uSquared)));
    B = uSquared / 1024 * (256 + uSquared * (74 - 47 * uSquared));
    deltaSigma = B * sinSigma * (cos2Sigma_m + B / 4 * (cosSigma * \
                                                    (-1 + 2 * cos2Sigma_m * cos2Sigma_m - B / 6 * cos2Sigma_m * \
                                                     (-3 + 4 * sinSigma * sinSigma * (-3 + 4 * cos2Sigma_m * \
                                                                                      cos2Sigma_m)))));
    
    distance = (b * A * (sigma - deltaSigma));
    return distance;

if __name__=="__main__":
    if len(argv)>1:
        if argv[1]=="date2jd":
            helptxt="""
            Options: yyyy mm dd hh mm ss
            Return: Julian date
            """
            args=tuple([int(d) for d in argv[2:]])
            if len(args)==0:
                print helptxt
                exit(1)
            try:
                jd=date2jd(datetime.datetime(*args))
            except:
                print helptxt
                exit(1)
            print jd
        elif argv[1]=="tdWindow":
            helptxt="""
            Options: M <method>
            Where: <method>: GK72, GK74
            Return: Time and Space Window (days, km)
            """
            try:
                M=float(argv[2])
                fit=argv[3]
                t,d=tdWindow(M,fit=fit)
            except:
                print helptxt
                exit(1)
            print "M = %.2f, dt = %.2f days, d = %.2f km"%(M,t,d)
        else:
            print "This is tQuakes!"

def subPlots(plt,panels,l=0.1,b=0.1,w=0.8,dh=None):
    """
    Subplots
    """
    npanels=len(panels)
    spanels=sum(panels)

    # GET SIZE OF PANELS
    b=b/npanels
    if dh is None:dh=[b/2]*npanels
    elif type(dh) is not list:dh=[dh]*npanels
    else:
        dh+=[0]

    # EFFECTIVE PLOTTING REGION
    hall=(1-2*b-sum(dh))
    hs=(hall*numpy.array(panels))/spanels
    fach=(1.0*max(panels))/spanels

    # CREATE AXES
    fig=plt.figure(figsize=(8,6/fach))
    axs=[]
    for i in xrange(npanels):
        axs+=[fig.add_axes([l,b,w,hs[i]])]
        b+=hs[i]+dh[i]
    return fig,axs

def md5sumFile(myfile):
    md5sum=System("md5sum %s |cut -f 1 -d ' '"%myfile)
    return md5sum

def pOsc(phase,params):
    P=params[0]+params[1]*numpy.cos(phase-params[2])
    return P

def chisq(params,function,xdata,ydata,dydata):
    dymean=dydata.mean()
    dydata[dydata==0]=dymean
    return (ydata-function(xdata,params))/dydata

def prepareScript():
    # CONFIGURATION FILE
    if len(argv)>1 and os.path.lexists(argv[1]):confile=argv[1]
    else:confile="%s.conf"%BASENAME
    # HISTORY DIR
    dirname="%s.history"%BASENAME
    if not os.path.lexists(dirname):
        System("mkdir %s"%dirname)
    # MOVE PREVIOUS COMPUTED FIGURES
    System("mv %s__*.png %s.history/"%(BASENAME,BASENAME))
    # SIGNATURE
    md5sum=md5sumFile(confile)
    # COPY CONFIGURATION FILE
    System("cp %s %s/%s__%s.conf"%(confile,dirname,BASENAME,md5sum))
    return confile

def saveFigure(confile,fig):
    # MD5SUM FOR THIS REALIZATION
    md5sum=md5sumFile(confile)
    # SAVE FIGURE
    figname="%s/%s__%s.png"%(DIRNAME,BASENAME,md5sum)
    print "Saving figure ",figname
    fig.savefig(figname)
