c$tjulid
c------------------------------------------------------------
      double precision function tjulid( iy, im, id, ih, mi, is )
c------------------------------------------------------------
c
c     CALCULATION OF JULIAN DATE
c
      implicit double precision (a-h,o-z)
c
      dimension days(12)
c
      data   days /   0.d0,  31.d0,  59.d0,  90.d0, 120.d0, 151.d0,
     +              181.d0, 212.d0, 243.d0, 273.d0, 304.d0, 334.d0 /
c
      iyy = mod( iy, 1900 )
      if ( iyy.le.0 .or. iyy.ge.200 )  then
         write(*,*)  'ERROR AT FUNCTION TJULID        IY =', iy
         stop
      end if
c
      tjulid =   dble( iyy*365 + id + iyy/4 ) + days(im)
     +         + dble(ih)/24.d0 + dble(mi)/1440.d0 + dble(is)/86400.d0
     +         + 2415019.5d0
c
      if ( (mod(iyy,4).eq.0) .and. (im.le.2) )  tjulid = tjulid - 1.d0
c
      return
      end
c
