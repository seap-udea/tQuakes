# ############################################################
# IMPORT TOOLS
# ############################################################
from tquakes import *
from matplotlib import use
use('Agg')
import matplotlib.pyplot as plt
confile=prepareScript()
conf=execfile(confile)

# ############################################################
# CONNECT TO DATABASE
# ############################################################
connection=connectDatabase()
db=connection.cursor()

# ############################################################
# GET DATA FROM DATABASE
# ############################################################
#cluster="BucaramangaNest"
#cluster="PucallpaCluster"
#cluster="PuyoCluster"
cluster="CaucaCluster"

sql="select qjd,sigman,sigmas from Quakes where sigman is not NULL and qclass='%s'"%cluster # and quakeid='00NZUT3'"
results=mysqlArray(sql,db)
nquakes=len(results)
print("Number of selected earthquakes: ",len(results))

sigmans=[]
sigmass=[]
tcfs=[]
table1=[]
table2=[]
for i,quake in enumerate(results):
    sigmanAll=[float(sigma) for sigma in quake[1].strip(";").split(";")]
    sigmasAll=[float(sigma) for sigma in quake[2].strip(";").split(";")]

    sigmans+=[OrderedDict()]
    sigmass+=[OrderedDict()]
    tcfs+=[OrderedDict()]
    values1=[i+1,float(quake[0])]
    values2=[i+1+nquakes,float(quake[0])]
    for j,comb in enumerate(TCFS_COMBINATIONS.keys()):
        mu=float(comb.split(".")[-1].split("=")[-1].replace("_","."))
        sigmans[i][comb]=sigmanAll[j]
        sigmass[i][comb]=sigmasAll[j]
        tcfs[i][comb]=sigmass[i][comb]+mu*sigmans[i][comb]
        print(quake[0],j,comb,sigmans[i][comb],sigmass[i][comb],tcfs[i][comb])
        if "MAIN" in comb:
            values1+=[tcfs[i][comb]]
        if "MAIN" in comb:
            values2+=[tcfs[i][comb]]
    table1+=[values1]
    table2+=[values2]

table=numpy.vstack((numpy.array(table1),numpy.array(table2)))
numpy.savetxt("%s.txt"%cluster,table)
nquakes=i+1
exit(0)

# ############################################################
# ENSAMBLE TCFS ARRAYS
# ############################################################
tcfsArray=[]

mu=0.4
mustr=str(mu).replace(".","_")

time="QUAKE"
#time="MAX"

hcombs=['P=MAIN.T=%s.V=RD.MU=%s'%(time,mustr),'P=AUX.T=%s.V=RD.MU=%s'%(time,mustr)]
for hcomb in hcombs:
    for i in range(nquakes):
        tcfsArray+=[tcfs[i][hcomb]]
print "Number of data points: ",len(tcfsArray)

# ############################################################
# STATISTICS
# ############################################################
tcfsArray=numpy.array(tcfsArray)
mean=tcfsArray.mean()
std=tcfsArray.std()
kur=kurtosis(tcfsArray)
skew=skew(tcfsArray)

print "Statistics:"
print "\tMean estimate = %.2lf"%mean
print "\tDispersion estimate = %.2lf"%std
print "\tKurtosis estimate = %.2lf"%kur
print "\tSkewness estimate = %.2lf"%skew

# ############################################################
# HISTOGRAM
# ############################################################

# ############################################################
# PREPARE PLOTTING REGION
# ############################################################
fig,axs=subPlots(plt,[1])

axs[0].hist(tcfsArray,bins=8)

# ############################################################
# SAVING FIGURE
# ############################################################
saveFigure(confile,fig)
