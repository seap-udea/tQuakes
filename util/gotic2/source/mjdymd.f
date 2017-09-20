c$mjdymd
c---------------------------------------------------------------------
      subroutine mjdymd(xmjd, iymd, ihms, iflag)
c---------------------------------------------------------------------
c
c xmjd  : modified julian date
c iymd  : year, month, day
c ihms  : hour, minute, second
c iflag : 1 -> YMDHMS to MJD
c         2 -> MJD to YMDHMS
c Date must be within the years Mar. 1, 1900 to Feb. 28, 2100
c
      implicit double precision (a-h,o-z)
c
      parameter ( xjd0 = 2400000.5d0 )
      parameter ( half =       0.5d0 )
c
c -----< YMDHMS to MJD >-----
c
      if (iflag.eq.1) then
c
         iy   = iymd/10000
         im   = (iymd - iy*10000)/100
         id   = iymd - iy*10000 - im*100
         ih   = ihms/10000
         imin = (ihms - ih*10000)/100
         isec = ihms - ih*10000 - imin*100
c
         y = dfloat(iy - 1)
c
         if (im.gt.2) then
            m = im
            y = y + 1
         else
            m = im + 12
         endif
c
         xjd  = int(365.25d0*y) + int(30.6001d0*(m+1)) - 15
     +        + 1720996.5d0     + id
         xmjd = xjd - xjd0
c
         fsec = dfloat(ih)*3600.d0 + dfloat(imin)*60.d0 + dfloat(isec)
c
         xmjd = xmjd + fsec/86400.d0
c
c -----< MJD to YMDHMS >-----
c
      else if (iflag.eq.2) then
c
         mjd  = xmjd
         xjd  = dfloat(mjd) + xjd0
         c    = int(xjd + half) + 1537
         nd   = int((c - 122.1d0)/365.25d0 )
         e    = int(365.25d0*nd)
         nf   = int((c - e)/30.6001d0)
c     
         ifr  = int(xjd + half)
         frc  = xjd + half - dfloat(ifr) 
         id   = c - e - int(30.6001d0*nf) + frc
         im   = nf - 1 - 12*int(nf/14)
         iy   = nd - 4715 - int((7+im)/10)
c
         iymd = iy*10000 +im*100 + id
c
         sec  = (xmjd-dfloat(mjd))*86400.d0
         isec = sec
         if ((sec-isec).gt.0.5d0) isec = isec + 1
         ih   = isec/3600
         im   = (isec - ih*3600)/60
         is   = isec - ih*3600 - im*60
         ihms = ih*10000 + im*100 + is
c
      else
c
         print*,'!!! Error in <mjdymd>. iflag should be 1 or 2.'
         stop
c
      endif
c
      return
      end
c
