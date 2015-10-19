from tquakes import *
from matplotlib import use
use('Agg')
import matplotlib.pyplot as plt
basename=fileBase(argv[0])

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
qlat=mysqlArray("select qlat from Quakes where astatus+0=4;",db)
qlat=numpy.array([float(lat[0]) for lat in qlat])
qlon=mysqlArray("select qlon from Quakes where astatus+0=4;",db)
qlon=numpy.array([float(lon[0]) for lon in qlon])
nquakes=len(qlon)

ax.plot(qlon,qlat,'or',markersize=1,markeredgecolor='None')

# ############################################################
# DECORATION
# ############################################################
ax.set_xlim((-85,-70))
ax.set_ylim((-10,15))

ax.set_title("Scatter plot of %d Earthquakes"%nquakes)
ax.set_xlabel("Longitude (degrees)")
ax.set_ylabel("Latitude (degrees)")
ax.grid()

# ############################################################
# SAVE FIGURE
# ############################################################
figname="plots/stats/%s.png"%basename
print "Saving figure ",figname
fig.savefig(figname)
