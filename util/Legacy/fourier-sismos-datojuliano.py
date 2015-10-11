#PROGRAMA PARA CALCULAR LA FASE DEL SISMO

###############################
#PAQUETES EXTERNOS
###############################
from rutinas import *
import numpy as np
from matplotlib.pyplot import*
import cmath as cm

###############################
#PARAMETROS
###############################
outdir=argv[1]+"/"
fecha=argv[2]
hora=argv[3]
numsismo=argv[4]
archivo=outdir+"%s.dat"%numsismo

if not isfile(archivo):
    print "Archivo de datos '%s' no existe."%archivo
    exit(1)

fechavec=fecha.split("/")
horavec=hora.split(":")
fecha_sismo=[fechavec[2],fechavec[1],fechavec[0],horavec[0],horavec[1],horavec[2]]

print "Analizando sismo '%s' en %s, %s,..."%(numsismo,fecha,hora)


###############################
#PROGRAMA
###############################
jd=fecha2jd_all(fecha_sismo)

print "\tLeyendo archivo de datos..."
signal_original=loadtxt(archivo,delimiter=" ")

# Analisis
tiempot=jd
#print "Propiedades:"
#print "\tDia juliano sismo: ",jd

phasesytiempos=[]
periodos=[0.5,1.0,7.0,15.0,30.0,60.0]
#print "Fases y  tiempo juliano"
for periodo in periodos:

    print "Fase : ",periodo

    grafper=1.5*periodo
    cond=(abs(signal_original[:,0]-tiempot)<grafper)
    signal=signal_original[cond,:]

    tiempoij=signal[0][0]
    deltatiempo=tiempot-tiempoij
    
   # print "\tdeltatiempo ventana:" , deltatiempo
    print "\tTiempo inicial ventana: ",tiempoij

    t=signal[:,0]
    t=t-t[0]
    s=signal[:,1]   #Esta es la componente HS. Las demas componentes tiene el mismo valor de fase
    N=len(s)

   # print "\tN=", N
    wo=2*pi/periodo

   # print "\tvalor de wo=", wo

    #ft=fft.fft(s,N) #Calcula Fast Fourier Transform fft

    #ft:vector de amplitudes de las componentes de Fourier
    T=t[-1]
    k=omega2k(wo,T,N)
   # print "\tvalor de k=", k
    #T representa la duracion en meses, pero se expresa en dias. El
    #periodo (nperiodo) tambien se expresa en dias
    duracion=T
    
   # print "\tduracion=", duracion

    k=omega2k(wo,T,N)

    ft=fft.fft(s,N) #Calcula Fast Fourier Transform fft

    phasek=phase(ft,deltatiempo,T,N,periodo)

    phasesytiempos+=[phasek]
   # print "\tphasesytiempos=", phasesytiempos
    print "\t\tComponent P = %.2f, Phase = %6.3f grados, tiempojd = %.2f" %(periodo,phasek,jd)


savetxt(".phases",array(phasesytiempos))    

