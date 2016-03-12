from tquakes import *
import spiceypy as sp
sp.furnsh("util/kernels/kernels.mk")

qdatetime=argv[1]
qet,qjd=dtime2etjd(qdatetime)
print "%.6f"%qjd
