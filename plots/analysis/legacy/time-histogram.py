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
qjd=mysqlArray("select qjd from Quakes;",db)
qjd=numpy.array([float(jd[0]) for jd in qjd])-MJD_0
nquakes=len(qjd)

ax.hist(qjd,nquakes/2000,facecolor='blue')

# ############################################################
# DECORATION
# ############################################################
xts=ax.get_xticks()
xls=[]
for x in xts:
    gcal=jd2gcal(MJD_0,x)
    xls+=["%d-%s-%s"%(gcal[0],gcal[1],gcal[2])]
ax.set_xticklabels(xls,rotation=30,horizontalalignment='right',fontsize=10)

ax.set_title("Histogram of dates for %d earthquakes"%nquakes)
ax.set_xlabel("Time (MJD)")
ax.set_ylabel("Number of earthquakes")
ax.grid()

# ############################################################
# SAVE FIGURE
# ############################################################
figname="%s/%s.png"%(DIRNAME,BASENAME)
print "Saving figure ",figname
fig.savefig(figname)
