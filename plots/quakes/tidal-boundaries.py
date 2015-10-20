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
# GET SIGNAL VALUE
qsignal=quake.qsignal.split(";")
value=float(qsignal[1])

# READ SIGNAL
signal=numpy.loadtxt(DIRNAME+"/%s.data"%quakeid)
t=signal[:,0]-float(quake.qjd)
s=signal[:,2]

# PLOT SIGNAL
ax.plot(t,s,'k-',alpha=0.2)
ax.axvline(0,color='r')
ax.plot([0],[value],marker='o',color='r',markersize=10,markeredgecolor="None")

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# SIGNAL BOUNDARIES
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
from scipy import signal

# ==============================
# SEMI-DIURNAL LEVEL
# ==============================
tmb,smb,tMb,sMb=signalBoundary(t,s)
dtmean=(tMb[1:]-tMb[:-1]).mean()
dt=tMb[tMb<0][-1]
dtphase=-dt/dtmean;
print "Semidiurnal (%e): dt = %e, dtphase = %e"%(dtmean,dt,dtphase)

ax.plot(tmb,smb,'ko-',label="P = %.1f, phase = %.2f"%(dtmean,dtphase))
ax.plot(tMb,sMb,'ko-')

# ==============================
# BIWEEKLY LEVEL
# ==============================
# SMOOTH
b,a=signal.butter(8,0.125)
sMs=signal.filtfilt(b,a,sMb,padlen=100)
ax.plot(tMb,sMs,'b-')

# MAXIMA
tm,sm,tM,sM=signalBoundary(tMb,sMs)
dtmean=(tM[1:]-tM[:-1]).mean()
dt=tM[tM<0][-1]
dtphase=-dt/dtmean;
print "Biweekly (%e): dt = %e, dtphase = %e"%(dtmean,dt,dtphase)
ax.plot(tM,sM,'cs-',label="P = %.1f, phase = %.2f"%(dtmean,dtphase))

# ==============================
# MONTHLY LEVEL
# ==============================
# SMOOTH
b,a=signal.butter(8,0.125)
sms=signal.filtfilt(b,a,smb,padlen=100)
ax.plot(tmb,sms,'b-')

# MINIMUMS
tm,sm,tM,sM=signalBoundary(tmb,sms)
dtmean=(tm[1:]-tm[:-1]).mean()
dt=tm[tm<0][-1]
dtphase=-dt/dtmean;
print "Biweekly with minimums (%e): dt = %e, dtphase = %e"%(dtmean,dt,dtphase)
ax.plot(tm,sm,'cs-')

# MINIMUMS(S)
tm,sm,tM,sM=signalBoundary(tm,sm)
dtmean=(tm[1:]-tm[:-1]).mean()
dt=tm[tm<0][-1]
dtphase=-dt/dtmean;
print "Monthly (%e): dt = %e, dtphase = %e"%(dtmean,dt,dtphase)

ax.plot(tm,sm,'gv-',label="P = %.1f, phase = %.2f"%(dtmean,dtphase))

# ############################################################
# DECORATION
# ############################################################
ax.set_xlim((-60,+60))

ax.set_title(r"Horizontal strain boundaries for quake %s"%quakeid)
ax.set_xlabel(r"Days to/since earthquake")
ax.set_ylabel(r"Horizontal strain ($\times10^{-9}$)")
ax.legend(loc='upper right',prop=dict(size=8))
ax.grid()

# ############################################################
# SAVE FIGURE
# ############################################################
figname="%s/%s.png"%(DIRNAME,BASENAME)
print "Saving figure ",figname
fig.savefig(figname)
