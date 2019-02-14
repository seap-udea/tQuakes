c$lpout2
c------------------------------------------------------------------
      subroutine lpout2(istat, nwave, kind)
c------------------------------------------------------------------
c
      implicit double precision (a-h,o-z)
c
      common /amphs/  amps(5,6,6,10,21), phsg(5,6,6,10,21),
     +                phsl(5,6,6,10,21),
     +                ampa(5,10,21), phsa(5,10,21),
     +                ampe(5,10,21), phse(5,10,21),
     +                ampst(6,6,10,21), ampot(6,6,10,21),
     +                ampt (6,6,10,21), phsea(6,6,10,21),
     +                phsoa(6,6,10,21), phsta(6,6,10,21),
     +                phser(6,6,10,21), phsor(6,6,10,21),
     +                phstr(6,6,10,21)
      common /comp/   ncomp(6)
      common /const/  rearth, earthm, gravct, pi , rad, deg,
     +                dens  , rls1  , rls2  , egv, elp
      common /stat99/ slat(10,3), slon(10,3),
     +                altd(10), azmth(10), slt(10), sln(10)
      common /wavei/  ncnt(21), isp(21)
      common /waver/  xlambda(21)
      common /wavec/  wn(21)
c
      character*3 wn
      character lcomp*8
c
      dimension lcomp(6,6)
c
      data lcomp / '        ','        ','        ',
     +             '        ','        ','        ',
     +             'N-S     ','E-W     ','Azimuth ',
     +             '        ','        ','        ',
     +             'Total   ','N-part  ','E-part  ',
     +             '        ','        ','        ',
     +             'N-S     ','E-W     ','Azimuth ',
     +             'N-part  ','E-part  ','        ',
     +             'N-S     ','E-W     ','Shear   ',
     +             'Azimuth ','Areal   ','Cubic   ',
     +             'N-S     ','E-W     ','Azimuth ',
     +             'N-part  ','E-part  ','        ' /
c
      write(6,6001)
 6001 format('               ')
      write(6,6002)
 6002 format(' **************************************',
     +       '*******************')
      write(6,6003)
 6003 format(' **  Theoretical Earth tide and oceanic',
     +       ' tidal effects   **')
      write(6,6002)
      write(6,6001)
c
      ncmp = ncomp(kind)
      is   = istat
      k    = kind
c
      write(6,609)
  609 format(18x,'Solid Earth tide',16x,'Oceanic tidal effect',
     +       21x,'Total')
      write(6,610)
  610 format(5x,3(7x,'Amplitude  A-phase  R-phase')/)
c
      do nc = 1,ncmp
c
         write(6,607) lcomp(nc,kind)
 607     format(1x,a8)
c
         do  iw = 1,nwave
c
            write(6,602) wn(ncnt(iw)) ,
     +         ampst(k,nc,is,iw), phsea(k,nc,is,iw), phser(k,nc,is,iw),
     +         ampot(k,nc,is,iw), phsoa(k,nc,is,iw), phsor(k,nc,is,iw),
     +         ampt (k,nc,is,iw), phsta(k,nc,is,iw), phstr(k,nc,is,iw)
 602        format(1x,a3,1x,3(3x,1pe13.4,2(0pf9.3)))
c
         enddo                  ! iw
c
         write(6,6001)
c
      enddo                     ! nc
c
      return
      end
c


