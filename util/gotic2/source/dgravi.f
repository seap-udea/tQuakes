c$dgravi
c------------------------------------------------------------------
      subroutine dgravi (plat  , plon  , qlat  , qlon  , wlat  ,
     +                   wlon  , hload , dgrav , bang           )
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
c
      if (angq.le.bang)  then
c
         hlat(2) = wlat*0.5d0
         hlat(1) = -hlat(2)
         hlon(2) = wlon*0.5d0
         hlon(1) = -hlon(2)
         k       = 0
c
         do i = 1,2
            do j = 1,2
               k = k + 1
               rlat = qlat + hlat(j)
               rlon = qlon + hlon(i)
               call angld (plat, plon, rlat, rlon, angl)
               ang4(k) = angl
            enddo
         enddo
c
         call greenf (ang4, grna, grnb, grnc, 3)
         call azmth (qlat, qlon, plat, plon, angq, azmt)
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
         dgrav = 0.0d0
         rr    = rearth*rearth
         grnb  = grnb/rearth
         grnc  = grnc/(6.0d0*rr)
c
         do i = 1,2
            do j = 1,2
c
               xx    = x(i)*x(i)
               yy    = y(j)*y(j)
               xy    = x(i)*y(j)
               xxyy  = dsqrt(xx + yy)
               wlogx = 0.0d0
               wlogy = 0.0d0
c
               if ( (y(j) + xxyy) .gt. 0.d0 ) then
                  wlogy = dlog(y(j) + xxyy)
               endif
c
               if ( (x(i) + xxyy) .gt. 0.d0 ) then
                  wlogx = dlog(x(i) + xxyy)
               endif
c
               ij = i + j
c
               gint = x(i)*(grna + grnc*xx)*wlogy
     +              + y(j)*(grna + grnc*yy)*wlogx
     +              + grnb*xy
     +              + grnc*xy*xxyy*2.0d0
c
               if (mod(ij,2).eq.0) then
                  dgrav = dgrav + gint
               else
                  dgrav = dgrav - gint
               endif
c
            enddo
         enddo
c
         dgrav = dgrav*dens*hload*1.0d-18
c
      else                      ! point load
c
         call greenp (angq, grnq, 3)
c
         dgrav = rearth*wlat*wlon*dcos(qlat)*hload*dens*grnq
     +         / (angq*1.0d18)
c
      endif
c
      return
      end
c