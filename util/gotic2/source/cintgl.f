c$cintgl
c------------------------------------------------------------------
      subroutine cintgl (plat  , plon  , phgt  , azm   , kind  ,
     +                   qlat  , qlon  , wlat  , wlon  , ar0   ,
     +                   hight , phase , cov                    )
c------------------------------------------------------------------
c
      implicit double precision (a-h,o-z)
c
      Logical Lmapout, Lmesh1, Lmesh2, Lmesh3, Lmesh4, Lpoint, Lmascor
      Logical Latan2, Lfirst, Lvryfst, Lminfo, Lverbo, Lpred , Lprein
      Logical Lhavej, Loutj , Lfullm , Lmapln
c
      common /areas/  area1, area2, abnd12, abnd23, abnd34
      common /const/  rearth, earthm, gravct, pi , rad, deg,
     +                dens  , rls1  , rls2  , egv, elp
      common /flag/   Lmapout, Lmesh1, Lmesh2, Lmesh3, Lmesh4, Lpoint,
     +                Lmascor, Latan2, Lverbo, Lpred , Lprein, Lhavej,
     +                Loutj  , Lmapln, Lfullm
      common /gfile/  ang(50), grn(50,6), cgrn(50,2,3), igrn, idelta
      common /nodupl/ Lfirst, Lvryfst, Lminfo
c
      dimension cov(2,6)
c
      if (Lpoint) then
         bang = 0.d0
      else
         bang = 0.523599d0
      endif
c
      chgt = hight*dcos(phase)
      shgt = hight*dsin(phase)
      cazm = dcos(azm)
      sazm = dsin(azm)
c
      do i = 1,6
         do j = 1,2
            cov(j,i) = 0.0d0
         enddo
      enddo
c
      call angld(plat, plon, qlat, qlon, angd)
      if ( (angd.le.area1) .or. (angd.gt.area2) ) return
c
c -----< Radial displacement >-----
c
      if (kind.eq.1) then
c
         call rdispi (plat, plon, qlat, qlon, wlat, wlon, chgt,
     +                crdsp, bang)
         call rdispi (plat, plon, qlat, qlon, wlat, wlon, shgt,
     +                srdsp, bang)
c
         cov(1,1) = crdsp*ar0
         cov(2,1) = srdsp*ar0
c
         return
c
      endif
c
c -----< Tangential displacement >-----
c
      if (kind.eq.2) then
c
         call tdispi (plat, plon, qlat, qlon, wlat, wlon, chgt,
     +                cxdsp, cydsp, bang)
         call tdispi (plat, plon, qlat, qlon, wlat, wlon, shgt,
     +                sxdsp, sydsp, bang)
c
         cov(1,1) = cydsp*ar0
         cov(2,1) = sydsp*ar0
         cov(1,2) = cxdsp*ar0
         cov(2,2) = sxdsp*ar0
         cov(1,3) = cov(1,1)*cazm + cov(1,2)*sazm
         cov(2,3) = cov(2,1)*cazm + cov(2,2)*sazm
c
         return
c
      endif
c
c -----< Gravity >-----
c
      if (kind.eq.3) then
c
         cagrv = 0.d0
         sagrv = 0.d0
         cdgrv = 0.d0
         sdgrv = 0.d0
c
         if (Lfirst) then
c
            call agravi (plat, plon, phgt, qlat, qlon, wlat, wlon,
     +                   chgt, cagrv, bang)
            call agravi (plat, plon, phgt, qlat, qlon, wlat, wlon,
     +                   shgt, sagrv, bang)
c     
         endif
c
         call dgravi (plat, plon, qlat, qlon, wlat, wlon, chgt,
     +                cdgrv, bang)
         call dgravi (plat, plon, qlat, qlon, wlat, wlon, shgt,
     +                sdgrv, bang)
c
         cov(1,2) = cagrv*ar0
         cov(2,2) = sagrv*ar0
         cov(1,3) = cdgrv*ar0
         cov(2,3) = sdgrv*ar0
c     
         cov(1,1) = cov(1,2) + cov(1,3)
         cov(2,1) = cov(2,2) + cov(2,3)
c
         return
c
      endif
c
c -----< Tilt >-----
c
      if (kind.eq.4) then
c
         call atilti (plat, plon, phgt, qlat, qlon, wlat, wlon, chgt,
     +                catltx, catlty, bang)
         call atilti (plat, plon, phgt, qlat, qlon, wlat, wlon, shgt,
     +                satltx, satlty, bang)
         call dtilti (plat, plon, qlat, qlon, wlat, wlon, chgt, cdtltx,
     +                cdtlty, bang)
         call dtilti (plat, plon, qlat, qlon, wlat, wlon, shgt, sdtltx,
     +                sdtlty, bang)
c
         cov(1,1) = (catlty + cdtlty)*ar0
         cov(2,1) = (satlty + sdtlty)*ar0
         cov(1,2) = (catltx + cdtltx)*ar0
         cov(2,2) = (satltx + sdtltx)*ar0
         cov(1,3) = cov(1,1)*cazm + cov(1,2)*sazm
         cov(2,3) = cov(2,1)*cazm + cov(2,2)*sazm
         cov(1,4) = (catltx*sazm + catlty*cazm)*ar0
         cov(2,4) = (satltx*sazm + satlty*cazm)*ar0
         cov(1,5) = cov(1,3) - cov(1,4)
         cov(2,5) = cov(2,3) - cov(2,4)
c
         return
c
      endif
c
c -----< Strain >-----
c
      if (kind.eq.5) then
c
         call strani (plat, plon, qlat, qlon, wlat, wlon, chgt,
     +                cstnxx, cstnyy, cstnxy, bang)
         call strani (plat, plon, qlat, qlon, wlat, wlon, shgt,
     +                sstnxx, sstnyy, sstnxy, bang)
c
         cov(1,1) = cstnyy*ar0
         cov(2,1) = sstnyy*ar0
         cov(1,2) = cstnxx*ar0
         cov(2,2) = sstnxx*ar0
         cov(1,3) = cstnxy*ar0
         cov(2,3) = sstnxy*ar0
c
         ccazm    = cazm*cazm
         ssazm    = sazm*sazm
         csazm    = cazm*sazm*2.0d0
c
         cov(1,4) = cov(1,1)*ccazm + cov(1,2)*ssazm + cov(1,3)*csazm
         cov(2,4) = cov(2,1)*ccazm + cov(2,2)*ssazm + cov(2,3)*csazm
         cov(1,5) = cov(1,1) + cov(1,2)
         cov(2,5) = cov(2,1) + cov(2,2)
c
c ### RLS=L/(L+2*G), L AND G ARE LAME'S CONST. AND RIGIDITY AT THE SURFACE.
c
         if (igrn .eq. 1) then
            rls = rls1
         else if (igrn .eq. 2)  then
            rls = rls2
         endif
c
         cov(1,6) = (1.0d0 - rls)*cov(1,5)
         cov(2,6) = (1.0d0 - rls)*cov(2,5)
c
         return
c
      endif
c
c -----< Vertical deflection >-----
c
      if (kind.eq.6) then
c
         call atilti (plat, plon, phgt, qlat, qlon, wlat, wlon, chgt,
     +                catltx, catlty, bang)
         call atilti (plat, plon, phgt, qlat, qlon, wlat, wlon, shgt,
     +                satltx, satlty, bang)
         call dverti (plat, plon, qlat, qlon, wlat, wlon, chgt,
     +                svertx, sverty, bang)
         call dverti (plat, plon, qlat, qlon, wlat, wlon, shgt,
     +                cvertx, cverty, bang)
c
         cov(1,1) = (catlty + cverty)*ar0
         cov(2,1) = (satlty + sverty)*ar0
         cov(1,2) = (catltx + cvertx)*ar0
         cov(2,2) = (satltx + svertx)*ar0
         cov(1,3) = cov(1,1)*cazm + cov(1,2)*sazm
         cov(2,3) = cov(2,1)*cazm + cov(2,2)*sazm
         cov(1,4) = (catltx*sazm + catlty*cazm)*ar0
         cov(2,4) = (satltx*sazm + satlty*cazm)*ar0
         cov(1,5) = cov(1,3) - cov(1,4)
         cov(2,5) = cov(2,3) - cov(2,4)
c
         return
c
      endif
c
      stop '!!! Error in cintgl : Wrong kind ID!'
c
      end
c
