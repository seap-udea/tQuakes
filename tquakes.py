import MySQLdb as mdb
import csv
from sys import exit,argv
from os import system
from datetime import date

###################################################
#CONFIGURACION
###################################################
BASENAME="tQuakes"
DATABASE="tQuakes"
USER="tquakes"
PASSWORD="quakes2015"

###################################################
#GLOBAL
###################################################
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

FIELDSTXT="("
FIELDSUP=""
for field in FIELDS_DB:
    FIELDSTXT+="%s,"%field
    FIELDSUP+="%s=VALUES(%s),"%(field,field)
FIELDSTXT+="quakeid,"
FIELDSTXT=FIELDSTXT.strip(",")+")"
FIELDSUP+="quakeid=VALUES(quakeid),"
FIELDSUP=FIELDSUP.strip(",")

###################################################
#ROUTINES
###################################################
class dict2obj(object):
    def __init__(self,dic={}):self.__dict__.update(dic)
    def __add__(self,other):
        for attr in other.__dict__.keys():
            exec("self.%s=other.%s"%(attr,attr))
        return self

def loadDatabase(server='localhost',
                 user=USER,
                 password=PASSWORD,
                 database=DATABASE):
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
