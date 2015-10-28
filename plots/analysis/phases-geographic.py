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

    dh=0.01
    h=(1-2*b-(npanels-1)*dh)/npanels

    axs=[]
    for i in xrange(npanels):
        axs+=[fig.add_axes([l,b,w,h])]
        b+=h+dh

    fig2=plt.figure(figsize=(8,6))
    ax2=fig2.gca()

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
    for phase in 5,6,7:
        ax=axs[i]

        # ############################################################
        # PERFORM QUERY
        # ############################################################
        # and quakeid='UTFZQRX'
        npos=np+phase
        minphase=0.0
        maxphase=1.0
        """
        minphase=0.50
        maxphase=0.52

        minphase=0.98
        maxphase=1.00

        sql="select SUBSTRING_INDEX(SUBSTRING_INDEX(qphases,';',%d),';',-1),qlat,qlon,qjd from Quakes where SUBSTRING_INDEX(SUBSTRING_INDEX(qphases,';',%d),';',-1)+0>%f and SUBSTRING_INDEX(SUBSTRING_INDEX(qphases,';',%d),';',-1)+0<%f and Ml+0>0 and Ml+0<2 and qdepth+0<20 and qlon+0>-79 and qlon+0<-77 and qlat+0>0.5 and qlat+0<1"%(npos,npos,minphase,npos,maxphase)
        
        sql="select SUBSTRING_INDEX(SUBSTRING_INDEX(qphases,';',%d),';',-1),qlat,qlon,qjd from Quakes where SUBSTRING_INDEX(SUBSTRING_INDEX(qphases,';',%d),';',-1)+0>%f and SUBSTRING_INDEX(SUBSTRING_INDEX(qphases,';',%d),';',-1)+0<%f and Ml+0>0 and Ml+0<5 and qdepth+0<20 and qlon+0>-72.5 and qlon+0<-71 and qlat+0>8.0 and qlat+0<10"%(npos,npos,minphase,npos,maxphase)
        """

        sql="select SUBSTRING_INDEX(SUBSTRING_INDEX(SUBSTRING_INDEX(SUBSTRING_INDEX(qphases,';',%d),';',-1),':',2),':',-1)+0,qlat,qlon,qjd from Quakes where qphases<>'' and SUBSTRING_INDEX(SUBSTRING_INDEX(SUBSTRING_INDEX(SUBSTRING_INDEX(qphases,';',%d),';',-1),':',2),':',-1)+0>=%f and SUBSTRING_INDEX(SUBSTRING_INDEX(SUBSTRING_INDEX(SUBSTRING_INDEX(qphases,';',%d),';',-1),':',2),':',-1)+0<=%f"%(npos,npos,minphase,npos,maxphase)

        results=mysqlArray(sql,db)
        phases=[]
        qlats=[]
        qlons=[]
        qjds=[]
        for ph in results:
            phases+=[float(ph[0])]
            qlats+=[float(ph[1])]
            qlons+=[float(ph[2])]
            qjds+=[float(ph[3])]

        phases=numpy.array(phases)
        qlats=numpy.array(qlats)
        qlons=numpy.array(qlons)
        qjds=numpy.array(qjds)
        nphases=len(qlats)

        # ############################################################
        # SCATTER PLOT
        # ############################################################
        merdict=dict(labels=[False,False,False,False])
        if i==0:
            merdict["labels"][3]=True
        elif i==npanels-1:
            merdict["labels"][2]=True

        m=scatterMap(ax,qlats,qlons,
                     merdict=merdict,
                     color='k',marker='o',linestyle='None',
                     markersize=1,markeredgecolor='None',alpha=1)


        ax2.plot(qjds-qjds[0],qlats,'ko')

        ax.text(0.5,0.05,"%s"%phasename[i],
                horizontalalignment='center',fontsize=20,
                transform=ax.transAxes)

        i+=1

    # ############################################################
    # DECORATION
    # ############################################################
    ax2.set_xlim((-1,1))
    # ax.set_xlim((0,360))
    # axs[0].set_xlabel("Phase")
    # axs[-1].set_title("%s: phase distribution of %d quakes"%(name,nphases))

    # ############################################################
    # SAVE FIGURE
    # ############################################################
    figname="%s/%s.png"%(DIRNAME,BASENAME)
    print "Saving figure ",figname
    fig.savefig(figname)
    fig2.savefig("times.png")

plot("vd")
