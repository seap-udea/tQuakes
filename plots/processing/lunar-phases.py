# ############################################################
# IMPORT TOOLS
# ############################################################
from tquakes import *
from matplotlib import use
use('Agg')
import matplotlib.pyplot as plt
import spiceypy as sp

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
# SPICE RELATED ROUTINES
# ############################################################
# Ephemeris time: et=sp.str2et("01/01/2015 00:00:00.000 UTC")
etini=sp.str2et("01/01/%s 00:00:00.000 UTC"%yini)
jdini=et2jd(etini)
etend=sp.str2et("01/01/%s 00:00:00.000 UTC"%yend)
print "Number of days:",(etend-etini)/DAY
#det=1.0*DAY
det=1*HOUR

et=etini
news=[]
fulls=[]
amoon_old=0
asun_old=0
delmoon=0
delsun=0
da_new_old=0
da_full_old=0
while True:

    # JULIAN DAY
    jd=et2jd(et)

    # STATE VECTOR MOON AND SUN
    Rmoon,amoon,dmoon=bodyPosition("MOON",et)
    Rsun,asun,dsun=bodyPosition("SUN",et)
    amoon*=RAD
    asun*=RAD

    if amoon-amoon_old<0:delmoon+=360
    amoonc=amoon+delmoon
    amoon_old=amoon

    if asun-asun_old<0:delsun+=360
    asunc=asun+delsun
    asun_old=asun

    # DIFFERENCE   
    da=numpy.mod(amoonc-asunc,360.0)
    if da-da_new_old<0:
        print("Nueva:",sp.et2utc(et,"C",0),amoonc,asunc,da)
        news+=[jd]
    elif (da-180.0)*(da_full_old-180)<0:
        print("Llena:",sp.et2utc(et,"C",0),amoonc,asunc,da)
        fulls+=[jd]
    da_new_old=da
    da_full_old=da

    if et>etend:break
    et+=det

news=numpy.array(news)
fulls=numpy.array(fulls)
numpy.savetxt("astronomy-fullmoons-%s_%s.data"%(yini,yend),fulls)
numpy.savetxt("astronomy-newmoons-%s_%s.data"%(yini,yend),news)
