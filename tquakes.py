import csv,datetime,commands,re,os,numpy,cmath,time
from sys import exit,argv
from util.jdcal import *

# ######################################################################
# MACROS
# ######################################################################
system=os.system
PI=numpy.pi
sleep=time.sleep

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

# ######################################################################
# CORE ROUTINES
# ######################################################################
class dict2obj(object):
    def __init__(self,dic={}):self.__dict__.update(dic)
    def __add__(self,other):
        for attr in other.__dict__.keys():
            exec("self.%s=other.%s"%(attr,attr))
        return self

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

# ######################################################################
# CONFIGURATION
# ######################################################################
CONF=loadConf("configuration")

# ######################################################################
# REGULAR ROUTINES
# ######################################################################
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

def randomStr(N):
    import string,random
    string=''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(N))
    return string

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
