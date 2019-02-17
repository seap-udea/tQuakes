# ############################################################
# IMPORT TOOLS
# ############################################################
from tquakes import *
from matplotlib import use
use('Agg')
import matplotlib.pyplot as plt
execfile("%s.conf"%BASENAME)

# ############################################################
# DATABASE CONNECTION
# ############################################################
connection=connectDatabase()
db=connection.cursor()

# ############################################################
# LOOK FOR QUAKES
# ############################################################
Quakes=getAllQuakes(db,cond="extra5='tcfs'")
nquakes=len(Quakes)

# ############################################################
# CONSTANTS
# ############################################################
#Constantes
u= 30 #constante de lame rigidez en GPa
v= 0.25  # coeficiente de Poisson

#coeficientes de friccion
u1=0.2
u2=0.4
u3=0.6
u4=0.8

#for i,quake in tqdm(enumerate(Quakes)):
for i,quake in enumerate(Quakes):

    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #BASIC INFO
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    quakeid=quake["quakeid"]
    print("Processing quake %d/%d %s..."%(i,nquakes,quakeid))

    qjd=float(quake["qjd"])
    print "\tDate: %s (JD = %s)"%(quake["qdatetime"],qjd)

    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #SQL UPDATE STRING
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    sql="update Quakes set "
    
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #FOCAL MECHANISM
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #Main plane
    phimain=float(quake["qstrikemain"]) #Strike
    deltamain=float(quake["qdipmain"]) #Dip
    lambdamain=float(quake["qrakemain"]) #Rake

    #Auxiliar plane
    phiaux=float(quake["qstrikeaux"]) #Strike
    deltaaux=float(quake["qdipaux"]) #Dip
    lambdaaux=float(quake["qrakeaux"]) #Rake

    print "\tFocal mechanism:"
    print "\t\tMain (strike = %.2f, dip = %.2f, rake = %.2f)"%(phimain,deltamain,lambdamain)
    print "\t\tAux (strike = %.2f, dip = %.2f, rake = %.2f)"%(phiaux,deltaaux,lambdaaux)
        
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #GET TIDAL TIMESERIES
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #Get data
    data=getQuakeData(quakeid)
    qjds=data[:,0]

    #Interpolate strains
    components=["T=ST.L=S.C=NSEXP","T=ST.L=S.C=EW","T=ST.L=S.C=SHEARNE",
                "T=ST.L=S.C=AREAL","T=ST.L=S.C=CUBIC"]
    strain=dict()
    for component in components:
        qvalues=data[:,GOTIC2_NCOLUMNS[component]]
        strain[component]=interpolate(qjds,qvalues,kind="slinear")
    
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #GET TIME OF PREVIOUS MAXIMUM
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #Strain
    listMax=[
        dict(
            var="st",
            etots=numpy.sqrt(data[:,GOTIC2_NCOLUMNS["T=ST.L=B.C=NSEXP"]]**2+data[:,GOTIC2_NCOLUMNS["T=ST.L=S.C=EW"]]**2)
        ),
        dict(
            var="rd",
            etots=data[:,GOTIC2_NCOLUMNS["T=RD.L=B.C=UPWARD"]]
        ),
        dict(
            var="gv",
            etots=data[:,GOTIC2_NCOLUMNS["T=GV.L=B.C=UPWARD"]]
        ),
    ]

    sql_qjdmax=""
    for qMax in listMax:
        straintot=interpolate(qjds,qMax["etots"],kind="slinear")
        ts=numpy.linspace(qjd-1.0,qjd,50)
        its=numpy.arange(len(ts))
        sts=straintot(ts)
        dsts=numpy.concatenate((sts[1:]-sts[:-1],[0]));dsts[dsts>0]=+1;dsts[dsts<0]=-1
        ddsts=numpy.concatenate((dsts[1:]-dsts[:-1],[0]))
        qjdmax=ts[its[ddsts==-2][-1]+1]
        strainmax=straintot(qjdmax)
        sql_qjdmax+="%.7lf;"%qjdmax
        
        #Show
        """
        print(numpy.column_stack(((ts-qjd)*24,sts,dsts,ddsts)))
        print "\tTime of latest maximum for var. %s: jd = %lf (dt = %lf hours)"%(qMax["var"],qjdmax,(qjdmax-qjd)*24)
        print "\tValue at latest maximum: strain = %lf"%strainmax
        exec("qjd%smax=qjdmax"%qMax["var"])
        raw_input()
        """

    sql+="qjdmax='%s',"%sql_qjdmax
    print(sql)
    
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #CALCULATE TCFS
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    raw_input()

    """
    print (ezz)
    eyz=0
    exz=0
    exx=eEW
    eyy=eNS
    exy=shear   #porque segun Gotic2 es (dv/dy+dv/dx)/2

    factor=((2*u)/(1-2*v))
    print ("factor=", factor)
    print ("")
    
    a=sin(30*pi/180)
    print ("VERIFICANDO sen(30)=0.5,  a=", a)

    A=(exx*(1-v)+(eyy*v)+(ezz*v))*(cos(phi*pi/180)*sin(delta*pi/180))-((1-2*v)*(exy)*(sin(phi*pi/180)*sin(delta*pi/180)))+((1-2*v)*(exz)*(cos(delta*pi/180)))
    B=((1-2*v)*(exy)*(cos(phi*pi/180)*sin(delta*pi/180)))-((exx*v+eyy*(1-v)+ezz*v)*(sin(phi*pi/180)*sin(delta*pi/180)))+((1-2*v)*(eyz)*cos(delta*pi/180))
    C=((1-2*v)*(exz)*cos(phi*pi/180)*sin(delta*pi/180))-((1-2*v)*(eyz)*sin(phi*pi/180)*sin(delta*pi/180))+(((1-v)*(ezz)+(exx)*v+(eyy)*v)*cos(delta*pi/180))
    
    q=[A,B,C]
    Q1=factor*A
    Q2=factor*B
    Q3=factor*C

    Q=[Q1,Q2,Q3]  #vector traccion
    print ("A=", A, "B=", B, "C=", C, "q=", q)
    print ("Vector traccion Q=", Q)
    print ("")

    #Calculo del esfuerzo normal
    
    DeltasigmaN=(Q1*(cos(phi*pi/180)*sin(delta*pi/180)))-(Q2*(sin(phi*pi/180)*sin(delta*pi/180)))+(Q3*cos(delta*pi/180))

    #Calculo del esfuerzo cortante

    DeltasigmaS=(Q1*(sin(phi*pi/180)*cos(lambdas*pi/180)-cos(phi*pi/180)*cos(delta*pi/180)*sin(lambdas*pi/180)))+(Q2*(cos(phi*pi/180)*cos(lambdas*pi/180)+sin(phi*pi/180)*cos(delta*pi/180)*sin(lambdas*pi/180)))+(Q3*(sin(delta*pi/180)*sin(lambdas*pi/180)))

    print ("Esfuerzo Normal=", DeltasigmaN, "Esfuerzo Cortante=", DeltasigmaS)
    print ("")

    ##########################################
    #Calculo del Tidal Coulomb Failure Stress
    ##########################################
    
    DeltasigmaC1=DeltasigmaS+u1*DeltasigmaN
    DeltasigmaC2=DeltasigmaS+u2*DeltasigmaN
    DeltasigmaC3=DeltasigmaS+u3*DeltasigmaN
    DeltasigmaC4=DeltasigmaS+u4*DeltasigmaN
    print ("PRIMER PLANO, TFCS para diferentes coeficientes de friccion")
    print ("u1=", u1, "TFCS1=", DeltasigmaC1)
    print ("u2=", u2, "TFCS2=", DeltasigmaC2)
    print ("u3=", u3, "TFCS3=", DeltasigmaC3)
    print ("u4=", u4, "TFCS4=", DeltasigmaC4)
    print ("")
    """
    
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #STORE VALUES IN DATABASE
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    
