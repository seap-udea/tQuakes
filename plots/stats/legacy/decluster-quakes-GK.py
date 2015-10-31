# ############################################################
# IMPORT TOOLS
# ############################################################
from tquakes import *
from matplotlib import use
use('Agg')
import matplotlib.pyplot as plt
execfile("%s.conf"%BASENAME)

# ############################################################
# CONNECT TO DATABASE
# ############################################################
connection=connectDatabase()
db=connection.cursor()

# ############################################################
# READ CLUSTER DATABASE
# ############################################################
search="where Ml+0>3 order by Ml+0 desc,qjd+0 asc"
qids,quakes=getQuakes(search,db)
nquakes=len(qids)
print "Declustering %d earthquakes..."%nquakes

# ############################################################
# CREATE CLUSTER FOR EACH EARTHQUAKE
# ############################################################
print quakes.shape
for iq in xrange(nquakes):
    if iq%1000==0:
        print "Getting aftershocks for quake %d, '%s'..."%(iq+1,qids[iq])
    # GET QUAKE PROPERTIES
    Ml=quakes[iq,4]
    qlat=quakes[iq,1]
    qlon=quakes[iq,2]
    qjd=quakes[iq,0]

    # GET WINDOWS
    tw,dw=tdWindow(Ml,fit="GK74")

    # GET EARTHQUAKES IN TIME WINDOW
    times=quakes[:,0]-qjd
    condt=(numpy.abs(times)<=tw)*(numpy.abs(times)>0)
    times=times[condt]
    ntime=len(times)
    qs=quakes[condt,:]

    # GET DISTANCES OF QUAKES TO PRESENT QUAKE
    # d=distancePoints(6.0,-75.0,0.0,-75.0)
    ds=numpy.array([distancePoints(qlat,qlon,qlati,qloni) for qlati,qloni in zip(qs[:,1],qs[:,2])])
    condd=(ds<=dw)
    qs=qs[condd,:]

    # AFTERSHOCKS
    nshocks=qs.shape[0]
    
    """
    print "\tEarth quakes in time window : %d"%(ntime)
    print "\tProperties: Ml = %.1f, qlat = %.3f, qlon = %.3f"%(Ml,qlat,qlon)
    print "\tAftershocks window: time = %.2f days, distance = %.2f km"%(tw,dw)
    print "\tNumber of foreshocks and aftershocks for this earthquake: %d"%nshocks
    # """
