c$tdispi
c------------------------------------------------------------------
      subroutine tdispi (plat  , plon  , qlat  , qlon  , wlat  ,
     +                   wlon  ,hload  , tdispx, tdispy, bang   )
c------------------------------------------------------------------
c
      implicit double precision (a-h, o-z)
c
      common /const/  rearth, earthm, gravct, pi , rad, deg,
     +                dens  , rls1  , rls2  , egv, elp
c
      dimension ang4(4), hlat(2), hlon(2), x(2), y(2)
c
      call angld(plat, plon, qlat, qlon, angq)
      call azmth(plat, plon, qlat, qlon, angq, azmt)
c
      if (angq.le.bang) then
c
         hlat(2) = wlat*0.5d0
         hlat(1) = -hlat(2)
         hlon(2) = wlon*0.5d0
         hlon(1) = -hlon(2)
         k       = 0
c
         do i = 1,2
            do j = 1,2
               k    = k + 1
               rlat = qlat + hlat(j)
               rlon = qlon + hlon(i)
               call angld (plat, plon, rlat, rlon, angl)
               ang4(k) = angl
            enddo
         enddo
c
         call greenf (ang4, grna, grnb, grnc, 2)
c
         clat = dcos(qlat)
         cang = dcos(azmt)*angq
         sang = dsin(azmt)*angq
c
         do i = 1,2
            x(i) = rearth*(hlon(i)*clat - sang)
            y(i) = rearth*(hlat(i)      - cang)
         enddo
c
         tdispx = 0.0d0
         tdispy = 0.0d0
         rr     = rearth*rearth
         grnb   = grnb/(2.0d0*rearth)
         grnc   = grnc/(2.0d0*rr)
         am     = dens*hload
c
         do i = 1,2
            do j = 1,2
c
               xx     = x(i)*x(i)
               yy     = y(j)*y(j)
               xxyy   = dsqrt(xx+yy)
               wlogx  = 0.0d0
               wlogy  = 0.0d0
               watanx = 0.0d0
               watany = 0.0d0
               wlogxy = 0.0d0
c
               if ( (y(j) + xxyy) .gt. 0.d0 ) then
                  wlogy = dlog(y(j) + xxyy)
               endif
c
               if ( (x(i) + xxyy) .gt. 0.d0 ) then
                  wlogx = dlog(x(i) + xxyy)
               endif
c
               if (x(i).ne.0.d0) then
                  watanx = dabs(x(i))*datan2( y(j), dabs(x(i)) )
               endif
c
               if (y(j).ne.0.d0) then
                  watany = dabs(y(j))*datan2( x(i), dabs(y(j)) )
               endif
c
               if ( (xx + yy) .gt. 0.d0) then
                  wlogxy = dlog(xx + yy)
               endif
c
               ij    = i + j
               gintx = grna*(0.5d0*y(j)*wlogxy + watanx)
     +               + grnb*(xx*wlogy + y(j)*xxyy)
     +               + grnc*xx*y(j)
               ginty = grna*(0.5d0*x(i)*wlogxy + watany)
     +               + grnb*(yy*wlogx + x(i)*xxyy)
     +               + grnc*yy*x(i)
c
               if (mod(ij,2).eq.0) then
                  tdispx = tdispx + gintx
                  tdispy = tdispy + ginty
               else
                  tdispx = tdispx - gintx
                  tdispy = tdispy - ginty
               endif
c
            enddo
         enddo
c
         tdispx = tdispx*am*1.0d-12
         tdispy = tdispy*am*1.0d-12
c
      else                      ! Point load
c
         call greenp(angq, grnq, 2)
         tdisp  = wlat*wlon*dcos(qlat)*hload*dens*grnq*rearth
     +          / (angq*1.0d12)
         tdispx = -tdisp*dsin(azmt)
         tdispy = -tdisp*dcos(azmt)
c     
      endif
c
      return
      end
c
