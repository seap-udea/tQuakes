# ############################################################
# IMPORT TOOLS
# ############################################################
from tquakes import *
from matplotlib import use
use('Agg')
import matplotlib.pyplot as plt
execfile("%s.conf"%BASENAME)

verbose=0
if verbose:tqdm=lambda x:x

try:
    criteria=argv[1]
except:
    criteria="(2>0)"

# ############################################################
# DATABASE CONNECTION
# ############################################################
connection=connectDatabase()
db=connection.cursor()

# ############################################################
# LOOK FOR QUAKES
# ############################################################
try:
    Quakes=getAllQuakes(db,cond="((ABS(qstrikemain)+ABS(qdipmain)+ABS(qrakemain))>0 and (ABS(qstrikeaux)+ABS(qdipaux)+ABS(qrakeaux)>0)) and %s"%criteria)
    nquakes=len(Quakes)
except:
    print "Something went wrong with the criteria"
    exit(1)
if nquakes==0:
    print "No quakes fulfilling the criteria"
    exit(0)

print "Calculating the TCFS of %d earthquakes..."%nquakes
freq=max(int(nquakes/10),1)

# ############################################################
# COMPUTATION
# ############################################################
#for i,quake in tqdm(enumerate(Quakes)):
nodata=0
for i,quake in enumerate(Quakes):

    if (i%freq)==0:
        print "Quake %d/%d..."%(i,nquakes)
    
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #BASIC INFO
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    quakeid=quake["quakeid"]
    if verbose:print "Processing quake %d/%d %s..."%(i,nquakes,quakeid)

    qjd=float(quake["qjd"])
    if verbose:print "\tDate: %s (JD = %s)"%(quake["qdatetime"],qjd)

    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #SQL UPDATE STRING
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    sql="update Quakes set "
    
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #GET TIDAL TIMESERIES
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #Get data
    try:
        data=getQuakeData(quakeid)
    except AssertionError:
        print "No data for %s"%quakeid
        nodata+=1
        continue
    
    qjds=data[:,0]

    #Interpolate strains
    components=["T=ST.L=B.C=NSEXP","T=ST.L=B.C=EW","T=ST.L=B.C=SHEARNE",
                "T=ST.L=B.C=AREAL","T=ST.L=B.C=CUBIC"]
    strain=dict()
    for component in components:
        try:
            qvalues=data[:,GOTIC2_NCOLUMNS[component]]
        except:
            print "Problems with (%s,%s)"%(quakeid,component)
            exit(1)
        strain[component]=interpolate(qjds,qvalues,kind="slinear")
    
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #GET TIME OF PREVIOUS MAXIMUM
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #Strain
    listMax=[
        dict(
            var="st",
            etots=numpy.sqrt(data[:,GOTIC2_NCOLUMNS["T=ST.L=B.C=NSEXP"]]**2+data[:,GOTIC2_NCOLUMNS["T=ST.L=B.C=EW"]]**2)
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
    qjdmaxs=dict()
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
        qjdmaxs[qMax["var"]]=qjdmax
        #Show
        """
        if verbose:print numpy.column_stack(((ts-qjd)*24,sts,dsts,ddsts)))
        if verbose:print "\tTime of latest maximum for var. %s: jd = %lf (dt = %lf hours)"%(qMax["var"],qjdmax,(qjdmax-qjd)*24)
        if verbose:print "\tValue at latest maximum: strain = %lf"%strainmax
        exec("qjd%smax=qjdmax"%qMax["var"])
        raw_input()
        """

    sql+="qjdmax='%s',"%sql_qjdmax

    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #TCFS COMBINATIONS
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    tcfs_string=""
    sigman_string=""
    sigmas_string=""
    for key,tcfsCombination in TCFS_COMBINATIONS.items():
        if verbose:print "\tComputing TCFS for:",key
        plane=tcfsCombination["plane"]

        #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        #FOCAL MECHANISM
        #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        #Main plane
        phi=float(quake["qstrike%s"%plane]) #Strike
        delta=float(quake["qdip%s"%plane]) #Dip
        lamb=float(quake["qrake%s"%plane]) #Rake
        
        if verbose:print "\t\tFocal mechanism: Strike = %.2f, Dip = %.2f, Rake = %.2f"%(phi,
                                                                             delta,
                                                                             lamb)
        #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        #TIME
        #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        time=tcfsCombination["time"]
        var=tcfsCombination["var"]
        if time=="quake":jd=qjd
        elif time=="max":jd=qjdmaxs[var]
        else:jd=qjd

        if verbose:print "\t\tTime of computation (%s,%s) = %.7lf"%(time,var,jd)
        
        #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        #CALCULATE STRAIN
        #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        eNS=strain["T=ST.L=B.C=NSEXP"](jd)
        eEW=strain["T=ST.L=B.C=EW"](jd)
        shear=strain["T=ST.L=B.C=SHEARNE"](jd)
        areal=strain["T=ST.L=B.C=AREAL"](jd)
        cubic=strain["T=ST.L=B.C=CUBIC"](jd)
        if verbose:print "\t\tStrains:"
        if verbose:print "\t\t\teNS=%.2lf,eEW=%.2lf"%(eNS,eEW)
        if verbose:print "\t\t\tshear=%.2lf,areal=%.2lf,cubic=%.2lf"%(shear,
                                                           areal,
                                                           cubic)
        
        #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        #CALCULATE TCFS
        #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        mu=tcfsCombination["mu"]
        sigmaN,sigmaS,tcfs=calculateTCFS(phi*DEG,delta*DEG,lamb*DEG,
                           eNS,eEW,shear,areal,cubic,mu)
        if verbose:print "\t\tStress (mu = %.2lf): Normal = %.3lf, Sheart = %.3lf"%(mu,
                                                                                    sigmaN,sigmaS)
        if verbose:print "\t\tTCFS (mu = %.2lf) = %.3lf"%(mu,tcfs)

        sigman_string+="%.7e;"%sigmaN
        sigmas_string+="%.7e;"%sigmaS

    sql+="sigman='%s',sigmas='%s',"%(sigman_string,sigmas_string)
    
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #STORE VALUES IN DATABASE
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    sql=sql.strip(",")
    sql+=" where quakeid='%s'"%quakeid
    if verbose:
        print "\tExecuting command:\n\t\t%s"%sql
        raw_input("Press enter to continue...")
    else:
        db.execute(sql)

print "Data no available for %d quakes"%nodata
connection.commit()
