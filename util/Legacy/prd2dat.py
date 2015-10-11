"""
Funcion del Programa
El programa convierte los archivos con extension .PRD ubicados en el directorio etherna-results a archivos con formato de matriz. El resultado es un archivo que contiene fecha, desplazaminto vertical VD, horizontal strain HS y vertical strain VS y de extension .dat


Entradas:
- Nombre
- Archivo PRD: etherna-results/<nombre>VD.PRD,<nombre>HS.PRD, nombre>VS.PRD

Salidas:
- Archivo dat: etherna-dat/<nombre>.dat

"""
from rutinas import *

def fecha2jd(fecha,hora):
    fecha=fecha.split("/")
    hora=hora.split("/")
    siglo,desfase=jdcal.gcal2jd(int(Ano),int(Mes),int(Dia))
    jd=siglo+desfase+(int(Hora)+int(Minuto)/60.+int(Segundo)/3600.)/24
    return jd

    
dir=argv[1]+"/"
nombre=argv[2]

base="%s"%nombre
name=dir+base+"HS.PRD"
f=open(name)

name2=dir+base+"VS.PRD"
g=open(name2)

name3=dir+base+"VD.PRD"
l=open(name3)


#Ingresa datos en una matriz
X=[]
i=0
qstart=False
print "Leyendo los datos de los archivos de salida..."
print "\tArchivo HS..."
for line in f:
    i+=1
    #Toma los dato a partir de cierta fila 

    if line=="\r\n":continue
    if "C*******" in line:
        qstart=True
        continue
    if not qstart:continue
    if "PREDICT" in line:continue
    if "777777" in line:continue
    if "999999" in line:continue
    if "888888" in line:continue

    valores=line.split()
    #Despliega el strain
    disp=float(valores[2])
        
    Fecha=valores[0]
    print Fecha
    Ano=Fecha[0:4]
    #Para extaer de la cadena el valor del mes
    Mes=Fecha[4:6]
    #Para extraer de la cadena Fecha el valor del Dia
    Dia=Fecha[6:8]
    #Extraer de Tiempo datos de hora, minuto y segundo
    #Hora
    Tiempo=valores[1]
    
    if Tiempo=="0":
        Tiempo="000000"

    tiempoint=int(Tiempo)
    Tiempo="%06d"%tiempoint
    Hora=Tiempo[0:2]
    Minuto=Tiempo[2:4]
    Segundo=Tiempo[4:6]

    #Ingresa los valores de jd y desplazamiento en la matriz
    fecha=Ano+"/"+Mes+"/"+Dia
    hora=Hora+"/"+Minuto+"/"+Segundo
    jd=fecha2jd(fecha,hora)
    X+=[[jd,disp]]
 
    
    # Realiza la misma rutina anterior para cada una de las otras componentes VD, 
 # HS, VS

M=[]
i=0
qstart=False
print "\tArchivo VS..."
for line in g:
    i+=1
    if line=="\r\n":continue
    if "C*******" in line:
        qstart=True
        continue
    if not qstart:continue
    if "PREDICT" in line:continue
    if "777777" in line:continue
    if "999999" in line:continue
    if "888888" in line:continue
    
    valores=line.split()
    disp=float(valores[2])
    
    Fecha=valores[0]
    Ano=Fecha[0:4]
    # Para extaer de la cadena el valor del mes
    Mes=Fecha[4:6]
    # Para extraer de la cadena Fecha el valor del Dia
    Dia=Fecha[6:8]
    # Extraer de Tiempo datos de hora, minuto y segundo
    # Hora
    Tiempo=valores[1]
    
    if Tiempo=="0":
        Tiempo="000000"
        
    tiempoint=int(Tiempo)
    Tiempo="%06d"%tiempoint
    Hora=Tiempo[0:2]
    Minuto=Tiempo[2:4]
    Segundo=Tiempo[4:6]
    
    fecha=Ano+"/"+Mes+"/"+Dia
    hora=Hora+"/"+Minuto+"/"+Segundo
    jd=fecha2jd(fecha,hora)
    M+=[[jd,disp]]


N=[]
i=0
qstart=False
print "\tArchivo VD..."
for line in l:
    i+=1
    if line=="\r\n":continue

    if "C*******" in line:
        qstart=True
        continue
    if not qstart:continue
    if "PREDICT" in line:continue
    if "777777" in line:continue
    if "999999" in line:continue
    if "888888" in line:continue

    valores=line.split()
    disp=float(valores[2])
        
    Fecha=valores[0]
    Ano=Fecha[0:4]
    #Para extaer de la cadena el valor del mes
    Mes=Fecha[4:6]
    #Para extraer de la cadena Fecha el valor del Dia
    Dia=Fecha[6:8]
    #Extraer de Tiempo datos de hora, minuto y segundo
    #Hora
    Tiempo=valores[1]
    
    if Tiempo=="0":
        Tiempo="000000"
        
    tiempoint=int(Tiempo)
    Tiempo="%06d"%tiempoint
    Hora=Tiempo[0:2]
    Minuto=Tiempo[2:4]
    Segundo=Tiempo[4:6]

    fecha=Ano+"/"+Mes+"/"+Dia
    hora=Hora+"/"+Minuto+"/"+Segundo
    jd=fecha2jd(fecha,hora)
    N+=[[jd,disp]]


X=array(X)
M=array(M)
N=array(N)


Z=hstack((X,M,N))

f.close()
g.close()
l.close()


#Guarda los archivos 
savetxt(dir+"/"+nombre+".dat",array(Z))



