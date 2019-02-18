from tquakes import *
import spiceypy as sp
sp.furnsh("util/kernels/kernels.mk")

verbose=1
freq=1000

# ############################################################
# CONVERT XLS TO CSV
# ############################################################
filexls=argv[1]
label=argv[2]

if os.path.isfile("%s.xls"%filexls):
    print "%s.xls..."%filexls
    system("LC_NUMERIC='en_US.UTF-8' LC_CURRENCY=' ' /usr/bin/ssconvert %s.xls %s.csv 2> /tmp/convert"%(filexls,filexls))
else:
    print "File %s.csv already found..."%filexls

# ############################################################
# LOAD CSV FILE WITH PROFESORES
# ############################################################
csvfile=open("%s.csv"%filexls,"rU")
content=csv.DictReader(csvfile,fieldnames=FIELDS_CSV,dialect="excel",delimiter=",")

# ############################################################
# LOAD DATABASE
# ############################################################
connection=connectDatabase()
db=connection.cursor()

# ############################################################
# GET QUAKE STRINGS
# ############################################################
q=db.execute("select quakestr from Quakes;")
qs=[s[0] for s in db.fetchall()]
q=db.execute("select customid from Quakes;")
cs=[s[0] for s in db.fetchall()]
q=db.execute("select quakeid from Quakes;")
qids=[s[0] for s in db.fetchall()]

# ############################################################
# GET DATA FROM FILE
# ############################################################
itot=0
iins=0
iskp=0
ibad=0
print "Starting earthquake insertion..."
for quake in content:

    try:depth=float(quake['Profundidad'])
    except:continue

    if(verbose):print "-- %d --"%itot
    if(verbose):print "Inserting a new quake into database..."

    # COUNTER
    itot+=1

    #Check longitude and latitude
    qlon=float(quake["Longitud"])
    qlat=float(quake["Latitud"])
    if numpy.abs(qlon)>180 or numpy.abs(qlat)>90:
        #print "Skipping earthquake..."
        ibad+=1
        continue

    # NEW FIELDS
    quake["qtype"]=quake["Tipo"]
    quake["qstrikemain"]=quake["Strike_main"]
    quake["qstrikeaux"]=quake["Strike_aux"]
    quake["qdipmain"]=quake["Dip_main"]
    quake["qdipaux"]=quake["Dip_aux"]
    quake["qrakemain"]=quake["Rake_main"]
    quake["qrakeaux"]=quake["Rake_aux"]

    quake["qfocaltype"]=quake["Tipo focal"]
    quake["qgrade"]=quake["Grado"]
    quake["qdepthfm"]=quake["Profundidad Focal"]
    quake["qvtr"]=quake["VTR"]
    quake["extra1"]=quake["Extra1"]
    quake["extra2"]=quake["Extra2"]
    quake["extra3"]=quake["Extra3"]
    quake["extra4"]=quake["Extra4"]

    quake["overwrite"]=quake["Sobreescribe"]
    quake["customid"]=quake["Identificador"]
    quake["qclass"]=quake["Clasificacion"]
    
    # CONVERT DATE TO FORMAT
    quake["qdatetime"]=quake["Fecha"]+" "+quake["Hora UTC"];

    if (itot%freq)==0:
        print "Analizando sismo %d fecha = %s (insertados %d, saltados %d)"%(itot,quake["qdatetime"],iins,iskp)

    # CALCULATE JULIAN DAY AND EPHEMERIS TIME
    try:
        qdate=datetime.datetime.strptime(quake["qdatetime"],DATETIME_FORMAT)
    except:
        print "Date is not in the format %s"%DATETIME_FORMAT
        exit(1)

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
    qgen=1
    if (quake["quakestr"] in qs) or (quake["customid"] in cs):
        if quake["overwrite"]=="0":
            iskp+=1
            if(verbose):print >>stderr,"\tQuake already exist in database. Skipping."
            continue
        else:
            qgen=0
            if quake["quakestr"] in qs:
                for i,q in enumerate(qs):
                    if q==quake["quakestr"]:
                        quakeid=qids[i]
                        break
            if quake["customid"] in cs:
                for i,c in enumerate(cs):
                    if c==quake["customid"]:
                        quakeid=qids[i]
                        break
            
            iins+=1
            if(verbose):print >>stderr,"\tOld quake (quakeid=%s). Overwriting."%quakeid;
    else:
        iins+=1
        if(verbose):print >>stderr,"\tNew quake. Inserting.";

    # GENERATE A RANDOM ID
    if qgen:
        q=1
        while q:
            quakeid=randomStr(7)
            q=db.execute("select quakeid from Quakes where quakeid='%s';"%quakeid)
    quake["quakeid"]=quakeid
    if(verbose):print "\tQuake id: ",quakeid

    # CALCULATE HOUR ANGLE OF THE MOON AND THE SUN
    hmoon=bodyHA("MOON",qet,qlon)
    hsun=bodyHA("SUN",qet,qlon)
    quake["hmoon"]="%.5f"%(hmoon)
    quake["hsun"]="%.5f"%(hsun)

    if(verbose):print "\tDate: ",quake["qdatetime"]
    if(verbose):print "\tJD: ",quake["qjd"]
    if(verbose):print "\tET: ",quake["qet"]

    print>>stderr,"Inserting quake ",quake["quakeid"]
    fields=FIELDSTXT.replace("(","(extra5,")
    sql="insert into Quakes %s values ('%s',"%(fields,label)
    for dbfield in FIELDS_DB:
        try:fieldname=FIELDS_DB2CSV[dbfield]
        except KeyError:fieldname=dbfield

        #print "\nOriginal:",dbfield,fieldname,quake[fieldname]
        
        try:value=quake[fieldname]
        except KeyError:value=""

        #print "Para la base:",fieldname,value

        sql+="'%s',"%value
    sql=sql.strip(",")
    sql+=") on duplicate key update %s;\n"%FIELDSUP

    if(verbose):print >>stderr,sql
    db.execute(sql)

print "Number of quakes read: ",itot
print "Number of quakes inserted: ",iins
print "Number of quakes skipped: ",iskp
print "Number of quakes bad formed: ",ibad
connection.commit()
