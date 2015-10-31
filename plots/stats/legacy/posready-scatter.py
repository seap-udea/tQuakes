from scatter import *
qpos=mysqlArray("select qlat,qlon from Quakes where astatus+0>0;",db)
qlat=numpy.array([float(pos[0]) for pos in qpos])
qlon=numpy.array([float(pos[1]) for pos in qpos])
plotmap(qlat,qlon)
