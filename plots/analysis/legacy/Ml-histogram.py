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
Ml=mysqlArray("select Ml from Quakes;",db)
Ml=[float(M[0]) for M in Ml]
nquakes=len(Ml)

ax.hist(Ml,nquakes/1000,facecolor='blue')


# ############################################################
# DECORATION
# ############################################################
ax.set_title("Histogram of $M_l$ for %d earthquakes"%nquakes)
ax.set_xlabel("$M_l$")
ax.set_ylabel("Number of earthquakes")

# ############################################################
# SAVE FIGURE
# ############################################################
figname="%s/%s.png"%(DIRNAME,BASENAME)
print "Saving figure ",figname
fig.savefig(figname)
