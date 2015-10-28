"""
        minphase=0.50
        maxphase=0.52

        minphase=0.98
        maxphase=1.00

        sql="select SUBSTRING_INDEX(SUBSTRING_INDEX(qphases,';',%d),';',-1),qlat,qlon,qjd from Quakes where SUBSTRING_INDEX(SUBSTRING_INDEX(qphases,';',%d),';',-1)+0>%f and SUBSTRING_INDEX(SUBSTRING_INDEX(qphases,';',%d),';',-1)+0<%f and Ml+0>0 and Ml+0<2 and qdepth+0<20 and qlon+0>-79 and qlon+0<-77 and qlat+0>0.5 and qlat+0<1"%(npos,npos,minphase,npos,maxphase)
        
        sql="select SUBSTRING_INDEX(SUBSTRING_INDEX(qphases,';',%d),';',-1),qlat,qlon,qjd from Quakes where SUBSTRING_INDEX(SUBSTRING_INDEX(qphases,';',%d),';',-1)+0>%f and SUBSTRING_INDEX(SUBSTRING_INDEX(qphases,';',%d),';',-1)+0<%f and Ml+0>0 and Ml+0<5 and qdepth+0<20 and qlon+0>-72.5 and qlon+0<-71 and qlat+0>8.0 and qlat+0<10"%(npos,npos,minphase,npos,maxphase)

for comp in hs tilt vs vd ocean;do sed -e "s/\"grav\"/\"$comp\"/" times-statistics-grav.py > times-statistics-$comp.py;done

"""
