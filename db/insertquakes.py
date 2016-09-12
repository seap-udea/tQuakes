from tquakes import *
import spiceypy as sp
sp.furnsh("util/kernels/kernels.mk")

# ############################################################
# LOAD DATABASE
# ############################################################
tQuakes,connection=loadDatabase()
db=connection.cursor()

# ############################################################
# LOAD CSV FILE WITH PROFESORES
# ############################################################
filecsv=argv[1]
csvfile=open("%s"%filecsv,"rU")
content=csv.DictReader(csvfile,fieldnames=FIELDS_CSV,dialect="excel",delimiter=";")

# ############################################################
# GET DATA FROM FILE
# ############################################################
itot=0
iins=0
iskp=0
for quake in content:
    try:depth=float(quake['Profundidad'])
    except:continue

    print "-- %d --"%itot
    print "Inserting a new quake into database..."

    # GENERATE A RANDOM ID
    q=1
    while q:
        quakeid=randomStr(7)
        q=db.execute("select quakeid from Quakes where quakeid='%s';"%quakeid)
    quake["quakeid"]=quakeid
    print "\tQuake id: ",quakeid

    # CALCULATE JULIAN DAY AND EPHEMERIS TIME
    quake["qdatetime"]=quake["Fecha"]+" "+quake["Hora UTC"];
    """
    qdate=datetime.datetime.strptime(quake["qdatetime"],DATETIME_FORMAT)
    quake["qjd"]=date2jd(qdate)
    """
    dtime=qdate.strftime("%m/%d/%Y %H:%M:%S.%f")
    qet=sp.str2et(dtime)
    qjd=et2jd(et)
    quake["qet"]="%.3f"%et
    quake["qjd"]="%.6f"%qjd

    # CALCULATE HOUR ANGLE OF THE MOON AND THE SUN
    qlon=float(quake["Longitud"])
    hmoon=bodyHA("MOON",qet,qlon)
    hsun=bodyHA("SUN",qet,qlon)
    quake["hmoon"]="%.5f"%(hmoon)
    quake["hsun"]="%.5f"%(hsun)

    print "\tDate: ",quake["qdatetime"]
    print "\tJD: ",quake["qjd"]
    print "\tET: ",quake["qet"]

    # CALCULATE QUAKE STRING
    quake["quakestr"]=quake2str(float(quake["Latitud"]),float(quake["Longitud"]),float(quake["Profundidad"]),float(quake["qjd"]))
    print "\tString: ",quake["quakestr"]

    itot+=1
    # if itot>20:break #DEBUGGING

    # CHECK IF QUAKE ALREADY EXIST IN DATABASE
    q=db.execute("select quakestr from Quakes where quakestr='%s';"%quake["quakestr"])
    if q:
        iskp+=1
        print "\tQuake %s already exist in database. Skipping."%quake["quakestr"]
        continue
    else:
        iins+=1
        print "\tNew quake. Inserting.";
    
    sql="insert into Quakes %s values ("%(FIELDSTXT)
    for dbfield in FIELDS_DB:
        try:fieldname=FIELDS_DB2CSV[dbfield]
        except KeyError:fieldname=dbfield
        try:value=quake[fieldname]
        except KeyError:value=""
        sql+="'%s',"%value
    sql=sql.strip(",")
    sql+=") on duplicate key update %s;\n"%FIELDSUP
    db.execute(sql)

print "Number of quakes read: ",itot
print "Number of quakes inserted: ",iins
print "Number of quakes skipped: ",iskp
connection.commit()
