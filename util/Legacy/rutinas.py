from numpy import *
from sys import exit,argv,stderr,stdout
from os.path import isfile,isdir
from os import system
from math import *
import jdcal
import cmath as cm

#Conversion a dia juliano para restar 90 dias
def fecha2jd(fecha,hora):
    siglo,desfase=jdcal.gcal2jd(int(fecha[2]),int(fecha[1]),int(fecha[0]))
    jd=siglo+desfase+(int(hora[0])+int(hora[1])/60.+int(hora[2])/3600.)/24
    return jd

#Calculo de la fecha juliana
def fecha2jd_all(fecha_sismo):
    Ano=fecha_sismo[0]
    Mes=fecha_sismo[1]
    Dia=fecha_sismo[2]
    Hora=fecha_sismo[3]
    Minuto=fecha_sismo[4]
    Segundo=fecha_sismo[5]
    siglo,desfase=jdcal.gcal2jd(int(Ano),int(Mes),int(Dia))
    jd=siglo+desfase+(int(Hora)+int(Minuto)/60.+int(Segundo)/3600.)/24
    return jd

def signal_teo(t,ft,T,N,K):
    w=2*pi*k/T
    serie=ft[0]+2*ft[k]*cm.exp(1j*w*t)
    serie=serie/N
    return real(serie)

def all_signal_teo(t,ft,T,N,ko,dk):
    serie=ft[0]
    for k in xrange(ko,ko+dk):
        w=2*pi*k/T
        serie+=2*ft[k]*cm.exp(1j*w*t)
    serie=serie/N
    return real(serie)

def omega2k(wo,T,N):
    w1=2*pi/T
    k=round((wo-w1)*N*T/(2*pi*(N-2))+1)
    return int(k)

def phase(ft,to,T,N,periodo):
    wo=2*pi/periodo
    k=omega2k(wo,T,N)
    x=real(ft[k])
    y=imag(ft[k])
    phase=(atan2(y,x)*180/pi)
    phase=mod(phase,360.0)
    wk=2*pi*k/T
    wkt=(wk*to)*180/pi
    phasek=wkt+phase
    phasek=mod(phasek,360.0)
    return phasek

