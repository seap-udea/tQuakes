# ############################################################
# IMPORT
# ############################################################
from matplotlib import use
use('Agg')
import matplotlib.pyplot as plt
from tquakes import *

# ############################################################
# READ CLUSTERS
# ############################################################
fc=open("cluster.clu","r")
i=1
clusters=dict()
for line in fc:
    line=line.strip("\r\n")
    props=line.split()

    # BASIC PROPERTIES
    qdatetime=datetime.datetime.strptime(props[0]+props[1],"%y%m%d%H%M")
    qjd=date2jd(qdatetime)
    qlat=s2d(int(props[2]),float(props[3]),0)
    qlon=s2d(int(props[4]),float(props[5]),0)
    qdep=float(props[6])
    Ml=float(props[7])
    cluster=props[-1]

    """
    print "Quake ",i
    print "\tDate: ",qdatetime
    print "\tJD: ",qjd
    print "\tLat: ",qlat
    print "\tLon: ",qlon
    print "\tDepth: ",qdep
    print "\tMl: ",Ml
    print "\tCluster: ",cluster
    """

    icluster="%05d"%int(cluster)
    qprops=numpy.array([qjd,qlat,qlon,qdep,Ml])
    if icluster not in clusters.keys():
        clusters[icluster]=qprops
    else:
        clusters[icluster]=numpy.vstack((clusters[icluster],qprops))
    i+=1

iclusters=sorted(clusters.keys())

# ############################################################
# MAP
# ############################################################

fig=plt.figure(figsize=(8,8))
ax=fig.gca()

m=None

#iclusters=['00032']
for ic in iclusters:
    nq=len(clusters[ic][:,0])
    print "Plotting cluster '%s' with %d earthquakes..."%(ic,nq)
    m=scatterMap(ax,clusters[ic][:,1],clusters[ic][:,2],
                 m=m,
                 zoom=50,
                 color='k',marker='o',linestyle='None',
                 markersize=1,markeredgecolor='None',alpha=1)
    qlatmean=clusters[ic][:,1].mean()
    qlonmean=clusters[ic][:,2].mean()
    x,y=m(qlonmean,qlatmean)
    ax.text(x,y,"%s"%ic,fontsize=6)

# ############################################################
# SAVE FIGURE
# ############################################################
figname="%s/%s_map.png"%(DIRNAME,BASENAME)
print "Saving figure ",figname
fig.savefig(figname)

# ############################################################
# MAP
# ############################################################
fig=plt.figure(figsize=(8,8))
ax=fig.gca()

for ic in iclusters:
    ax.plot(clusters[ic][:,0],clusters[ic][:,4],'o')

# ############################################################
# SAVE FIGURE
# ############################################################
figname="%s/%s.png"%(DIRNAME,BASENAME)
print "Saving figure ",figname
fig.savefig(figname)
