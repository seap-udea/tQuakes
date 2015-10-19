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
Ml=mysqlArray("select Ml from Quakes;",db)
Ml=numpy.array([float(M[0]) for M in Ml])
nquakes=len(Ml)

# CUMULATIVE DITRIBUTION
h,bins=numpy.histogram(Ml,nquakes/1000)
Q=numpy.cumsum(h[::-1])[::-1]
Ms=(bins[:-1]+bins[1:])/2
Qp=Q[::2];Msp=Ms[::2]
ax.plot(Msp,Qp,'r-',linewidth=5)

# FIT
cond=(Msp>3)*(Msp<6)
Mf=Msp[cond]
Qf=Qp[cond]
b,a=numpy.polyfit(Mf,numpy.log10(Qf),1)

# GUTENBERG-RICHTER LAW
Mt=numpy.linspace(Ml.min(),Ml.max(),100)
ax.plot(Mt,10**(a+b*Mt),'b--',
        linewidth=3,
        label="Gutenberg-Richter law, b = %.2lf, a = %.2lf"%(b,a))

# ############################################################
# DECORATION
# ############################################################
ax.set_yscale("log",nonposy="clip")
ax.set_ylim((0,nquakes))
ax.set_title("Cumulative ditribution of %d earthquakes"%nquakes)
ax.set_xlabel("$M_l$")
ax.set_ylabel("$N (M > M_l)$")
ax.text(0.05,0.90,"Roll-off",
        horizontalalignment="left",
        transform=ax.transAxes,
        fontsize=18)
ax.grid()
ax.legend(loc="lower left")

# ############################################################
# SAVE FIGURE
# ############################################################
figname="plots/stats/%s.png"%basename
print "Saving figure ",figname
fig.savefig(figname)
