# ############################################################
# IMPORT TOOLS
# ############################################################
from tquakes import *
from matplotlib import use
use('Agg')
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from scipy import signal
confile=prepareScript()
conf=execfile(confile)

# ############################################################
# PREPARE PLOTTING REGION
# ############################################################
fig,axs=subPlots(plt,[1,2,1],l=0.15,b=0.15)

# ############################################################
# CONNECT TO DATABASE
# ############################################################
connection=connectDatabase()
db=connection.cursor()

# ############################################################
# GET QUAKES
# ############################################################
limit="10000000"
allqids,allquakes=getQuakes(search+" limit "+limit,db)
nallquakes=len(allqids)
decsearch=search+"and (cluster1='0' or cluster1 like '-%')"
decqids,decquakes=getQuakes(decsearch+" limit "+limit,db)
ndecquakes=len(decqids)

# ############################################################
# CREATING HISTOGRAMS
# ############################################################
# ALL EARTH QUAKES
Ml=allquakes[:,ML]
h,bins=numpy.histogram(Ml,nallquakes/1000)
Q=numpy.cumsum(h[::-1])[::-1]
Ms=(bins[:-1]+bins[1:])/2
Qp=Q[::2];Msp=Ms[::2]
Qpi=interp1d(Msp,Qp)

# ALL EARTH QUAKES
Mld=decquakes[:,ML]
hd,bins=numpy.histogram(Mld,ndecquakes/1000)
Q=numpy.cumsum(hd[::-1])[::-1]
Msd=(bins[:-1]+bins[1:])/2
Qpd=Q[::2];Mspd=Msd[::2]
Qpid=interp1d(Mspd,Qpd)

# ############################################################
# GUTENBERG-RICHTER LAW
# ############################################################
# FIT
Mc=3.0
Mu=5.0

cond=(Msp>Mc)*(Msp<Mu)
Mf=Msp[cond]
Qf=Qp[cond]
b,a=numpy.polyfit(Mf,numpy.log10(Qf),1)

# FIT
cond=(Mspd>Mc)*(Mspd<Mu)
Mf=Mspd[cond]
Qf=Qpd[cond]
bd,ad=numpy.polyfit(Mf,numpy.log10(Qf),1)

# ############################################################
# DISTRIBUTION
# ############################################################
axs[2].plot(Ms[h>0],h[h>0],'k-',linewidth=3)
axs[2].plot(Msd[hd>0],hd[hd>0],'b-',linewidth=3)

# ############################################################
# CUMULATIVE DISTRIBUTION
# ############################################################
axs[1].plot(Msp,Qp,'k-',label='%d earthquakes'%nallquakes,
            linewidth=3)
axs[1].plot(Mspd,Qpd,'b-',label='%d declustered earthquakes'%ndecquakes,
            linewidth=3)

nt=100
Mt=numpy.linspace(Msp.min(),Msp.max(),nt)
axs[1].plot(Mt,10**(a+b*Mt),'k--',
            linewidth=3,
            label="Gutenberg-Richter b = %.3lf"%(-b))

Mtd=numpy.linspace(Mspd.min(),Mspd.max(),nt)
axs[1].plot(Mtd,10**(ad+bd*Mtd),'b--',
            linewidth=3,
            label="Gutenberg-Richter b = %.3lf"%(-bd))

padlen=nt/10

rt=Qpi(Mt)/10**(a+b*Mt)
# axs[0].plot(Mt,rt,'k:',linewidth=2)
b,a=signal.butter(2,0.125)
rts=signal.filtfilt(b,a,rt,padlen=padlen)
axs[0].plot(Mt,rts,'k-',linewidth=3)

rtd=Qpid(Mtd)/10**(ad+bd*Mtd)
# axs[0].plot(Mtd,rtd,'b:',linewidth=2)
b,a=signal.butter(2,0.125)
rtds=signal.filtfilt(b,a,rtd,padlen=padlen)
axs[0].plot(Mtd,rtds,'b-',linewidth=3)

axs[0].axhline(0.9,color='r')

# ############################################################
# DECORATION
# ############################################################
# axs[2].set_title("Earthquakes magnitude distribution")
# axs[2].set_yscale("log",nonposy="clip")

axs[1].set_yscale("log",nonposy="clip")
axs[1].set_ylim((0,1.2*nallquakes))
axs[1].set_xlim((Ml.min(),Ml.max()))
axs[1].legend(loc='lower left')

fs=18

axs[2].set_xticklabels([])
axs[1].set_xticklabels([])
axs[0].set_xlabel("$M_l$",fontsize=fs)

axs[0].set_ylabel(r"$N_{\rm obs}/N_{\rm GR}$",fontsize=fs)
axs[1].set_ylabel(r"$N_{\rm obs}(M>M_l)$, $N_{\rm GR}=N_o 10^{-b M_l}$",fontsize=fs)
axs[2].set_ylabel(r"$dN/dM_l$",fontsize=14)

axs[0].grid()

# ############################################################
# SAVING FIGURE
# ############################################################
saveFigure(confile,fig)

