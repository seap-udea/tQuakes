from tquakes import *
import spiceypy as sp
sp.furnsh("util/kernels/kernels.mk")

#INPUT
qdatetime=argv[1]
qlon=float(argv[2])

#DATE
qdate=datetime.datetime.strptime(qdatetime,DATETIME_FORMAT)
dtime=qdate.strftime("%m/%d/%Y %H:%M:%S.%f")
qet=sp.str2et(dtime)

# CALCULATE HOUR ANGLE OF THE MOON AND THE SUN
hmoon=bodyHA("MOON",qet,qlon)
hsun=bodyHA("SUN",qet,qlon)

print "%.3f,%.3f"%(hmoon,hsun)
