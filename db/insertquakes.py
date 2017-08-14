from tquakes import *
import spiceypy as sp
sp.furnsh("util/kernels/kernels.mk")

verbose=0
freq=10

# ############################################################
# LOAD DATABASE
# ############################################################
tQuakes,connection=loadDatabase()
db=connection.cursor()

# ############################################################
# GET QUAKE STRINGS
# ############################################################
q=db.execute("select quakestr from Quakes;")
qs=[s[0] for s in db.fetchall()]

# ############################################################
# LOAD CSV FILE WITH PROFESORES
# ############################################################
filecsv=argv[1]
csvfile=open("%s"%filecsv,"rU")
content=csv.DictReader(csvfile,fieldnames=FIELDS_CSV,dialect="excel",delimiter=",")

# ############################################################
# GET DATA FROM FILE
# ############################################################
itot=0
iins=0
iskp=0
print "Starting earthquake insertion..."
for quake in content:

    try:depth=float(quake['Profundidad'])
    except:continue

    if(verbose):print "-- %d --"%itot
    if(verbose):print "Inserting a new quake into database..."

    # COUNTER
    itot+=1
    quake["qdatetime"]=quake["Fecha"]+" "+quake["Hora UTC"];
    if (itot%freq)==0:
        print "Analizando sismo %d fecha = %s (insertados %d, saltados %d)"%(itot,quake["qdatetime"],iins,iskp)

    # CALCULATE JULIAN DAY AND EPHEMERIS TIME
    try:
        qdate=datetime.datetime.strptime(quake["qdatetime"],DATETIME_FORMAT)
    except:
        qdate=datetime.datetime.strptime(quake["qdatetime"],"%Y/%m/%d %H:%M:%S")
        quake["Fecha"]=qdate.strftime("%d/%m/%Y")
        quake["qdate"]=quake["Fecha"]
        quake["qdatetime"]=quake["Fecha"]+" "+quake["Hora UTC"];
        
    quake["qjd"]=date2jd(qdate)
    dtime=qdate.strftime("%m/%d/%Y %H:%M:%S.%f")

    # EPHEMERIS TIME
    qet=sp.str2et(dtime)
    qjd=et2jd(qet)
    quake["qet"]="%.3f"%qet
    quake["qjd"]="%.6f"%qjd

    # CALCULATE QUAKE STRING
    quake["quakestr"]=quake2str(float(quake["Latitud"]),float(quake["Longitud"]),float(quake["Profundidad"]),float(quake["qjd"]))
    if(verbose):print "\tString: ",quake["quakestr"]

    # CHECK IF QUAKE ALREADY EXIST IN DATABASE
    if quake["quakestr"] in qs:
        iskp+=1
        if(verbose):print "\tQuake already exist in database. Skipping."
        continue
    else:
        iins+=1
        if(verbose):print "\tNew quake. Inserting.";

    # GENERATE A RANDOM ID
    q=1
    while q:
        quakeid=randomStr(7)
        q=db.execute("select quakeid from Quakes where quakeid='%s';"%quakeid)
    quake["quakeid"]=quakeid
    if(verbose):print "\tQuake id: ",quakeid

    # CALCULATE HOUR ANGLE OF THE MOON AND THE SUN
    qlon=float(quake["Longitud"])
    hmoon=bodyHA("MOON",qet,qlon)
    hsun=bodyHA("SUN",qet,qlon)
    quake["hmoon"]="%.5f"%(hmoon)
    quake["hsun"]="%.5f"%(hsun)

    if(verbose):print "\tDate: ",quake["qdatetime"]
    if(verbose):print "\tJD: ",quake["qjd"]
    if(verbose):print "\tET: ",quake["qet"]

    sql="insert into Quakes %s values ("%(FIELDSTXT)
    for dbfield in FIELDS_DB:
        try:fieldname=FIELDS_DB2CSV[dbfield]
        except KeyError:fieldname=dbfield
        try:value=quake[fieldname]
        except KeyError:value=""
        #if(verbose):print dbfield,value
        sql+="'%s',"%value
    sql=sql.strip(",")
    sql+=") on duplicate key update %s;\n"%FIELDSUP
    db.execute(sql)
    if(verbose):print sql

print "Number of quakes read: ",itot
print "Number of quakes inserted: ",iins
print "Number of quakes skipped: ",iskp
connection.commit()
