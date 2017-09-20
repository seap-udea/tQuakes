c$dtilti
c------------------------------------------------------------------
      subroutine dtilti (plat  , plon  , qlat  , qlon  , wlat  ,
     +                   wlon  , hload , dtiltx, dtilty, bang   )
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
         call greenf (ang4, grna, grnb, grnc, 4)
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
         dtiltx = 0.0d0
         dtilty = 0.0d0
         rr     = rearth*rearth
         grnb   = grnb/rearth
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
               if ( (y(j) + xxyy) .gt. 0.d0) then
                  wlogy = dlog(y(j) + xxyy)
               endif
c
               if ( (x(i) + xxyy) .gt. 0.d0) then
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
               if ( (xx+yy).gt.0.d0 ) then
                  wlogxy = dlog(xx + yy)
               endif
c
               ij = i + j
c
               gintx = (grna - grnc*xx)*wlogy
     +               - grnb*(y(j)*wlogxy*0.5d0 + watanx)
     +               - grnc*y(j)*xxyy
               ginty = (grna - grnc*yy)*wlogx
     +               - grnb*(x(i)*wlogxy*0.5d0 + watany)
     +               - grnc*x(i)*xxyy
c
               if (mod(ij,2).eq.0) then
                  dtiltx = dtiltx + gintx
                  dtilty = dtilty + ginty
               else
                  dtiltx = dtiltx - gintx
                  dtilty = dtilty - ginty
               endif
c
            enddo
         enddo
c     
         dtiltx = -dtiltx*am*1.0d-12
         dtilty = -dtilty*am*1.0d-12
c
      else                      ! Point load.
c
         call greenp(angq, grnq, 4)
c
         dtilt  = wlat*wlon*dcos(qlat)*hload*dens*grnq
     +          / (angq*angq*1.0d12)
         dtiltx = -dtilt*dsin(azmt)
         dtilty = -dtilt*dcos(azmt)
c
      endif
c
      return
      end
c
