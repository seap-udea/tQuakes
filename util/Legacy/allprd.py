from rutinas import *

inputdir="ETERNA-INI/"
outputdir="ETERNA-OUT/"

inputdb=argv[1]
f=open(inputdir+"%s-INI/numeracionsismos.dat"%inputdb,"r")
for line in f:
    if "#" in line:continue
    line=line.strip()
    numsismo=line.split()[0]
    print "Generando datos de sismo '%s'..."%numsismo
    cmd="python prd2dat.py %s/%s-OUT/ %s"%(outputdir,inputdb,numsismo)
    system(cmd)
f.close()
