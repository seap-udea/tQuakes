from tquakes import *
from matplotlib import use
use('Agg')
import matplotlib.pyplot as plt
quakeid=DIRNAME.split("/")[-1]

# ############################################################
# CONNECT TO DATABASE
# ############################################################
connection=connectDatabase()
db=connection.cursor()
quake=quakeProperties(quakeid,db)

# ############################################################
# PREPARE FIGURE
# ############################################################
fig=plt.figure()
ax=plt.gca()

# ############################################################
# CREATE FIGURE
# ############################################################
qphases=quake.qsignal.split(";")

t,ft=loadComplextxt(DIRNAME+"/%s-fft.data"%quakeid)
signal=numpy.loadtxt(DIRNAME+"/%s.data"%quakeid)
t=signal[:,0]-signal[0,0]
s=signal[:,2]
dt=float(quake.qjd)-signal[0,0]
T=t[-1]
N=len(t)
smean=s.mean()
smax=numpy.abs(s-smean).max()

# SIGNAL
ax.plot(t-dt,s)
ax.axvline(0,color='r')

# THEORETICAL SIGNAL
P=13.8
w=2*PI/P
k=omega2k(w,T,N)
st=numpy.array([signal_teo(tval,ft,T,N,k) for tval in t])
stmean=st.mean()
stmax=numpy.abs(st-stmean).max()
ax.plot(t-dt,(st-stmean)*smax/stmax+smean,'k--',
        label='Quincenal',alpha=0.7,zorder=-10)

P=27.6
w=2*PI/P
k=omega2k(w,T,N)
st=numpy.array([signal_teo(tval,ft,T,N,k) for tval in t])
stmean=st.mean()
stmax=numpy.abs(st-stmean).max()
ax.plot(t-dt,(st-stmean)*smax/stmax+smean,'k:',
        label='Monthly',alpha=0.9,zorder=-10)

# ############################################################
# DECORATION
# ############################################################
window=30
ax.set_xlim((-window,+window))

ax.set_title(r"Horizontal strain for quake %s"%quakeid)
ax.set_xlabel(r"Days to/since earthquake")
ax.set_ylabel(r"Horizontal strain ($\times10^{-9}$)")

ax.legend(loc='lower right')

# ############################################################
# SAVE FIGURE
# ############################################################
figname="%s/%s.png"%(DIRNAME,BASENAME)
print "Saving figure ",figname
fig.savefig(figname)
