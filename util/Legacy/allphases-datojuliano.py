from rutinas import *

inputdir="ETERNA-INI/"
outputdir="ETERNA-OUT/"

inputdb=argv[1]
f=open(inputdir+"%s-INI/numeracionsismos.dat"%inputdb,"r")
allphases=[]
n=1
for line in f:
    if "#" in line:continue
    line=line.strip()
    parts=line.split()
    numsismo=parts[0]
    fecha=parts[1]
    hora=parts[2]
   #print fecha, hora, numsismo

    fechavin=fecha.split("/")
    horavin=hora.split(":")
    #print fechavin
    #print horavin

    fechadelarchivo=[fechavin[2],fechavin[1],fechavin[0],horavin[0],horavin[1],horavin[2]]
    jd=fecha2jd_all(fechadelarchivo)
    #print "jd", jd

    fechadelsismo=jd+90.0
    print "fechadelsismo=",fechadelsismo
####################################
#pasando nuevamente a dato gregoriano
####################################    
    fechaorigensismo=jdcal.jd2gcal(0.0,fechadelsismo)
    #print "tiempot=", fechaorigensismo

    dia_inicio=str(fechaorigensismo[2])
    mes_inicio=str(fechaorigensismo[1])
    ano_inicio=str(fechaorigensismo[0])

    origensismo=dia_inicio+"/"+mes_inicio+"/"+ano_inicio
    print "origensismo=", origensismo

    print "Calculando fases de sismo '%s'..."%numsismo
    cmd="python fourier-sismos-datojuliano.py %s/%s-OUT/ %s %s %s"%(outputdir,inputdb,origensismo,hora,numsismo)
    system(cmd)
    phases=loadtxt(".phases")
    allphases+=[[int(numsismo)]+[int(fechadelsismo)]+phases.tolist()]
    n+=1
   # if n>2:break

savetxt("allphases-%s.dat"%(inputdb),allphases)


f.close()
