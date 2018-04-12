try:
    import MySQLdb as mdb
except:
    import pymysql
    pymysql.install_as_MySQLdb()
    import MySQLdb as mdb
import csv,datetime,commands,re,os,numpy,cmath,time as timing
from scipy import signal
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
norm=numpy.linalg.norm

# MOON ANGULAR RATE
MOONRATE=(360.0-360.0/27.32166) # Degrees per day

ONE=1.0
MIN=60.0
HOUR=60*MIN
DAY=24*HOUR # seconds
YEAR=365.25*DAY # seconds

SIDFAC=1.002737909

# EARTH'S EQUATORIAL RADIUS
REARTH=6378.1366 #km

# EARTH'S FLATTENING
FEARTH=0.00335281310846

# MOON ANGULAR RATE
MOONRATE=(360.0-360.0/27.32166) # Degrees per day

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
            "qdatetime","qjd","qet","hmoon","hsun",
            "astatus","adatetime","stationid","country"]

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
9: for tidal horizontal strain at azimuth 90 deg.
"""

# NAME    :  g  tilt  vd vs hs0 hs90   areal shear volume
# IN FILE :  1  2     3  4  5   6      7     8     9
COMPONENTS=[ 0, 1,    2, 4, 5,  9]#,     6,    7,    8]
PHASESGN=  [-1,+1,   +1,-1,+1, +1]   
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
                     hst=[9,"Horizontal strain (Az = 90)","nstr"]
                 )

PHASES_DICT=dict(sd_fourier=[1,"Semidiurnal (Fourier)"],
                 dn_fourier=[2,"Diurnal (Fourier)"],
                 fn_fourier=[3,"Fornightly (Fourier)"],
                 mn_fourier=[4,"Monthly (Fourier)"],
                 sd=[5,"Semidiurnal"],
                 dn=[6,"Diurnal"],
                 fn=[7,"Fornightly"],
                 mn=[8,"Monthly"])
NUM_PHASES=len(PHASES_DICT)

"""
Components are: 
   1 - Apogea, 2 - Perigea
   3 - Max.Apogee, 4 - Min.Perigee
   5 - Aphelia, 6 - Perihelia
"""
EXTREMES=[[1,"Apogea"],
          [2,"Perigea"],
          [3,"Max.Apogee"],
          [4,"Min.Perigee"],
          [5,"Aphelia"],
          [6,"Perihelia"]]

# ASTRONOMY PHASES

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
    else:print("Configuration file '%s' does not found."%filename)

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
    else:print("Configuration file '%s' does not found."%filename)
    return conf

def fileBase(filename):
    dirs=filename.split("/")
    search=re.search("([^\/]+)\.[^\/]+$",filename)
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
            print("Actualizando tabla ",table)
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
    jd=century+mjd+(int(hours)+int(minutes)/60.+float(seconds)/3600.+float(lag))/24.
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
                 component,azimut):
    
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
STATAZIMUT=     %.3f       # stations azimuth in degree from north
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
     qlat,qlon,qdepth,azimut,
     year,month,day,
     timespan,component,
     basename)
    
    content=content.replace("\n","\r\n")
    return content

def loadExtremesTable(extremes,table):
    """
    extremes is an array of the form:

    [[1,"Component1"],
     [2,"Component2"],
     ...
    ]
    """
    n=table.shape[0]
    data=dict()
    for i in xrange(n):
        if i==0:continue
        line=table[i]
        if line[1]>1E8:
            ncomp=int(line[0])
            name=extremes[ncomp-1][1]
            data[name]=numpy.array([0,0])
            continue
        data[name]=numpy.vstack((data[name],line))
    return data

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
    imax=100
    for i in xrange(1,n):
        #if i<imax:print i,t[i],s[i],ds[i],ds[i-1]
        if ds[i]<ds[i-1]:
            tM+=[t[i]]
            sM+=[s[i]]
            #if i<imax:print "Maximum:",t[i],s[i]
        if ds[i]>ds[i-1]:
            tm+=[t[i]]
            sm+=[s[i]]
            #if i<imax:print "Minimum:",t[i],s[i]

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
    numphases=NUM_PHASES*(numcol-1)
    
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
               topography=False,
               lsmask=False,
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

        if lsmask:m.drawlsmask(alpha=0.5)
        if topography:m.etopo(zorder=-10)
        m.drawcoastlines(linewidth=1.25)
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
QET=5
def getQuakes(search,db,vvv=True):
    # ############################################################
    # GET BASIC INFO EARTHQUAKES
    # ############################################################
    i=0
    sql="select quakeid,qjd,qlat,qlon,qdepth,Ml from Quakes %s"%(search)
    if vvv:print("Searching quakes with the criterium:\n\t%s"%sql)
    results=mysqlArray(sql,db)
    nquakes=len(results)
    table=numpy.zeros((nquakes,5))
    qids=[]
    for i in xrange(nquakes):
        qids+=[results[i][0]]
        for j in xrange(5):
            table[i,j]=float(results[i][j+1])
    if vvv:print("%s quakes found."%len(qids))
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

def getPhases(search,component,db,dbtable="Quakes",vvv=True):
    # COLUMNS: 
    """
    0:qjd,1:qlat,2:qlon,3:qdepth,4:Mlq
    Fourier: 5:sd, 6:dn, 7:fn, 8:mn
    Boundaries: 9:sd, 10:dn, 11:fn, 12:mn
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
    sql="select quakeid,qjd,qlat,qlon,qdepth,Ml from %s %s"%(dbtable,search)
    if vvv:print("Searching quakes' phases with the criterium:\n\t%s"%sql)
    results=mysqlArray(sql,db)
    nquakes=len(results)
    table=numpy.zeros((nquakes,5))
    qids=[]
    for i in xrange(nquakes):
        qids+=[results[i][0]]
        for j in xrange(5):
            table[i,j]=float(results[i][j+1])

    for ip in xrange(1,NUM_PHASES+1):
        sql="select SUBSTRING_INDEX(SUBSTRING_INDEX(qphases,';',%d),';',-1) from %s %s"%(np+ip,dbtable,search)
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
        
    if vvv:print("%s quakes found."%len(qids))
    return qids,table

def schusterValue(phases,qbootstrap=False,
                  facbootstrap=0.5,bootcycles=50,
                  qsteps=0):

    if len(phases)<int(1/facbootstrap):return 0,0

    if qbootstrap:
        nbootstrap=int(facbootstrap*len(phases))
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
        nbootstrap=int(facbootstrap*len(phases))
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
                print(helptxt)
                exit(1)
            try:
                jd=date2jd(datetime.datetime(*args))
            except:
                print(helptxt)
                exit(1)
            print(jd)
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
                print(helptxt)
                exit(1)
            print("M = %.2f, dt = %.2f days, d = %.2f km"%(M,t,d))
        else:
            print("This is tQuakes!")

def subPlots(plt,panels,l=0.1,b=0.1,w=0.8,dh=None,
             fac=2.0,fach=False):
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
    hall=(1-fac*b-sum(dh))
    hs=(hall*numpy.array(panels))/spanels
    if not fach:
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
    System("cp %s %s/%s__%s.conf"%(confile,dirname,BASENAME,md5sum[0:5]))
    return confile

def saveFigure(confile,fig,qwater=True):
    # MD5SUM FOR THIS REALIZATION
    md5sum=md5sumFile(confile)
    # SAVE FIGURE
    figname="%s/%s__%s.png"%(DIRNAME,BASENAME,md5sum[0:5])
    print("Saving figure ",figname)

    # WATER MARK
    if qwater:
        ax=fig.gca()
        ax.text(1.01,1.0,"tQuakes",
                horizontalalignment='left',verticalalignment='top',
                rotation=-90,fontsize=10,color='b',alpha=0.3,
                transform=ax.transAxes,zorder=1000)

    fig.savefig(figname)

def plotSignal(quakeid,component,plt):
    # ############################################################
    # COMPONENT
    # ############################################################
    info=COMPONENTS_DICT[component]
    compnum=info[0]
    name=info[1]
    units=info[2]
    nc,np=numComponent(component)
    
    # ############################################################
    # QUAKE PROPERTIES
    # ############################################################
    quake=loadConf(DIRNAME+"/quake.conf")
    quakestr="QUAKE-lat_%+.2f-lon_%+.2f-dep_%+.2f-JD_%.5f"%\
        (float(quake.qlat),
         float(quake.qlon),
         float(quake.qdepth),
         float(quake.qjd))

    # ############################################################
    # PREPARE FIGURE
    # ############################################################
    fig=plt.figure()
    ax=plt.gca()

    # ############################################################
    # CREATE FIGURE
    # ############################################################
    qsignal=quake.qsignal.split(";")
    value=float(qsignal[nc-1])

    signal=numpy.loadtxt(DIRNAME+"/%s.data"%quakeid)
    t=signal[:,0]-float(quake.qjd)
    s=signal[:,nc]
    smin=s.min();smax=s.max()
    
    ax.plot(t,s)
    ax.plot([0],[value],marker='o',color='r',markersize=10,markeredgecolor="None")
    ax.axvline(0,color='r')

    # ############################################################
    # DECORATION
    # ############################################################
    ax.set_xlim((-CONF.TIMEWIDTH,+CONF.TIMEWIDTH))
    ax.set_ylim((smin,smax+(smax-smin)/2))

    ax.set_title(r"%s for quake %s"%(name,quakeid))
    ax.set_xlabel(r"Days to/since earthquake")
    ax.set_ylabel(r"%s (%s)"%(name,units))

    # ############################################################
    # INSET PANEL
    # ############################################################
    axi=fig.add_axes([0.172,0.65,0.68,0.22])
    axi.plot(t,s)
    axi.plot([0],[value],marker='o',color='r',markersize=10,markeredgecolor="None")
    axi.axvline(0,color='r')
    axi.set_xlim((-10,10))
    axi.text(0.1,0.93,r"%s = %.1f %s"%(component.upper(),value,units),transform=ax.transAxes,fontsize=8)
    axi.set_yticklabels([])

    # ############################################################
    # SAVE FIGURE
    # ############################################################
    ax.text(1.02,0.5,quakestr,
            horizontalalignment='center',verticalalignment='center',
            rotation=90,fontsize=10,color='k',alpha=0.2,
            transform=ax.transAxes)

    figname="%s/%s.png"%(DIRNAME,BASENAME)
    print("Saving figure ",figname)
    fig.savefig(figname)
    return fig

def quake2str(qlat,qlon,qdepth,qjd):
    quakestr="QUAKE-lat_%+08.4f-lon_%+09.4f-dep_%+010.4f-JD_%.5f"%\
        (float(qlat),
         float(qlon),
         float(qdepth),
         float(qjd))
    return quakestr

def plotBoundaries(quakeid,component,plt):
    # ############################################################
    # COMPONENT
    # ############################################################
    info=COMPONENTS_DICT[component]
    compnum=info[0]
    name=info[1]
    units=info[2]
    nc,np=numComponent(component)

    # ############################################################
    # QUAKE PROPERTIES
    # ############################################################
    quake=loadConf(DIRNAME+"/quake.conf")
    quakestr="QUAKE-lat_%+.2f-lon_%+.2f-dep_%+.2f-JD_%.5f"%\
        (float(quake.qlat),
         float(quake.qlon),
         float(quake.qdepth),
         float(quake.qjd))
    quakestr=quake2str(quake.qlat,quake.qlon,quake.qdepth,quake.qjd)

    # ############################################################
    # PREPARE FIGURE
    # ############################################################
    fig=plt.figure()
    ax=plt.gca()

    # ############################################################
    # CREATE FIGURE
    # ############################################################
    # GET SIGNAL VALUE
    qsignal=quake.qsignal.split(";")
    value=float(qsignal[nc-1])

    # GET PHASES
    qphases=quake.qphases.split(";")

    phtime=qphases[np+3+1].split(":")
    
    phase_sd=float(phtime[1])
    phtime=qphases[np+3+2].split(":")
    phase_dn=float(phtime[1])
    phtime=qphases[np+3+3].split(":")
    phase_fn=float(phtime[1])
    phtime=qphases[np+3+4].split(":")
    phase_mn=float(phtime[1])

    # READ SIGNAL
    sign=numpy.loadtxt(DIRNAME+"/%s.data"%quakeid)
    t=sign[:,0]-float(quake.qjd)
    s=sign[:,nc]
    smin=s.min();smax=s.max()

    # ==============================
    # FIND MAXIMA AND MINIMA
    # ==============================
    # SEMIDIURNAL LEVEL PEAKS
    tmb,smb,tMb,sMb=signalBoundary(t,s)

    # SMOOTH MAXIMA & MINIMA
    b,a=signal.butter(8,0.125)
    sMs=signal.filtfilt(b,a,sMb,padlen=100)
    tMs=tMb
    b,a=signal.butter(8,0.125)
    sms=signal.filtfilt(b,a,smb,padlen=100)
    tms=tmb

    # FORTNIGHTLY LEVEL PEAKS (MAXIMA)
    tmF,smF,tMF,sMF=signalBoundary(tMs,sMs)
    # FORTNIGHTLY LEVEL PEAKS (MINIMA)
    tmf,smf,tMf,sMf=signalBoundary(tms,sms)

    # PEAKS SEMIDIURNAL
    npeaks=len(tMb)
    ipeaks=numpy.arange(npeaks)
    ipeak=ipeaks[tMb<0][-1]
    tminb=tMb[ipeak];tmaxb=tMb[ipeak+1]

    # PEAKS DIURNAL
    dpeak1=sMb[ipeak]-smb[ipeak]
    dpeak2=sMb[ipeak+1]-smb[ipeak+1]
    if dpeak1<dpeak2:ipeak=ipeak-1
    tmind=tMb[ipeak];tmaxd=tMb[ipeak+2]

    tMd=numpy.concatenate((tMb[ipeak::-2],tMb[ipeak::+2]))
    sMd=numpy.concatenate((sMb[ipeak::-2],sMb[ipeak::+2]))

    tmd=numpy.concatenate((tmb[ipeak::-2],tmb[ipeak::+2]))
    smd=numpy.concatenate((smb[ipeak::-2],smb[ipeak::+2]))

    # PEAKS FORTNIGHTLY
    npeaks=len(tMF)
    ipeaks=numpy.arange(npeaks)
    ipeak=ipeaks[tMF<0][-1]
    tminf=tMF[ipeak];tmaxf=tMF[ipeak+1]

    # PEAKS MONTHLY
    npeaks=len(tMF)
    ipeaks=numpy.arange(npeaks)
    ipeak=ipeaks[tMF<0][-1]
    dpeak1=sMF[ipeak]-smf[ipeak]
    dpeak2=sMF[ipeak+1]-smf[ipeak+1]
    if dpeak1<dpeak2:ipeak=ipeak-1
    tminm=tMF[ipeak];tmaxm=tMF[ipeak+2]

    # ############################################################
    # DECORATION
    # ############################################################
    ax.set_xlim((-CONF.TIMEWIDTH,+CONF.TIMEWIDTH))
    ax.set_ylim((smin,smax+(smax-smin)/2))

    ax.set_title(r"%s for quake %s"%(name,quakeid))
    ax.set_xlabel(r"Days to/since earthquake")
    ax.set_ylabel(r"%s (%s)"%(name,units))

    # ############################################################
    # INSET PANEL
    # ############################################################
    axi=fig.add_axes([0.172,0.65,0.68,0.22])

    for axp in ax,axi:

        # SIGNAL
        axp.plot(t,s,'k-',alpha=0.2)
        # TIME OF EARTHQUAKE
        axp.axvline(0,color='k')
        # VALUE OF SIGNAL
        axp.plot([0],[value],marker='s',color='w',
                 markersize=10,markeredgecolor='k')
        # MAXIMA AND MINIMA
        axp.plot(tMb,sMb,'ro',markersize=3,markeredgecolor='none',label='Semidiurnal:%.4f'%float(phase_sd))
        axp.plot(tmb,smb,'ro',markersize=3,markeredgecolor='none')
        
        axp.plot(tMd,sMd,marker='s',markersize=5,markerfacecolor='none',markeredgecolor='b',linewidth=0,
                 label='Diurnal:%.4f'%float(phase_dn))
        axp.plot(tmd,smd,marker='s',markersize=5,markerfacecolor='none',markeredgecolor='b',linewidth=0)

        # SOFTED SIGNAL
        axp.plot(tMs,sMs,'b-',)
        axp.plot(tms,sms,'b-',)
        # MAXIMA AND MINIMA LONGTERM
        axp.plot(tMF,sMF,'g^',markersize=8,markeredgecolor='none',label='Fortnightly:%.4f'%float(phase_fn))
        axp.plot(tmf,smf,'gv',markersize=8,markeredgecolor='none')
        # PEAKS
        axp.plot(tMF[ipeak::2],sMF[ipeak::2],'cs',markersize=10,markeredgecolor='none',label='Monthly:%.4f'%float(phase_mn))
        axp.plot(tMF[ipeak::-2],sMF[ipeak::-2],'cs',markersize=10,markeredgecolor='none')
        axp.plot(tmf[ipeak::2],smf[ipeak::2],'cs',markersize=10,markeredgecolor='none')
        axp.plot(tmf[ipeak::-2],smf[ipeak::-2],'cs',markersize=10,markeredgecolor='none')


    axi.axvspan(tminb,tmaxb,color='r',alpha=0.2)
    axi.axvspan(tmind,tmaxd,color='k',alpha=0.2)
    ax.axvspan(tminf,tmaxf,color='g',alpha=0.2)
    ax.axvspan(tminm,tmaxm,color='c',fill=False,hatch="/")

    ax.legend(loc='lower right',prop=dict(size=10))
    axi.set_xlim((-10,10))
    axi.set_yticklabels([])

    # ############################################################
    # SAVE FIGURE
    # ############################################################
    ax.text(1.02,0.5,quakestr,
            horizontalalignment='center',verticalalignment='center',
            rotation=90,fontsize=8,color='k',alpha=0.2,
            transform=ax.transAxes)
    
    figname="%s/%s.png"%(DIRNAME,BASENAME)
    print("Saving figure ",figname)
    fig.savefig(figname)
    return fig

def quake2str(qlat,qlon,qdep,qjd):
    quakestr="QUAKE-lat_%+08.4f-lon_%+09.4f-dep_%+010.4f-JD_%.6f"%\
        (qlat,qlon,qdep,qjd)
    return quakestr

# ######################################################################
# SPICE RELATED ROUTINES
# ######################################################################
# Magnitude of a Spice state vector
def normX(state):
    x=state[0]
    d=norm(x[:3])
    v=norm(x[3:])
    return d,v

# Convert from JD to ET
# MM/DD/YYYY HH:MM:SS.DCM UTC-L
# Ephemeris time: et=sp.str2et("01/01/2015 00:00:00.000 UTC")
def jd2et(jd):

    import spiceypy as sp

    # Convert from JD to UTC seconds (seconds since J2000)
    utc=(jd-sp.j2000())/365.25*sp.jyear()

    # Compute deltat = ET - UTC
    deltat=sp.deltet(utc,"UTC");

    # Compute ET
    et=utc+deltat

    return et

# Convert from ET to JD
def et2jd(et):
    import spiceypy as sp

    # Convert et to jed
    jed=sp.unitim(et,"ET","JED")

    # Calculate the deltat at et
    deltat=sp.deltet(et,"ET");

    # Add deltat to et
    jd=jed-deltat/86400.0

    return jd

def dtime2etjd(dtime):
    import spiceypy as sp

    # dtime in DATETIME_FORMAT="%d/%m/%y %H:%M:%S"
    dtime=datetime.datetime.strptime(dtime,DATETIME_FORMAT)
    dtime=dtime.strftime("%m/%d/%Y %H:%M:%S.%f")
    qet=sp.str2et(dtime)
    qjd=et2jd(qet)

    return qet,qjd

def bodyPosition(body,et):
    import spiceypy as sp

    x,tl=sp.spkezr(body,et,"J2000","NONE","EARTH")
    R,alpha,dec=sp.recrad(x[:3])

    return R,alpha,dec

def bodyElements(body,mu,et):
    import spiceypy as sp

    x,tl=sp.spkezr(body,et,"J2000","NONE","EARTH")
    els=sp.oscltx(x,et,mu)

    return els

def bodyPosition(body,mu,et):
    import spiceypy as sp

    x,tl=sp.spkezr(body,et,"ECLIPJ2000","NONE","EARTH")

    return x


def localST(et,lon):
    """
    Local Solar time and hour angle of the sun

    et: Ephemeris time
    lon: Longitude (in degrees)
    """
    import spiceypy as sp

    # Local solar time
    lst=sp.et2lst(et,399,lon*DEG,"PLANETOGRAPHIC",51,51)

    # Hour angle
    hsun=numpy.mod((s2d(lst[0],lst[1],lst[2])-12.0)/SIDFAC*15,360)

    return lst,hsun

def bodyHA(body,et,qlon):
    import spiceypy as sp

    # SUB POINT POSITION
    pos=sp.subpnt("Intercept:  ellipsoid",
                  "EARTH",et,"IAU_EARTH","NONE",
                  body)
    lpos=sp.recpgr("EARTH",pos[0],REARTH,FEARTH);

    # LATITUDE AND LONGITUDE
    lon=lpos[0]*RAD
    lat=lpos[1]*RAD

    # print d2s(lon),d2s(lat)
    
    # DIFFERENCE IN LONGITUDE
    dlon=numpy.mod(qlon-lon,360)

    # HOUR ANGLE
    # H = LST - ALPHA
    ha=dlon

    return ha

def calculatePhases(t,s,psgn,hmoon,ps,DT=40,waves=None,verb=True):
    """
    Given a timeseries t (times), s (signal) compute the phases of
    wave (if None of all waves)
    """
    qphases=""
    speaks=""
    # ==============================
    # FIND MAXIMA AND MINIMA
    # ==============================
    # SEMIDIURNAL LEVEL PEAKS
    tmb,smb,tMb,sMb=signalBoundary(t,s)

    # ==============================
    # SMOOTH MAXIMA & MINIMA
    # ==============================
    b,a=signal.butter(8,0.125)
    sMs=signal.filtfilt(b,a,sMb,padlen=100)
    tMs=tMb
    b,a=signal.butter(8,0.125)
    sms=signal.filtfilt(b,a,smb,padlen=100)
    tms=tmb

    # FORTNIGHTLY LEVEL PEAKS (MAXIMA)
    tmF,smF,tMF,sMF=signalBoundary(tMs,sMs)

    # FORTNIGHTLY LEVEL PEAKS (MINIMA)
    tmf,smf,tMf,sMf=signalBoundary(tms,sms)

    # ==============================
    # SEMI-DIURNAL PHASE
    # ==============================
    if psgn>0:tb=tMb
    else:tb=tmb
    npeaks=len(tb)
    ipeaks=numpy.arange(npeaks)
    ipeak=ipeaks[tb<0][-1]
    dtmean=tb[ipeak+1]-tb[ipeak]
    dt=-tb[tb<0][-1]
    dtphase=dt/dtmean;
    qphases+="%.4f:%.4f;"%(dt,dtphase)
    if verb:print("\t\tSemidiurnal (%e): dt = %e, dtphase = %e"%(dtmean,dt,dtphase))
    #STORE SEMIDIURNAL PEAKS
    tps=numpy.concatenate((tb[tb<=0][-3:],tb[tb>=0][:3]))
    speaks+=";".join(["%.3f"%t for t in tps])
    speaks+="::"

    # ==============================
    # DIURNAL PHASE
    # ==============================
    if psgn>0:tp=tMb
    else:tp=tmb
    dprev=hmoon/MOONRATE
    tshift=tp+dprev
    isorts=abs(tshift).argsort()
    iso=0;dt=-1
    while dt<0:
        iprev=isorts[iso]
        dt=-tp[iprev]
        iso+=1
    dtmean=tp[iprev+2]-tp[iprev]
    dtphase=dt/dtmean
    qphases+="%.4f:%.4f;"%(dt,dtphase)
    if verb:print("\t\tDiurnal (%e): dt = %e, dtphase = %e"%(dtmean,dt,dtphase))
    
    # ==============================
    # FORTNIGHTLY PHASE
    # ==============================
    if psgn>0:tcF=tMF
    else:tcF=tmf
    npeaks=len(tcF)
    ipeaks=numpy.arange(npeaks)
    ipeak=ipeaks[tcF<0][-1]
    dtmean=tcF[ipeak+1]-tcF[ipeak]
    #if dtmean>16:dtmean=14.0
    dt=-tcF[tcF<0][-1]
    dtphase=dt/dtmean;
    qphases+="%.4f:%.4f;"%(dt,dtphase)
    if verb:print("\t\tFortnightly (%e): dt = %e, dtphase = %e"%(dtmean,dt,dtphase))
    #STORE FORNIGHTLY PEAKS
    tps=numpy.concatenate((tcF[tcF<=0][-3:],tcF[tcF>=0][:3]))
    speaks+=";".join(["%.3f"%t for t in tps])
    speaks+="::"

    # ==============================
    # MONTHLY PHASE
    # ==============================
    """
    # TAKES THE LATEST PEAK CLOSE TO THE START OF THE SYNODIC MONTH
    if psgn>0:tcF=tMF
    else:tcF=tmf
    cond=(tcF>-DT)*(tcF<+DT)
    tpF=tcF[cond]
    numpeak=len(tpF)
    ds=[]
    #You should use the synodic ps
    for tf in tpF:ds+=[min(abs(ps-tf))]
    iM=numpy.array(ds).argsort()[0]
    ipeaks=numpy.arange(npeaks)
    ipeak=ipeaks[tpF<0][-1]
    if abs(ipeak-iM)%2!=0:ipeak-=1
    if (ipeak+2)>=numpeak:npeak=ipeak-2
    else:npeak=ipeak+2
    dtmean=abs(tpF[npeak]-tpF[ipeak])
    dt=-tpF[ipeak]
    dtphase=dt/dtmean
    qphases+="%.4f:%.4f;"%(dt,dtphase)
    if verb:print "\t\tMonthly (%e): dt = %e, dtphase = %e"%(dtmean,dt,dtphase)
    #"""
    #"""
    # TAKES THE LATEST PEAK CLOSE TO THE START OF THE ANOMALISTIC MONTH
    if psgn>0:tcF=tMF
    else:tcF=tmf
    ipeaks=numpy.arange(npeaks)
    cond=tcF<0
    tpF=tcF[cond][-2:]
    ipeaks=ipeaks[cond][-2:]
    ds=[]
    #You should use the anomalistic ps (time of perigea)
    for tf in tpF:ds+=[min(abs(ps-tf))]
    iM=numpy.array(ds).argsort()[0]
    ipeak=ipeaks[iM]
    npeak=ipeak+2
    dtmean=abs(tcF[npeak]-tcF[ipeak])
    dt=-tcF[ipeak]
    dtphase=dt/dtmean
    qphases+="%.4f:%.4f;"%(dt,dtphase)
    if verb:print("\t\tMonthly (%e): dt = %e, dtphase = %e"%(dtmean,dt,dtphase))
    #"""
    speaks+=":"
    return qphases,speaks
