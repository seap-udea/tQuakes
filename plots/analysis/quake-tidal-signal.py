# ############################################################
# IMPORT TOOLS
# ############################################################
from tquakes import *
from matplotlib import use
use('Agg')
import matplotlib.pyplot as plt
confile=prepareScript()
conf=execfile(confile)
quake=loadConf("quake.conf")

# ############################################################
# CONNECT TO DATABASE
# ############################################################
connection=connectDatabase()
db=connection.cursor()

# ############################################################
# PLOT SIGNAL
# ############################################################
def plotSignal(quakeid,component,plt):
    # ############################################################
    # COMPONENT
    # ############################################################
    info=COMPONENTS_DICT[component]
    compnum=info[0]
    name=info[1]
    units=info[2]
    nc,np=numComponent(component)
    
    # ############################################################
    # QUAKE PROPERTIES
    # ############################################################
    quake=loadConf(DIRNAME+"/quake.conf")
    quakestr="QUAKE-lat_%+.2f-lon_%+.2f-dep_%+.2f-JD_%.5f"%\
        (float(quake.qlat),
         float(quake.qlon),
         float(quake.qdepth),
         float(quake.qjd))

    # ############################################################
    # PREPARE FIGURE
    # ############################################################
    fig=plt.figure()
    ax=plt.gca()

    # ############################################################
    # CREATE FIGURE
    # ############################################################
    qsignal=quake.qsignal.split(";")
    value=float(qsignal[nc-1])

    signal=numpy.loadtxt(DIRNAME+"/%s.data"%quakeid)
    t=signal[:,0]-float(quake.qjd)
    s=signal[:,nc]
    smin=s.min();smax=s.max()
    
    ax.plot(t,s)
    ax.plot([0],[value],marker='o',color='r',markersize=10,markeredgecolor="None")
    ax.axvline(0,color='r')

    # ############################################################
    # DECORATION
    # ############################################################
    ax.set_xlim((-CONF.TIMEWIDTH,+CONF.TIMEWIDTH))
    ax.set_ylim((smin,smax+(smax-smin)/2))

    ax.set_title(r"%s for quake %s"%(name,quakeid))
    ax.set_xlabel(r"Days to/since earthquake")
    ax.set_ylabel(r"%s (%s)"%(name,units))

    # ############################################################
    # INSET PANEL
    # ############################################################
    axi=fig.add_axes([0.172,0.65,0.68,0.22])
    axi.plot(t,s)
    axi.plot([0],[value],marker='o',color='r',markersize=10,markeredgecolor="None")
    axi.axvline(0,color='r')
    axi.set_xlim((-10,10))
    axi.text(0.1,0.93,r"%s = %.1f %s"%(component.upper(),value,units),transform=ax.transAxes,fontsize=8)
    axi.set_yticklabels([])

    # ############################################################
    # SAVE FIGURE
    # ############################################################
    ax.text(1.02,0.5,quakestr,
            horizontalalignment='center',verticalalignment='center',
            rotation=90,fontsize=10,color='k',alpha=0.2,
            transform=ax.transAxes)

    figname="%s/%s.png"%(DIRNAME,BASENAME)
    print "Saving figure ",figname
    fig.savefig(figname)
    return fig

# ############################################################
# PLOT
# ############################################################
fig=plotSignal(quake.quakeid,component,plt)

# ############################################################
# SAVING FIGURE
# ############################################################
saveFigure(confile,fig)