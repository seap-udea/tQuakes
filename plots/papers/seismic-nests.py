# ############################################################
# IMPORT TOOLS
# ############################################################
from tquakes import *
from matplotlib import use
use('Agg')
import matplotlib.pyplot as plt
#from mpl_toolkits.basemap import Basemap as map,shiftgrid
import matplotlib.patches as patches
from scipy.optimize import leastsq
import spiceypy as sp
sp.furnsh("util/kernels/kernels.mk")
confile=prepareScript()
conf=execfile(confile)

try:
    qload=argv[1]
except:
    qload=1

# ############################################################
# CONNECT TO DATABASE
# ############################################################
connection=connectDatabase()
db=connection.cursor()

# ############################################################
# COMPONENT AND PHASE INFORMATION
# ############################################################
info=COMPONENTS_DICT[component]
compnum=info[0]
compname=info[1]

info=PHASES_DICT[phase]
phasenum=info[0]
phasename=info[1]

# ############################################################
# GET PHASES
# ############################################################
latb=center[0]-dlat/2;latu=center[0]+dlat/2
lonl=center[1]-dlon/2;lonr=center[1]+dlon/2
jd1=date2jd(datetime.datetime.strptime(dateini,"%Y-%m-%d %H:%M:%S"))
jd2=date2jd(datetime.datetime.strptime(dateend,"%Y-%m-%d %H:%M:%S"))

search="""where qphases<>'' and 
qdeptherr/1<qdepth/1 and
Ml+0>=%.2f AND Ml+0<%.2f and 
qdepth+0>=%.2f and qdepth+0<%.2f and 
qdeptherr/1<qdepth/1 and
qlat+0>=%.2f and qlat+0<%.2f and 
qlon+0>=%.2f and qlon+0<%.2f and
qjd+0>=%.5f and qjd+0<=%.5f and
(cluster1='0' or cluster1 like '-%%') and
astatus+0=4 
limit %d"""%(Mlmin,Mlmax,
             depthmin,depthmax,
             latb,latu,
             lonl,lonr,
             jd1,jd2,
             limit)

#READ FULL MOONS
full=numpy.loadtxt("util/astronomy-fullmoons-1970_2030.data")

#READ QUAKES
qids,phases=getPhases(search,component,db,dbtable=dbtable)
phs=phases[:,4+phasenum]
cond=phs<=1
phs=phs[cond]
quakes=phases[cond]
nquakes=len(phs)
phases=numpy.array(360*phs)
logpt,dlogpt=schusterValue(phases*DEG,
                           qbootstrap=qbootstrap,
                           facbootstrap=facbootstrap,
                           bootcycles=nsamples)
print "p-value (phase %s): log(p) = %.2f +/- %.2f"%(phase,logpt,dlogpt)
exit(0)

qids,quakes=getQuakes(search,db,dbtable=dbtable)
nquakes=len(qids)

lat1=center[0]-dlat
lon1=center[1]-dlon

lats=quakes[:,1]
lons=quakes[:,2]
deps=quakes[:,3]

xs=(lats-lat1)*DEG*REARTH
ys=(lons-lon1)*DEG*REARTH
zs=-deps
Ms=quakes[:,4]

# ############################################################
# PREPARE PLOTTING REGION
# ############################################################
from mpl_toolkits.mplot3d import Axes3D
fig=plt.figure(figsize=(8,12))
ax1=fig.add_subplot(211, projection='3d')
ax2=fig.add_subplot(212, projection='3d')

# ############################################################
# FITTING
# ############################################################
import scipy.linalg
X,Y=numpy.meshgrid(numpy.linspace(xs.min(),xs.max(),5),
                   numpy.linspace(ys.min(),ys.max(),5))
XX=X.flatten()
YY=Y.flatten()

# best-fit linear plane
A=numpy.c_[xs,ys,numpy.ones(len(xs))]
C,_,_,_=scipy.linalg.lstsq(A,zs)    # coefficients

# evaluate it on grid
Z=C[0]*X+C[1]*Y+C[2]

# ############################################################
# PLOT
# ############################################################
def plotPlane(ax,normal,values,d,color='r',alpha=0.5):
    x,y=numpy.meshgrid(values,values)
    z=(-normal[0]*x-normal[1]*y-d)*1./normal[2]
    ax.plot_surface(x,y,z,color=color,alpha=alpha)

values=numpy.linspace(xs.min(),xs.max(),5)
#ax.plot(xs,ys,zs,'ko',ms=1)
deep=numpy.abs(zs)>=70.0
surf=numpy.abs(zs)<70.0
for ax in ax1,ax2:
    plotPlane(ax,[0.0,0.0,1.0],values,0.0,color='g')
    ax.plot_surface(X,Y,Z,alpha=0.5,color='r',rstride=1,cstride=1)
    #ax.scatter(xs,ys,zs,s=10*numpy.log10(Ms),c=zs,cmap="brg")

    #Deep quakes
    ax.scatter(xs[deep],ys[deep],zs[deep],c='b',s=2)
    ax.scatter(xs[surf],ys[surf],zs[surf],c='k',s=2)

ax1.view_init(10,20)
ax2.view_init(10,90)

# ############################################################
# DECORATION
# ############################################################
for ax in ax1,ax2:
    ax.set_xlabel("Lat.")
    ax.set_ylabel("Long.")
    ax.set_zlabel("Depth (km)")
    xmin,xmax=ax.get_xlim()
    ymin,ymax=ax.get_xlim()
    ax.set_xticks(numpy.linspace(xmin,xmax,5))
    ax.set_yticks(numpy.linspace(ymin,ymax,5))
    ax.set_xticklabels([])
    ax.set_yticklabels([])

fig.subplots_adjust(top=1,left=0,right=1)
# ############################################################
# SAVING FIGURE
# ############################################################
fig.tight_layout()
saveFigure(confile,fig,qwater=False)

