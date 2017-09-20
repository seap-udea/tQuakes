c$strani
c------------------------------------------------------------------
      subroutine strani (plat  , plon  , qlat  , qlon  , wlat  ,
     +                   wlon  , hload , strnxx, strnyy, strnxy,
     +                   bang                                   )
c------------------------------------------------------------------
c
      implicit double precision (a-h, o-z)
c
      common /const/  rearth, earthm, gravct, pi , rad, deg,
     +                dens  , rls1  , rls2  , egv, elp
c
      dimension ang4(4), hlat(2), hlon(2), x(2), y(2)
c
      call angld (plat, plon, qlat, qlon, angq)
      call azmth (plat, plon, qlat, qlon, angq, azmt)
c
      if ( (angq - bang).le.0.d0) then
c
         hlat(2) = wlat*0.5d0
         hlat(1) = -hlat(2)
         hlon(2) = wlon*0.5d0
         hlon(1) = -hlon(2)
c
         k = 0
c
         do i = 1,2
            do j = 1,2
c
               k = k + 1
               rlat = qlat + hlat(j)
               rlon = qlon + hlon(i)
               call angld (plat, plon, rlat, rlon, angl)
               ang4(k) = angl
c
            enddo
         enddo
c
         call greenf (ang4, grna, grnb, grnc, 1)
         call greenf (ang4, grnd, grne, grnf, 2)
c
         clat = dcos(qlat)
         cang = dcos(azmt)*angq
         sang = dsin(azmt)*angq
c
         do i = 1,2
            x(i) = rearth*(hlon(i)*clat - sang)
            y(i) = rearth*(hlat(i) - cang)
         enddo
c
         strnxx = 0.0d0
         strnyy = 0.0d0
         strnxy = 0.0d0
c
         rr    = rearth*rearth
         grna  = grna/rearth
         grnb  = grnb/rr
         grnc  = grnc/(6.0d0*rearth*rr)
         grne  = grne/rearth
         grnf  = grnf/rr
         amass = dens*hload*1.0d-12
c
         do i = 1,2
            do j = 1,2
c
               xx     = x(i)*x(i)
               yy     = y(j)*y(j)
               xy     = x(i)*y(j)
               xxyy   = dsqrt(xx+yy)
               wlogx  = 0.0d0
               wlogy  = 0.0d0
               wlogxy = 0.0d0
               watnx  = 0.0d0
               watny  = 0.0d0
c
               if ( (y(j) + xxyy).gt.0.d0 ) then
                  wlogy = dlog(y(j) + xxyy)
               endif
c
               if ( (x(i) + xxyy).gt.0.d0 ) then
                  wlogx = dlog(x(i) + xxyy)
               endif
c
               if (xxyy.gt.0.d0) then
                  wlogxy = dlog(xx + yy)
               endif
c
               if (x(i).ne.0.d0) then
                  watnx = datan2(y(j),x(i))
               endif
c
               if (y(j).ne.0.d0) then
                  watny = datan2(x(i),y(j))
               endif
c
               ij = i + j
c
               gintxx = grnd*watnx
     +                + 0.5d0*grne*x(i)
     +                + (grne + grna + grnc*xx)*x(i)*wlogy
     +                + (grnf + grnb)*xy
     +                + (grna + grnc*yy)*y(j)*wlogx
     +                + 2.0d0*grnc*xy*xxyy
c
               gintyy = grnd*watny
     +                + 0.5d0*grne*y(j)
     +                + (grne + grna + grnc*yy)*y(j)*wlogx
     +                + (grnf + grnb)*xy
     +                + (grna + grnc*xx)*x(i)*wlogy
     +                + 2.0d0*grnc*xy*xxyy
c
               gintxy = grnd*wlogxy
     +                + 2.0d0*grne*xxyy
c
c     +                + 2.0d0*grnf*(xx + yy)*rearth
c
c Thanks to Dr. O. Kamigaichi of JMA.
     +                + 0.5d0*grnf*(xx + yy)
c
               if (mod(ij,2).eq.0) then
                  strnxx = strnxx + gintxx
                  strnyy = strnyy + gintyy
                  strnxy = strnxy + gintxy
               else
                  strnxx = strnxx - gintxx
                  strnyy = strnyy - gintyy
                  strnxy = strnxy - gintxy
               endif
c
            enddo               ! j
         enddo                  ! i
c
         strnxx = strnxx*amass
         strnyy = strnyy*amass
         strnxy = strnxy*amass*0.5d0
c
      else                      ! Point load
c
         call greenp(angq, grns, 5)
         call greenp(angq, grnu, 1)
         call greenp(angq, grnv, 2)
c
         amass  = wlat*wlon*dcos(qlat)*hload*dens
         strnss = amass*grns/(angq*angq*1.0d12)
         strnll = amass*grnu/(angq*1.0d12)
     +          + amass*grnv/(angq*dtan(angq)*1.0d12)
         cazm   = dcos(azmt)
         sazm   = dsin(azmt)
         csazm  = cazm*sazm
         cazm   = cazm*cazm
         sazm   = sazm*sazm
         strnxx = strnss*sazm + strnll*cazm
         strnyy = strnss*cazm + strnll*sazm
         strnxy = (strnss - strnll)*csazm
c
      endif                     ! (angq - bang).le.0.d0
c
      return
      end
c
