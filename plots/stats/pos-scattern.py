from scatter import *

# ############################################################
# READ DATA
# ############################################################
qpos=mysqlArray("select qlat,qlon from Quakes;",db)
qlat=numpy.array([float(pos[0]) for pos in qpos])
qlon=numpy.array([float(pos[1]) for pos in qpos])
nquakes=len(qlon)

# ############################################################
# PREPARE FIGURE
# ############################################################
fig=plt.figure(figsize=(8,8))
ax=fig.add_axes([0.05,0.05,0.90,0.85])

# ############################################################
# CREATE MAP
# ############################################################
m=scatterMap(ax,qlat,qlon,
             color='k',marker='o',linestyle='None',
             markersize=1,markeredgecolor='None',alpha=1)

# ############################################################
# DECORATION
# ############################################################
ax.set_title("Scatter plot of %d Earthquakes"%nquakes,position=(0.5,1.05))

# ############################################################
# SAVE FIGURE
# ############################################################
figname="%s/%s.png"%(DIRNAME,BASENAME)
print "Saving figure ",figname
fig.savefig(figname)
