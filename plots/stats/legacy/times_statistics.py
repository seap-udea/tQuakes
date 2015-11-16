from tquakes import *
from matplotlib import use
use('Agg')
import matplotlib.pyplot as plt

def plot(component):
    # ############################################################
    # CONNECT TO DATABASE
    # ############################################################
    connection=connectDatabase()
    db=connection.cursor()

    # ############################################################
    # PREPARE FIGURE
    # ############################################################
    npanels=3
    l=0.1
    b=0.1/npanels
    w=0.8

    fig=plt.figure(figsize=(8,6*npanels))

    dh=0.02
    h=(1-2*b-(npanels-1)*dh)/npanels

    axs=[]
    for i in xrange(npanels):
        axs+=[fig.add_axes([l,b,w,h])]
        b+=h+dh

    # ############################################################
    # PHASE TO ANALYSE
    # ############################################################
    info=COMPONENTS_DICT[component]
    compnum=info[0]
    name=info[1]
    nc,np=numComponent(component)

    # Phases:
    #   Fourier: 1-Semidiurnal, 2-Diurnal, 3-Fortnightly, 4-Monthly
    #   Boundary: 5-Semidiurnal, 6-Fortnightly, 7-Monthly
    i=0
    phasename=["Semidiurnal","Fortnightly","Monthly"]
    phtimes=[0.5,15.0,30.0]
    for phase in 5,6,7:
        ax=axs[i]

        # ############################################################
        # PERFORM QUERY
        # ############################################################
        # and quakeid='UTFZQRX'
        sql="select SUBSTRING_INDEX(SUBSTRING_INDEX(qphases,';',%d),';',-1) from Quakes where qphases<>''"%(np+phase)
        results=mysqlArray(sql,db)
        phases=[]
        for ph in results:
            phtime=ph[0].split(":")
            phases+=[float(phtime[0])]
        phases=numpy.array(phases)
        nphases=len(phases)
        nbins=50

        # ############################################################
        # PLOT HISTOGRAM
        # ############################################################
        h,bins=numpy.histogram(phases,nbins)
        xs=(bins[:-1]+bins[1:])/2
        dh=numpy.sqrt(h)

        ax.hist(phases,nbins,facecolor='blue',alpha=0.2)
        ax.errorbar(xs,h,yerr=dh,linestyle='None',color='r')

        ax.set_xlim((0,1))
        ax.set_ylabel("Number of Earthquakes")

        ax.text(0.5,0.05,"%s"%phasename[i],
                horizontalalignment='center',fontsize=20,
                transform=ax.transAxes)

        ax.set_xlim((0,phtimes[i]))

        if i>0:
            # ax.set_xticklabels([])
            ax.set_yticks(ax.get_yticks()[1:])
        i+=1

    # ############################################################
    # DECORATION
    # ############################################################
    axs[0].set_xlabel("Time (days)")
    axs[-1].set_title("%s: time distribution of %d quakes"%(name,nphases))

    # ############################################################
    # SAVE FIGURE
    # ############################################################
    figname="%s/%s.png"%(DIRNAME,BASENAME)
    print "Saving figure ",figname
    fig.savefig(figname)