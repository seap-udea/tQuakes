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
