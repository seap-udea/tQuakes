from tquakes import *
import spiceypy as sp
sp.furnsh("util/kernels/kernels.mk")

# ############################################################
# LOAD DATABASE
# ############################################################
tQuakes,connection=loadDatabase()
db=connection.cursor()

i=0

f=open("failed.dat","r")
for line in f.readlines():
    quakeid=line.strip()
    if quakeid=="":continue
    i+=1
    print "Updating %s..."%quakeid
    sql="update Quakes set astatus='0' where quakeid='%s'"%(quakeid)
    db.execute(sql)
    connection.commit()

f.close()
