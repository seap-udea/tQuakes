# ############################################################
# IMPORT TOOLS
# ############################################################
from tquakes import *
from matplotlib import use
use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from mpl_toolkits.basemap import Basemap as map,shiftgrid
import matplotlib.patches as patches
confile=prepareScript()
conf=execfile(confile)

# ############################################################
# CONNECT TO DATABASE
# ############################################################
connection=connectDatabase()
db=connection.cursor()

# ############################################################
# PREPARE PLOTTING REGION
# ############################################################
fig,axs=subPlots(plt,[1])

# ############################################################
# COMPONENT AND PHASE INFORMATION
# ############################################################
info=COMPONENTS_DICT[component]
compnum=info[0]
compname=info[1]

info=PHASES_DICT[phase]
phasenum=info[0]
phasename=info[1]

numpy.random.seed(seed)

# ############################################################
# SAMPLE SETS
# ############################################################
sample_sets=[
    dict2obj(dict(
        title="Whole country, All times",
        dateini="1993-01-01 0:0:0",
        dateend="2015-12-31 0:0:0",
        center=(6.5,-74.5),
        dlat=12.0,
        dlon=14.0,
        Mlmin=3.0,
        Mlmax=7.0,
        depthmin=0.0,
        depthmax=700.0,
    ))
    ,
    dict2obj(dict(
        title="Whole country, Period A",
        dateini="1993-01-01 0:0:0",
        dateend="2008-03-01 0:0:0",
        center=(6.5,-74.5),
        dlat=12.0,
        dlon=14.0,
        Mlmin=3.0,
        Mlmax=7.0,
        depthmin=0.1,
        depthmax=700.0
    ))
    ,
    dict2obj(dict(
        title="Whole country, Period B",
        dateini="2008-03-01 0:0:0",
        dateend="2015-12-31 0:0:0",
        center=(6.5,-74.5),
        dlat=12.0,
        dlon=14.0,
        Mlmin=2.0,
        Mlmax=7.0,
        depthmin=70.0,
        depthmax=700.0
    ))
]

# ############################################################
# GET QUAKES
# ############################################################
osearch=search
header=["Wave"]
matriz=[]
i=1
for s in sample_sets:
    title=s.title+", M>%.1f"%s.Mlmin
    print "Results for sample:",title
    header+=[title]
    rows=[]
    row=[]
    j=1
    for phase in ['sd','dn','fn','mn']:
        info=PHASES_DICT[phase]
        phasenum=info[0]
        phasename=info[1]
        print "\tPhase:",phasename
        rows+=[phasename]

        search=osearch
        dl=s.dlat/10.0
        dt=s.dlon/10.0
        latb=s.center[0]-s.dlat/2;latu=s.center[0]+s.dlat/2
        lonl=s.center[1]-s.dlon/2;lonr=s.center[1]+s.dlon/2
        jd1=date2jd(datetime.datetime.strptime(s.dateini,"%Y-%m-%d %H:%M:%S"))
        jd2=date2jd(datetime.datetime.strptime(s.dateend,"%Y-%m-%d %H:%M:%S"))

        search=search+"""and
        Ml+0>=%.1f AND Ml+0<%.1f and 
        qdepth+0>=%.2f and qdepth+0<%.2f and 
        qlat+0>=%.2f and qlat+0<%.2f and 
        qlon+0>=%.2f and qlon+0<%.2f and
        qjd+0>=%.5f and qjd+0<=%.5f
        limit %d"""%(s.Mlmin,s.Mlmax,
                     s.depthmin,s.depthmax,
                     latb,latu,
                     lonl,lonr,
                     jd1,jd2,
                     limit)
        qids,quakes=getPhases(search,component,db,vvv=False)
        nquakes=len(qids)

        #print "Search: ",search
        print "\t\tNumber of quakes: ",nquakes

        # ############################################################
        # GLOBAL SCHUSTER P-VALUE
        # ############################################################
        if random:phases=360*numpy.random.random(nquakes)
        else:
            phs=quakes[:,4+phasenum]
            cond=phs<=1
            phs=phs[cond]
            quakes=quakes[cond]
            nquakes=len(phs)
            phases=numpy.array(360*phs)

        #"""
        logpt,dlogpt=schusterValue(phases*DEG,
                                   qbootstrap=qbootstrap,
                                   facbootstrap=0.8,
                                   bootcycles=nsamples)
        #"""
        #logpt=-i;dlogpt=j
        j+=1

        nboot=numpy.int(facbootstrap*nquakes)
        print "\t\tGlobal p-value: log(p) = %.1f +/- %.1f (N=%d)"%(logpt,dlogpt,nboot)
        row+=["%.1f (%.1f) [%d]"%(logpt,dlogpt,nboot)]
    
    i+=1
    matriz+=[row]

# PRINT MATRIX
f=open("/media/sf_jzuluaga/Dropbox/MiInvestigacion/Tesis/MAREAS-Y-SISMOS-GLORIA/PAPERS/PAPER1-FIRST-RESULTS/resultados.txt","w")
for j in xrange(len(header)):f.write(header[j]+";");
f.write("\n")
for i in xrange(len(rows)):
    f.write(rows[i]+";");
    for j in xrange(len(header)-1):
        f.write(matriz[j][i]+";")
    f.write("\n")
