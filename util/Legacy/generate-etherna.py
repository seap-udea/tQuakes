"""Funcion del programa El programa toma los datos de fecha, latitud,
longitud, profundidad de los sismos y los introduce en el texto dado
por ETERNA34. El programa genera los archivos.ini que seran llevados
luego al programa ETERNA34/BIN/Etherna-ini.

Entradas: datos de los sismos escogidos. Para darle el nombre a los
archivos, se tiene por ejemplo 000001HS donde el numero corresponde
al numero del sismo dentro de cada carpeta perteneciente a un departamento

Los departamentos: AM=Amazonas, AN= Antioquia, AR=Arauca, AT=Atlatico,
BO=Bolivar, BY=Boyaca, CA = Cauca, Caldas=Cl, CH=Choco, CO=Cordoba,
CQ=Caqueta, CS=Casanare, CE=Cesar, CU=Cundinamarca, GN=Guainia,
GU=Guajira, GV=Guaviare, HU=Huila, MA=Magdalena, ME=Meta, NA=Narino,
NS=Norte de Santander, PU=Putumayo, QU=Quindio, RI=Risaralda,
SA=Santander, SU=Sucre, TO=Tolima, VA=Valle, VP=Vaupes, VI=Vichada,
SP=SanAndresyProvidencia HS la componente


salidas: archivos con extension .ini
"""

from rutinas import *

#Base de datos de entrada
inputdb=argv[1]

#Input/Output directory
inputdir="DATABASE/"

#Archivo de Entrada
filedb=inputdir+"%s.csv"%inputdb

if isfile(filedb):
    print "Creando archivos de inicializacion para '%s'..."%inputdb
    fs=open(filedb,"r")
else:
    print "Base de datos '%s' no encontrada."%inputdb
    exit(1)

outputdir="ETERNA-INI/%s-INI/"%inputdb
if not isdir(outputdir):
    system("mkdir -p %s"%outputdir)

resultsdir="ETERNA-OUT/%s-OUT/"%inputdb
if not isdir(resultsdir):
    system("mkdir -p %s"%resultsdir)
   
corridas=open(outputdir+"corridas.bat","w")
corridas.write("mkdir %s-OUT\n"%inputdb)

b=open(outputdir+"numeracionsismos.dat","w")

contenido="""#Este archivo relaciona el numero del sismo creado con el programa generate-etherna.py con la fecha, hora y departamento donde se produjo el sismo
%-15s%-15s%-15s%-15s
"""%("# Numero","Fecha","Hora","Departamento")
contenido=contenido.replace("\n","\r\n")
b.write(contenido)

i=0
n=0
for linea in fs:
    # Se descartan las primeras lineas
    i+=1
    if i<3:continue
    n+=1

    # Identificacion del sismo
    id_sismo="%06d"%n

    # Guardo datos del sismo
    datos_sismos=linea.split(";")
    fecha_sismo=(datos_sismos[0]) # Formato: DD/MM/YYYY
    latitud_sismo=float(datos_sismos[2])
    longitud_sismo=float(datos_sismos[3])
    profundidad_sismo=(float(datos_sismos[4]))*(-1000) # m
    nombre_sismo=(datos_sismos[7])
    nombre_depto=nombre_sismo[0]
    nombre_municipio=nombre_sismo[1]
    #numero_sismo=(datos_sismos[16])
    hora_sismo=(datos_sismos[1])

    # Parto la fecha
    fecha=fecha_sismo.split("/")
    Ano_ini=fecha[2]
    Mes_ini=fecha[1]
    Dia_ini=fecha[0]
    
    # Separo ano en decada y ano
    Decada_inicio=Ano_ini[2]
    Ano_inicio=Ano_ini[3]

    # Separo hora
    hora=hora_sismo.split(":")
    hora_ini=hora[0]
    min_ini=hora[1]
    sec_ini=hora[2]
    
    # identificacion completa del sismo
    #identificacion_sismo=str(nombre_depto)+str(nombre_municipio)+numero_sismo

    # Fecha juliana del sismo
    jd=fecha2jd(fecha,hora)

    # Se resta a la fecha del sismo el valor en dias desde donde se
    # realiza elmuestreo
    dias_antes=90.0
   
    tiempo_inicial=jd-dias_antes

    #print tiempo_inicial

    # Epoca inicial
    initialepo=jdcal.jd2gcal(0.0,tiempo_inicial)

    #print tiempo_inicial, initialepo

    # Me falta calcular el tiempo inicial a partir del dato juliano
    # para reemplazarlo en el parametro INITIALEPO
    
    ano_inic=initialepo[0]
    mes_inic=initialepo[1]
    dia_inic=initialepo[2]

    # Tiempo de simulacion
    time_span="4320" # horas
   # time_span="311040" # horas

   
    # ###############################################################
    # Componente 5 horizontal del strain
    # ###############################################################
    componente=5
    nombre=id_sismo
    
    etherna=open(outputdir+"%sHS.INI"%nombre,"w")
    content=("""# This file ETJENA00.INI status 2006.04.25 containing control parameters
# for programs DETIDE 3.30 and PREGRED 3.30

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# ! NOTE: The datalines have to start with their names.       !
# !       An additional comment may follow after the values,  !
# !       delimited by a whitespace                           !
# ! Values of 0 or less causes PREGRED to calculate the       !
# ! range(s) automatically resp. to use default values        !
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# a commentline starts with an '#', it may appear at any position
# in this file. Empty lines may appear too

# The next control parameters are used by DETIDE/DESPIKE/DECIMATE:

SENSORNAME=PREDICT         # earth tide sensor name
NUMRAWCHAN=      2         # number of recorded channels
NUMBCHANEL=      2         # number of channels after DETIDE
INPFILNAME=ETJENA00.dat    # DETIDE input data filename
#CALFILNAME=ETJENA00.cal    # calibration parameters
OUTFILNAME=ETJENA00.xxx    # DECIMATE output filename
SAMPLERATE=     60         # sampling interval in seconds
DECIMATION=     12         # decimation factor for DECIMATE
#DECFILNAME=n60s5m02.nlf    # decimation filter 1 min to  5 min 
DECFILNAME=n14h5m01.nlf    # decimation filter 5 min to 1 h
STATLATITU=     %.3f    # stations latitude  in degree
STATLONITU=     %.3f       # stations longitude in degree
STATELEVAT=     %.3f       # stations elevation in meter
STATGRAVIT=      0.        # stations gravity in m/s**2
STATAZIMUT=      0.        # stations azimuth in degree from north
INITIALEPO= %s  %s   %s    # initial epoch in year,month,day
PREDICSPAN=     %s         # prediction time span in hours for PREDICT
TIDALCOMPO=     %d         # tidal component, see manual
TIDALPOTEN=      7         # tidal potential development
AMTRUNCATE=  1.D-6         # amplitude threshold    
POLTIDECOR=   0.00         # pole tide amplitude factor
LODTIDECOR=   0.00         # LOD  tide amplitude factor
STEPDETLIM=      5.        # DESPIKE limit for step detection  (nm/s**2) 
SPIKDETLIM=      2.        # DESPIKE limit for spike detection (nm/s**2)

#TIDALPARAM=  0.000000  0.600000   1.15000    0.0000 long   #tidal param. 
#TIDALPARAM=  0.600001  0.910000   1.14673   -0.2474 Q1     #tidal param.
#TIDALPARAM=  0.910001  0.949000   1.14882    0.0804 O1     #tidal param.
#TIDALPARAM=  0.949001  0.980000   1.13070    0.2132 M1     #tidal param.
#TIDALPARAM=  0.980001  1.012000   1.13599    0.2062 K1     #tidal param.
#TIDALPARAM=  1.012001  1.050000   1.15354    0.0801 J1     #tidal param.
#TIDALPARAM=  1.050001  1.500000   1.14851   -0.0251 OO1    #tidal param.
#TIDALPARAM=  1.500001  1.875000   1.15205    2.4463 2N2    #tidal param.
#TIDALPARAM=  1.875001  1.910000   1.17054    2.5425 N2     #tidal param.
#TIDALPARAM=  1.910001  1.950000   1.18705    2.0327 M2     #tidal param.
#TIDALPARAM=  1.950001  1.985000   1.22450    4.1630 L2     #tidal param.
#TIDALPARAM=  1.985001  2.500000   1.18963    0.6271 S2     #tidal param.
#TIDALPARAM=  2.500001  3.500000   1.06234    0.3783 M3     #tidal param.
#TIDALPARAM=  3.500001  7.000000   1.02000    0.0000 M4M6   #tidal param.

                                                                             
TIDALPARAM=  0.000000  0.501369   1.16000    0.0000 long   #tidal param. 
TIDALPARAM=  0.501370  0.842147   1.16000    0.0000 SGQ1   #tidal param.                                
TIDALPARAM=  0.842148  0.860293   1.16000    0.0000 2Q1    #tidal param.  
TIDALPARAM=  0.860294  0.878675   1.16000    0.0000 SGM1   #tidal param.  
TIDALPARAM=  0.878676  0.896968   1.16000    0.0000 Q1     #tidal param.  
TIDALPARAM=  0.896969  0.911390   1.16000    0.0000 RO1    #tidal param.  
TIDALPARAM=  0.911391  0.931206   1.16000    0.0000 O1     #tidal param.  
TIDALPARAM=  0.931207  0.947991   1.16000    0.0000 TAU1   #tidal param.  
TIDALPARAM=  0.947992  0.967660   1.16000    0.0000 NO1    #tidal param.  
TIDALPARAM=  0.967661  0.981854   1.16000    0.0000 CHI1   #tidal param.  
TIDALPARAM=  0.981855  0.996055   1.16000    0.0000 PI1    #tidal param.  
TIDALPARAM=  0.996056  0.998631   1.16000    0.0000 P1     #tidal param.  
TIDALPARAM=  0.998632  1.001369   1.16000    0.0000 S1     #tidal param.  
TIDALPARAM=  1.001370  1.004107   1.16000    0.0000 K1     #tidal param.  
TIDALPARAM=  1.004108  1.006845   1.16000    0.0000 PSI1   #tidal param.  
TIDALPARAM=  1.006846  1.023622   1.16000    0.0000 PHI1   #tidal param.  
TIDALPARAM=  1.023623  1.035379   1.16000    0.0000 TET1   #tidal param.  
TIDALPARAM=  1.035380  1.057485   1.16000    0.0000 J1     #tidal param.  
TIDALPARAM=  1.057486  1.071833   1.16000    0.0000 SO1    #tidal param.  
TIDALPARAM=  1.071834  1.090052   1.16000    0.0000 OO1    #tidal param.  
TIDALPARAM=  1.090053  1.470243   1.16000    0.0000 NU1    #tidal param.  
TIDALPARAM=  1.470244  1.845944   1.16000    0.0000 EPS2   #tidal param.  
TIDALPARAM=  1.845945  1.863026   1.16000    0.0000 2N2    #tidal param.  
TIDALPARAM=  1.863027  1.880264   1.16000    0.0000 MU2    #tidal param.    
TIDALPARAM=  1.880265  1.897351   1.16000    0.0000 N2     #tidal param.    
TIDALPARAM=  1.897352  1.914128   1.16000    0.0000 NU2    #tidal param.  
TIDALPARAM=  1.914129  1.950419   1.16000    0.0000 M2     #tidal param.  
TIDALPARAM=  1.950420  1.964767   1.16000    0.0000 LAM2   #tidal param.  
TIDALPARAM=  1.964768  1.984282   1.16000    0.0000 L2     #tidal param.  
TIDALPARAM=  1.984283  1.998996   1.16000    0.0000 T2     #tidal param.  
TIDALPARAM=  1.998997  2.002736   1.16000    0.0000 S2     #tidal param.  
TIDALPARAM=  2.002737  2.022488   1.16000    0.0000 K2     #tidal param.  
TIDALPARAM=  2.022489  2.057484   1.16000    0.0000 ETA2   #tidal param.  
TIDALPARAM=  2.057485  2.451943   1.16000    0.0000 2K2    #tidal param.  
TIDALPARAM=  2.451944  2.881176   1.16000    0.0000 MN3    #tidal param.  
TIDALPARAM=  2.881177  3.381378   1.16000    0.0000 M3     #tidal param.  
TIDALPARAM=  3.381379  4.347615   1.16000    0.0000 M4     #tidal param. 
                                           
                                                                     
# End of file ETJENA00.INI                                          
                                          
                                    
"""%(latitud_sismo,
     longitud_sismo,
     profundidad_sismo,
     ano_inic,
     mes_inic,
     dia_inic,
     time_span,
     componente))
         
    content=content.replace("\n","\r\n")
    
    etherna.write(content)
    etherna.close()

    # ###############################################################
    # Componente 4 vertical del strain
    # ###############################################################

    componente=4
    nombre=id_sismo
    etherna=open(outputdir+"%sVS.INI"%nombre,"w")
    content=("""# This file ETJENA00.INI status 2006.04.25 containing control parameters
# for programs DETIDE 3.30 and PREGRED 3.30

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# ! NOTE: The datalines have to start with their names.       !
# !       An additional comment may follow after the values,  !
# !       delimited by a whitespace                           !
# ! Values of 0 or less causes PREGRED to calculate the       !
# ! range(s) automatically resp. to use default values        !
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# a commentline starts with an '#', it may appear at any position
# in this file. Empty lines may appear too

# The next control parameters are used by DETIDE/DESPIKE/DECIMATE:

SENSORNAME=PREDICT         # earth tide sensor name
NUMRAWCHAN=      2         # number of recorded channels
NUMBCHANEL=      2         # number of channels after DETIDE
INPFILNAME=ETJENA00.dat    # DETIDE input data filename
#CALFILNAME=ETJENA00.cal    # calibration parameters
OUTFILNAME=ETJENA00.xxx    # DECIMATE output filename
SAMPLERATE=     60         # sampling interval in seconds
DECIMATION=     12         # decimation factor for DECIMATE
#DECFILNAME=n60s5m02.nlf    # decimation filter 1 min to  5 min 
DECFILNAME=n14h5m01.nlf    # decimation filter 5 min to 1 h
STATLATITU=     %.3f    # stations latitude  in degree
STATLONITU=     %.3f       # stations longitude in degree
STATELEVAT=     %.3f       # stations elevation in meter
STATGRAVIT=      0.        # stations gravity in m/s**2
STATAZIMUT=      0.        # stations azimuth in degree from north
INITIALEPO= %s  %s   %s    # initial epoch in year,month,day
PREDICSPAN=     %s         # prediction time span in hours for PREDICT
TIDALCOMPO=     %d         # tidal component, see manual
TIDALPOTEN=      7         # tidal potential development
AMTRUNCATE=  1.D-6         # amplitude threshold    
POLTIDECOR=   0.00         # pole tide amplitude factor
LODTIDECOR=   0.00         # LOD  tide amplitude factor
STEPDETLIM=      5.        # DESPIKE limit for step detection  (nm/s**2) 
SPIKDETLIM=      2.        # DESPIKE limit for spike detection (nm/s**2)

#TIDALPARAM=  0.000000  0.600000   1.15000    0.0000 long   #tidal param. 
#TIDALPARAM=  0.600001  0.910000   1.14673   -0.2474 Q1     #tidal param.
#TIDALPARAM=  0.910001  0.949000   1.14882    0.0804 O1     #tidal param.
#TIDALPARAM=  0.949001  0.980000   1.13070    0.2132 M1     #tidal param.
#TIDALPARAM=  0.980001  1.012000   1.13599    0.2062 K1     #tidal param.
#TIDALPARAM=  1.012001  1.050000   1.15354    0.0801 J1     #tidal param.
#TIDALPARAM=  1.050001  1.500000   1.14851   -0.0251 OO1    #tidal param.
#TIDALPARAM=  1.500001  1.875000   1.15205    2.4463 2N2    #tidal param.
#TIDALPARAM=  1.875001  1.910000   1.17054    2.5425 N2     #tidal param.
#TIDALPARAM=  1.910001  1.950000   1.18705    2.0327 M2     #tidal param.
#TIDALPARAM=  1.950001  1.985000   1.22450    4.1630 L2     #tidal param.
#TIDALPARAM=  1.985001  2.500000   1.18963    0.6271 S2     #tidal param.
#TIDALPARAM=  2.500001  3.500000   1.06234    0.3783 M3     #tidal param.
#TIDALPARAM=  3.500001  7.000000   1.02000    0.0000 M4M6   #tidal param.

                                                                             
TIDALPARAM=  0.000000  0.501369   1.16000    0.0000 long   #tidal param. 
TIDALPARAM=  0.501370  0.842147   1.16000    0.0000 SGQ1   #tidal param.                                
TIDALPARAM=  0.842148  0.860293   1.16000    0.0000 2Q1    #tidal param.  
TIDALPARAM=  0.860294  0.878675   1.16000    0.0000 SGM1   #tidal param.  
TIDALPARAM=  0.878676  0.896968   1.16000    0.0000 Q1     #tidal param.  
TIDALPARAM=  0.896969  0.911390   1.16000    0.0000 RO1    #tidal param.  
TIDALPARAM=  0.911391  0.931206   1.16000    0.0000 O1     #tidal param.  
TIDALPARAM=  0.931207  0.947991   1.16000    0.0000 TAU1   #tidal param.  
TIDALPARAM=  0.947992  0.967660   1.16000    0.0000 NO1    #tidal param.  
TIDALPARAM=  0.967661  0.981854   1.16000    0.0000 CHI1   #tidal param.  
TIDALPARAM=  0.981855  0.996055   1.16000    0.0000 PI1    #tidal param.  
TIDALPARAM=  0.996056  0.998631   1.16000    0.0000 P1     #tidal param.  
TIDALPARAM=  0.998632  1.001369   1.16000    0.0000 S1     #tidal param.  
TIDALPARAM=  1.001370  1.004107   1.16000    0.0000 K1     #tidal param.  
TIDALPARAM=  1.004108  1.006845   1.16000    0.0000 PSI1   #tidal param.  
TIDALPARAM=  1.006846  1.023622   1.16000    0.0000 PHI1   #tidal param.  
TIDALPARAM=  1.023623  1.035379   1.16000    0.0000 TET1   #tidal param.  
TIDALPARAM=  1.035380  1.057485   1.16000    0.0000 J1     #tidal param.  
TIDALPARAM=  1.057486  1.071833   1.16000    0.0000 SO1    #tidal param.  
TIDALPARAM=  1.071834  1.090052   1.16000    0.0000 OO1    #tidal param.  
TIDALPARAM=  1.090053  1.470243   1.16000    0.0000 NU1    #tidal param.  
TIDALPARAM=  1.470244  1.845944   1.16000    0.0000 EPS2   #tidal param.  
TIDALPARAM=  1.845945  1.863026   1.16000    0.0000 2N2    #tidal param.  
TIDALPARAM=  1.863027  1.880264   1.16000    0.0000 MU2    #tidal param.    
TIDALPARAM=  1.880265  1.897351   1.16000    0.0000 N2     #tidal param.    
TIDALPARAM=  1.897352  1.914128   1.16000    0.0000 NU2    #tidal param.  
TIDALPARAM=  1.914129  1.950419   1.16000    0.0000 M2     #tidal param.  
TIDALPARAM=  1.950420  1.964767   1.16000    0.0000 LAM2   #tidal param.  
TIDALPARAM=  1.964768  1.984282   1.16000    0.0000 L2     #tidal param.  
TIDALPARAM=  1.984283  1.998996   1.16000    0.0000 T2     #tidal param.  
TIDALPARAM=  1.998997  2.002736   1.16000    0.0000 S2     #tidal param.  
TIDALPARAM=  2.002737  2.022488   1.16000    0.0000 K2     #tidal param.  
TIDALPARAM=  2.022489  2.057484   1.16000    0.0000 ETA2   #tidal param.  
TIDALPARAM=  2.057485  2.451943   1.16000    0.0000 2K2    #tidal param.  
TIDALPARAM=  2.451944  2.881176   1.16000    0.0000 MN3    #tidal param.  
TIDALPARAM=  2.881177  3.381378   1.16000    0.0000 M3     #tidal param.  
TIDALPARAM=  3.381379  4.347615   1.16000    0.0000 M4     #tidal param. 
                                           
                                                                     
# End of file ETJENA00.INI                                          
                                          
                                    
"""%(latitud_sismo,
     longitud_sismo,
     profundidad_sismo,
     ano_inic,
     mes_inic,
     dia_inic,
     time_span,
     componente))
     
    
    content=content.replace("\n","\r\n")
    
    etherna.write(content)
    etherna.close()


    #######################################
    # Componente 2: desplazamiento vertical
    #######################################
    componente=2
    nombre=id_sismo
    etherna=open(outputdir+"%sVD.INI"%nombre,"w")
    content=("""# This file ETJENA00.INI status 2006.04.25 containing control parameters
# for programs DETIDE 3.30 and PREGRED 3.30

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# ! NOTE: The datalines have to start with their names.       !
# !       An additional comment may follow after the values,  !
# !       delimited by a whitespace                           !
# ! Values of 0 or less causes PREGRED to calculate the       !
# ! range(s) automatically resp. to use default values        !
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# a commentline starts with an '#', it may appear at any position
# in this file. Empty lines may appear too

# The next control parameters are used by DETIDE/DESPIKE/DECIMATE:

SENSORNAME=PREDICT         # earth tide sensor name
NUMRAWCHAN=      2         # number of recorded channels
NUMBCHANEL=      2         # number of channels after DETIDE
INPFILNAME=ETJENA00.dat    # DETIDE input data filename
#CALFILNAME=ETJENA00.cal    # calibration parameters
OUTFILNAME=ETJENA00.xxx    # DECIMATE output filename
SAMPLERATE=     60         # sampling interval in seconds
DECIMATION=     12         # decimation factor for DECIMATE
#DECFILNAME=n60s5m02.nlf    # decimation filter 1 min to  5 min 
DECFILNAME=n14h5m01.nlf    # decimation filter 5 min to 1 h
STATLATITU=     %.3f    # stations latitude  in degree
STATLONITU=     %.3f       # stations longitude in degree
STATELEVAT=     %.3f       # stations elevation in meter
STATGRAVIT=      0.        # stations gravity in m/s**2
STATAZIMUT=      0.        # stations azimuth in degree from north
INITIALEPO= %s  %s   %s    # initial epoch in year,month,day
PREDICSPAN=     %s         # prediction time span in hours for PREDICT
TIDALCOMPO=     %d         # tidal component, see manual
TIDALPOTEN=      7         # tidal potential development
AMTRUNCATE=  1.D-6         # amplitude threshold    
POLTIDECOR=   0.00         # pole tide amplitude factor
LODTIDECOR=   0.00         # LOD  tide amplitude factor
STEPDETLIM=      5.        # DESPIKE limit for step detection  (nm/s**2) 
SPIKDETLIM=      2.        # DESPIKE limit for spike detection (nm/s**2)

#TIDALPARAM=  0.000000  0.600000   1.15000    0.0000 long   #tidal param. 
#TIDALPARAM=  0.600001  0.910000   1.14673   -0.2474 Q1     #tidal param.
#TIDALPARAM=  0.910001  0.949000   1.14882    0.0804 O1     #tidal param.
#TIDALPARAM=  0.949001  0.980000   1.13070    0.2132 M1     #tidal param.
#TIDALPARAM=  0.980001  1.012000   1.13599    0.2062 K1     #tidal param.
#TIDALPARAM=  1.012001  1.050000   1.15354    0.0801 J1     #tidal param.
#TIDALPARAM=  1.050001  1.500000   1.14851   -0.0251 OO1    #tidal param.
#TIDALPARAM=  1.500001  1.875000   1.15205    2.4463 2N2    #tidal param.
#TIDALPARAM=  1.875001  1.910000   1.17054    2.5425 N2     #tidal param.
#TIDALPARAM=  1.910001  1.950000   1.18705    2.0327 M2     #tidal param.
#TIDALPARAM=  1.950001  1.985000   1.22450    4.1630 L2     #tidal param.
#TIDALPARAM=  1.985001  2.500000   1.18963    0.6271 S2     #tidal param.
#TIDALPARAM=  2.500001  3.500000   1.06234    0.3783 M3     #tidal param.
#TIDALPARAM=  3.500001  7.000000   1.02000    0.0000 M4M6   #tidal param.

                                                                             
TIDALPARAM=  0.000000  0.501369   1.16000    0.0000 long   #tidal param. 
TIDALPARAM=  0.501370  0.842147   1.16000    0.0000 SGQ1   #tidal param.                                
TIDALPARAM=  0.842148  0.860293   1.16000    0.0000 2Q1    #tidal param.  
TIDALPARAM=  0.860294  0.878675   1.16000    0.0000 SGM1   #tidal param.  
TIDALPARAM=  0.878676  0.896968   1.16000    0.0000 Q1     #tidal param.  
TIDALPARAM=  0.896969  0.911390   1.16000    0.0000 RO1    #tidal param.  
TIDALPARAM=  0.911391  0.931206   1.16000    0.0000 O1     #tidal param.  
TIDALPARAM=  0.931207  0.947991   1.16000    0.0000 TAU1   #tidal param.  
TIDALPARAM=  0.947992  0.967660   1.16000    0.0000 NO1    #tidal param.  
TIDALPARAM=  0.967661  0.981854   1.16000    0.0000 CHI1   #tidal param.  
TIDALPARAM=  0.981855  0.996055   1.16000    0.0000 PI1    #tidal param.  
TIDALPARAM=  0.996056  0.998631   1.16000    0.0000 P1     #tidal param.  
TIDALPARAM=  0.998632  1.001369   1.16000    0.0000 S1     #tidal param.  
TIDALPARAM=  1.001370  1.004107   1.16000    0.0000 K1     #tidal param.  
TIDALPARAM=  1.004108  1.006845   1.16000    0.0000 PSI1   #tidal param.  
TIDALPARAM=  1.006846  1.023622   1.16000    0.0000 PHI1   #tidal param.  
TIDALPARAM=  1.023623  1.035379   1.16000    0.0000 TET1   #tidal param.  
TIDALPARAM=  1.035380  1.057485   1.16000    0.0000 J1     #tidal param.  
TIDALPARAM=  1.057486  1.071833   1.16000    0.0000 SO1    #tidal param.  
TIDALPARAM=  1.071834  1.090052   1.16000    0.0000 OO1    #tidal param.  
TIDALPARAM=  1.090053  1.470243   1.16000    0.0000 NU1    #tidal param.  
TIDALPARAM=  1.470244  1.845944   1.16000    0.0000 EPS2   #tidal param.  
TIDALPARAM=  1.845945  1.863026   1.16000    0.0000 2N2    #tidal param.  
TIDALPARAM=  1.863027  1.880264   1.16000    0.0000 MU2    #tidal param.    
TIDALPARAM=  1.880265  1.897351   1.16000    0.0000 N2     #tidal param.    
TIDALPARAM=  1.897352  1.914128   1.16000    0.0000 NU2    #tidal param.  
TIDALPARAM=  1.914129  1.950419   1.16000    0.0000 M2     #tidal param.  
TIDALPARAM=  1.950420  1.964767   1.16000    0.0000 LAM2   #tidal param.  
TIDALPARAM=  1.964768  1.984282   1.16000    0.0000 L2     #tidal param.  
TIDALPARAM=  1.984283  1.998996   1.16000    0.0000 T2     #tidal param.  
TIDALPARAM=  1.998997  2.002736   1.16000    0.0000 S2     #tidal param.  
TIDALPARAM=  2.002737  2.022488   1.16000    0.0000 K2     #tidal param.  
TIDALPARAM=  2.022489  2.057484   1.16000    0.0000 ETA2   #tidal param.  
TIDALPARAM=  2.057485  2.451943   1.16000    0.0000 2K2    #tidal param.  
TIDALPARAM=  2.451944  2.881176   1.16000    0.0000 MN3    #tidal param.  
TIDALPARAM=  2.881177  3.381378   1.16000    0.0000 M3     #tidal param.  
TIDALPARAM=  3.381379  4.347615   1.16000    0.0000 M4     #tidal param. 
                                           
                                                                     
# End of file ETJENA00.INI                                          
                                          
                                    
"""%(latitud_sismo,
     longitud_sismo,
     profundidad_sismo,
     ano_inic,
     mes_inic,
     dia_inic,
     time_span,
     componente))
         
    
    content=content.replace("\n","\r\n")

    
    etherna.write(content)
    etherna.close()





#################
#PARTE FINAL
################


    # Agregando el codigo de DOS al archivo corridas
    for suffix in "HS","VS","VD":
        nombresuf=nombre+suffix
        contenido=("""
copy %s-INI\%s.INI
rename %s.INI %s.INI
echo %s > PROJECT
PREDICT.EXE
copy %s.PRD %s-OUT
del %s
del %s.*
        """%(inputdb,nombresuf,nombresuf,nombresuf,nombresuf,nombresuf,inputdb,nombresuf,nombresuf))
        corridas.write(contenido)

    # Agregar la linea del archivo numeracionsismos
    contenido=("""%-15s%-15s%-15s%-15s\n"""%(id_sismo,"%02d/%02d/%d"%(dia_inic,mes_inic,ano_inic),"%2s:%2s:%2s"%(hora_ini,min_ini,sec_ini),nombre_sismo))
    contenido=contenido.replace("\n","\r\n")
    b.write(contenido)
    
# Cierro archivos
corridas.close()
fs.close()
b.close()

