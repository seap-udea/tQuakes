# ############################################################
# IMPORT TOOLS
# ############################################################
from tquakes import *
from matplotlib import use
use('Agg')
import matplotlib.pyplot as plt
import spiceypy as sp

"""-

Usage:

   python astronomy-cycles.py <year ini.> <year end.>

Example:

   python astronomy-cycles.py 1970 2000

Return:
  
   Calculate the distance to the Sun, to the Moon and the average
   tidal potential each hour between initial and final year.

   It returns 2 files: 

      astronomy-cycles-1970_2000.data:

        Table with the following columns: jd, normalized Rmoon,
        normalized Rsun, tidal V.

      astronomy-extremes-1970_2000.data:

        Table with the following columns: jd, normalized Rmoon or
        Rsun.

        First column is "0 0".  There are 5 subtables all starting
        with a line "<num> 9.999990000e+08".  This subtables contain
        the information on 5 extremes: 1-apogea, 2-perigea, 3-maximum
        apogea, 4-minimum perigea, 5-aphelia, 6-perihelia.
"""


# ############################################################
# PARAMETERS
# ############################################################
yini=int(argv[1])
yend=int(argv[2])

# ############################################################
# SPICE INITIALIZATION
# ############################################################
sp.furnsh("util/kernels/kernels.mk")

# ############################################################
# CONSTANTS
# ############################################################
# EARTH SURFACE GRAVITY
g=9.8 # m/s^2

# DOODSON CONSTANTS (Hendershott, Lecture on Tides)
Dmoon=0.2675*g # m/s^2
Dsun=0.4605*Dmoon # m/s^2

# MEAN ORBITAL DISTANCE
Rmoon=3.84399e5 # m
Rsun=1.49598023e8 # m

# ######################################################################
# SPICE RELATED ROUTINES
# ######################################################################
# Ephemeris time: et=sp.str2et("01/01/2015 00:00:00.000 UTC")
etini=sp.str2et("01/01/%s 00:00:00.000 UTC"%yini)
jdini=et2jd(etini)
etend=sp.str2et("01/01/%s 00:00:00.000 UTC"%yend)
print "Number of days:",(etend-etini)/DAY
det=1.0*DAY/6
det=1*HOUR

astronomy=[]
et=etini
while True:
    # STATE VECTOR MOON AND SUN
    rmoon=sp.spkezr("MOON",et,"J2000","NONE","399")
    rsun=sp.spkezr("SUN",et,"J2000","NONE","399")
    Rm,vm=normX(rmoon)
    Rs,vs=normX(rsun)
    V=Dmoon*(Rmoon/Rm)**3+Dsun*(Rsun/Rs)**3
    # JULIAN DAY
    jd=et2jd(et)
    astronomy+=[[jd,Rm/Rmoon,Rs/Rsun,V]]
    if et>etend:break
    et+=det

astronomy=numpy.array(astronomy)
numpy.savetxt("astronomy-cycles-%s_%s.data"%(yini,yend),astronomy)

jds=astronomy[:,0]
Rms=astronomy[:,1]
Rss=astronomy[:,2]
Vs=astronomy[:,3]

# ############################################################
# PREPARE MAXIMA AND MINIMA
# ############################################################

# LEVEL 1
jdmb,Rmmb,jdMb,RmMb=signalBoundary(jds,Rms)

# SMOOTH
b,a=signal.butter(8,0.525)
sMs=signal.filtfilt(b,a,RmMb,padlen=100)
jdMs=jdMb
sms=signal.filtfilt(b,a,Rmmb,padlen=100)
jdms=jdmb

# LEVEL 2
jdm2,Rmm2,jdM2,RmM2=signalBoundary(jdMs,sMs)
jdm3,Rmm3,jdM3,RmM3=signalBoundary(jdms,sms)

# SUN
jdsmb,Rsmb,jdsMb,RsMb=signalBoundary(jds,Rss)

# ############################################################
# SAVE MAXIMA
# ############################################################
"""
Components are: 
   1 - Apogea, 2 - Perigea
   3 - Max.Apogee, 4 - Min.Perigee
   5 - Aphelia, 6 - Perihelia
"""
table=numpy.array([0,0])

# 1 - Apogea
line=numpy.array([1,999999999])
subtable=numpy.column_stack((jdMb,RmMb))
stable=numpy.vstack((line,subtable))
table=numpy.vstack((table,stable))

# 2 - Perigea
line=numpy.array([2,999999999])
subtable=numpy.column_stack((jdmb,Rmmb))
stable=numpy.vstack((line,subtable))
table=numpy.vstack((table,stable))

# 3 - Max apogea
line=numpy.array([3,999999999])
subtable=numpy.column_stack((jdM2,RmM2))
stable=numpy.vstack((line,subtable))
table=numpy.vstack((table,stable))

# 4 - Min apogea
line=numpy.array([4,999999999])
subtable=numpy.column_stack((jdm3,Rmm3))
stable=numpy.vstack((line,subtable))
table=numpy.vstack((table,stable))

# 5 - Aphelia
line=numpy.array([5,999999999])
subtable=numpy.column_stack((jdsMb,RsMb))
stable=numpy.vstack((line,subtable))
table=numpy.vstack((table,stable))

# 6 - Perihelia
line=numpy.array([6,999999999])
subtable=numpy.column_stack((jdsmb,Rsmb))
stable=numpy.vstack((line,subtable))
table=numpy.vstack((table,stable))

numpy.savetxt("astronomy-extremes-%s_%s.data"%(yini,yend),table,fmt="%.17e")

# ############################################################
# PLOT OF VARIATIONS
# ############################################################
fig,axs=subPlots(plt,[1,1,1],dh=0)

i=-1

# AVERAGE TIDAL POTENTIAL
i+=1
axs[i].plot((jds-jdini)/ONE,astronomy[:,3])
axs[i].set_ylabel("Average tidal potential")

# &&&&&&&&&&&&&&&&&&&&&&&&&&&&&
# MOON DISTANCE
# &&&&&&&&&&&&&&&&&&&&&&&&&&&&&
i+=1
axs[i].plot((jds-jdini)/ONE,Rms,'k+-')

# PEAKS
axs[i].plot((jdmb-jdini)/ONE,Rmmb,'rs')
axs[i].plot((jdMb-jdini)/ONE,RmMb,'rs')

# SMOOTHED
axs[i].plot((jdms-jdini)/ONE,sms,'b-')
axs[i].plot((jdMs-jdini)/ONE,sMs,'b-')

# MAXIMA
axs[i].plot((jdM2-jdini)/ONE,RmM2,'g^',markersize=10)
axs[i].plot((jdm3-jdini)/ONE,Rmm3,'cv',markersize=10)

axs[i].set_ylabel("Normalized lunar distance")

# &&&&&&&&&&&&&&&&&&&&&&&&&&&&&
# SOLAR DISTANCE
# &&&&&&&&&&&&&&&&&&&&&&&&&&&&&
i+=1
axs[i].plot((jds-jdini)/ONE,astronomy[:,2])

# PEAKS
axs[i].plot((jdsmb-jdini)/ONE,Rsmb,'rs')
axs[i].plot((jdsMb-jdini)/ONE,RsMb,'cs')

axs[i].set_ylabel("Normalized solar distance")

# ############################################################
# COMMON DECORATION
# ############################################################
dmax=30

i=0
for ax in axs:
    ax.grid()
    ax.axvline(0.0,color='r')
    ax.set_xlim((0,dmax))
    if i>0:
        ax.set_xticklabels([])
        yt=ax.get_yticks()
        ax.set_yticks(yt[1:])
    i+=1

# ############################################################
# SAVING FIGURE
# ############################################################
fig.savefig("astronomy-cycles-%s_%s.png"%(yini,yend))

