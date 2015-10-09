from tquakes import *

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
for quake in content:
    try:depth=float(quake['Profundidad'])
    except:continue

    # GENERATE A RANDOM STRING
    q=1
    while q:
        quakeid=randomStr(7)
        q=db.execute("select quakeid from Quakes where quakeid='%s';"%quakeid)

    sql="insert into Quakes %s values ("%(FIELDSTXT)
    for dbfield in FIELDS_DB:
        fieldname=FIELDS_DB2CSV[dbfield]
        value=quake[fieldname]
        sql+="'%s',"%value
    sql+="'%s',"%quakeid
    sql=sql.strip(",")
    sql+=") on duplicate key update %s;\n"%FIELDSUP
    print sql
    db.execute(sql)
    break

connection.commit()

