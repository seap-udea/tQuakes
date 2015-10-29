# ############################################################
# IMPORT CONFIGURATION
# ############################################################
from matplotlib import use
use('Agg')
import matplotlib.pyplot as plt
execfile("declustering.conf")

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

# ############################################################
# GET PHASES
# ############################################################
# COLUMNS: 
# 0:qjd,1:qlat,2:qlon,3:qdepth,4:Ml
# Fourier: 5:sd, 6:dn, 7:fn, 8:mn
# Boundaries: 9:sd, 10:fn, 11:mn
qids,quakes=getPhases(component,db,criteria=criteria)
nquakes=quakes.shape[0]
print "Criterium: ",criteria
print "Number of quakes: ",nquakes

# ############################################################
# CLUSTERING ALGORITHM
# ############################################################
# GENERATE EARTHQUAKE LIST IN RAESENBERG FORMAT
fc=open("catalogue.dat","w")
for iq in xrange(nquakes):
    dt=jd2date(quakes[iq,0])
    # year, month, day, hour, minute, lat, lon, depth, mag
    fc.write("%-5d%-4d%-4d%-4d%-4d%-10.3f%-10.3f%-10.3f%-10.2f\n"%(dt.year,dt.month,dt.day,dt.hour,dt.minute,
                                                                   quakes[iq,1],abs(quakes[iq,2]),quakes[iq,3],quakes[iq,4]))
fc.close()

