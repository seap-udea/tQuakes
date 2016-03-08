# lons=xe[:-1]
# lats=ye[:-1]

# H=numpy.rot90(H)
# H=numpy.flipud(H)

"""

lats=numpy.arange(latb,latu+dt,dt);nlats=len(lats)
lons=numpy.arange(lonl,lonr+dl,dl);nlons=len(lons)
# CALCULATE FIELD
field=numpy.zeros((nlons,nlats))
for i in xrange(nlons):
    for j in xrange(nlats):
        field[i,j]=lats[j]*lons[i]
"""

from scipy.optimize import leastsq

def function(x,params):
    y=params[0]*x**2+params[1]
    return y

def chisq(params,xdata,ydata,dydata):
    return (ydata-function(xdata,params))/dydata

x=numpy.array([0.0,1.0,2.0,3.0,4.0,5.0,6.0])
y=numpy.array([0.0,1.1,2.2,2.8,4.3,5.1,5.8])
dy=numpy.array([0.1,0.1,0.1,0.1,0.1,0.1,0.1])

pars0=[0.0,0.0]
pars,n=leastsq(chisq,pars0,args=(x,y,dy))

fig=plt.figure()
plt.plot(x,y,'ko')
plt.plot(x,function(x,pars),'b-')
fig.savefig("fit.png")

