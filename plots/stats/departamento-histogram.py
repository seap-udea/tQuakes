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
departamentos=mysqlArray("select departamento from Quakes;",db)
departamentos=[depto[0] for depto in departamentos]
nquakes=len(departamentos)
depset=sorted(list(set(departamentos)))
ndeps=len(depset)
depconv=dict()
i=0
for key in depset:
    depconv[key]=i
    i+=1
depnum=[]
for departamento in departamentos:
    depnum+=[depconv[departamento]]

ax.hist(depnum,ndeps-1,facecolor='blue')

# ############################################################
# DECORATION
# ############################################################
xts=numpy.arange(0,ndeps)
xls=[]
for x in xts:
    xls+=[depset[x][:5].upper()]

ax.set_xticks(xts)
ax.set_xticklabels(xls,rotation=90,
                   horizontalalignment='left',
                   fontsize=8)
ax.set_yscale("log",nonposy="clip")

ax.set_xlim((0,ndeps))
ax.set_title("Histogram of Departamentos for %d earthquakes"%nquakes)
ax.set_ylabel("Number of earthquakes")
ax.grid()

# ############################################################
# SAVE FIGURE
# ############################################################
figname="plots/stats/%s.png"%basename
print "Saving figure ",figname
fig.savefig(figname)
