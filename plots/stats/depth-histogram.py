from tquakes import *
from matplotlib import use
use('Agg')
import matplotlib.pyplot as plt

# ############################################################
# CONNECT TO DATABASE
# ############################################################
connection=connectDatabase()
db=connection.cursor()

# ############################################################
# PREPARE FIGURE
# ############################################################
fig=plt.figure()
ax=plt.gca()

# ############################################################
# CREATE FIGURE
# ############################################################
d=mysqlArray("select qdepth from Quakes;",db)
d=[float(D[0]) for D in d]
nquakes=len(d)

ax.hist(d,nquakes/2000,facecolor='blue')
ax.set_xlim((0,180))

# ############################################################
# DECORATION
# ############################################################
ax.set_yscale("log",nonposy="clip")
ax.set_title("Histogram of Depth (km) for %d earthquakes"%nquakes)
ax.set_xlabel("Depth (km)")
ax.set_ylabel("Number of earthquakes")

# ############################################################
# SAVE FIGURE
# ############################################################
figname="%s/%s.png"%(DIRNAME,BASENAME)
print "Saving figure ",figname
fig.savefig(figname)
