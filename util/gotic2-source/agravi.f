c$agravi
c------------------------------------------------------------------
      subroutine agravi (plat  , plon  , phgt  , qlat  , qlon  ,
     +                   wlat  , wlon  , hload , agrav , bang   )
c------------------------------------------------------------------
c
      implicit double precision (a-h, o-z)
c
      common /const/  rearth, earthm, gravct, pi , rad, deg,
     +                dens  , rls1  , rls2  , egv, elp
c
      dimension x(2), y(2), z(2)
c
      call angld (plat, plon, qlat, qlon, angq)
c
      rp = rearth + phgt
c
      if (angq.le.bang) then
c
         cltp = dcos(plat)
         sltp = dsin(plat)
         rpc  = rp*cltp
         rps  = rp*sltp
         cltq = dcos(qlat)
         sltq = dsin(qlat)
         clon = dcos(qlon - plon)
         slon = dsin(qlon - plon)
         xp   = -rpc*slon
         yp   = -rpc*sltq*clon+rps*cltq
         zp   =  rpc*cltq*clon+rps*sltq
         re05 = rearth*0.5d0
         x(2) = re05*wlon*cltq
         x(1) = -x(2)
         y(2) = re05*wlat
         y(1) = -y(2)
         z(1) = rearth
         z(2) = z(1)+hload
c     
         do i = 1,2
            x(i) = x(i) - xp
            y(i) = y(i) - yp
            z(i) = z(i) - zp
         enddo
c
         agrvx = 0.0d0
         agrvy = 0.0d0
         agrvz = 0.0d0
c
         do i = 1,2
            do j = 1,2
               do k = 1,2
c
                  xyz   = dsqrt(x(i)*x(i) + y(j)*y(j) + z(k)*z(k))
                  wlogx = 0.0d0
                  wlogy = 0.0d0
                  wlogz = 0.0d0
                  watnx = 0.0d0
                  watny = 0.0d0
                  watnz = 0.0d0
c
                  if ( (xyz + x(i)).gt.0.d0) then
                     wlogx = dlog(xyz + x(i))
                  endif
c
                  if ( (xyz + y(j)).gt.0.d0) then
                     wlogy = dlog(xyz + y(j))
                  endif
c
                  if ( (xyz + z(k)).gt.0.d0) then
                     wlogz = dlog(xyz + z(k))
                  endif
c
                  if (x(i).ne.0.d0) then
                     watnx = 2.0d0*dabs(x(i))
     +                     * datan2( (xyz + y(j) + z(k)), dabs(x(i)) )
                  endif
c
                  if (y(j).ne.0.d0) then
                     watny = 2.0d0*dabs(y(j))
     +                     * datan2( (xyz + z(k) + x(i)), dabs(y(j)) )
                  endif
c
                  if (z(k).ne.0.d0) then
                     watnz = 2.0d0*dabs(z(k))
     +                     * datan2( (xyz + x(i) + y(j)), dabs(z(k)) )
                  endif
c
                  ijk   = i + j + k
                  gintx = y(j)*wlogz + z(k)*wlogy + watnx
                  ginty = z(k)*wlogx + x(i)*wlogz + watny
                  gintz = x(i)*wlogy + y(j)*wlogx + watnz
c
                  if (mod(ijk,2).eq.0) then
                     agrvx = agrvx + gintx
                     agrvy = agrvy + ginty
                     agrvz = agrvz + gintz
                  else
                     agrvx = agrvx - gintx
                     agrvy = agrvy - ginty
                     agrvz = agrvz - gintz
                  endif
c
               enddo
            enddo
         enddo
c
         agrav = gravct*dens*(agrvx*cltp*slon
     +         - agrvy*(cltq*sltp-sltq*cltp*clon)
     +         - agrvz*(sltq*sltp+cltq*cltp*clon))
c
      else
c
         rr    = rearth*rearth
         cang  = dcos(angq)
         wpq   = rr + rp*(rp - 2.0d0*rearth*cang)
         pq    = dsqrt(wpq)
         agrav = -gravct*dens*hload*rr*wlat*wlon*dcos(qlat)
     +         * (rp - rearth*cang)/(wpq*pq)
c
      endif                     ! Point load or not
c
      return
      end
c
