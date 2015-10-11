from tquakespice import *

et=str2et("01/01/2015 00:00:00.000 UTC")
state_moon,ltime=spkezr("MOON",et,"J2000","NONE","EARTH")
state_sun,ltime=spkezr("SUN",et,"J2000","NONE","EARTH")

print mag(state_moon)
