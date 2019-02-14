c$lpout
c---------------------------------------------------------------------
      subroutine lpout(istat, nwave, kind)
c---------------------------------------------------------------------
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
      common /areas/  area1, area2, abnd12, abnd23, abnd34
      common /comp/   ncomp(6)
      common /const/  rearth, earthm, gravct, pi , rad, deg,
     +                dens  , rls1  , rls2  , egv, elp
      common /gfile/  ang(50), grn(50,6), cgrn(50,2,3), igrn, idelta
      common /name/   sname(10)
      common /stat99/ slat(10,3), slon(10,3),
     +                altd(10), azmth(10), slt(10), sln(10)
      common /wavei/  ncnt(21), isp(21)
      common /waver/  xlambda(21)
      common /wavec/  wn(21)
c
      character*3 wn
      character sname*10, lcomp*8, latsn*8, lonsn*8, ltext*60, lkind*28
      character*80 gname(5)
c
      dimension lkind(6), lcomp(6,6), ltext(2,6,6)
      dimension ntext(6)
      dimension latsn(2), lonsn(2)
c
      data gname(1)/'Guteberg-bullen'/
      data gname(2)/'1066A'/
      data gname(3)/'PREM'/
      data gname(4)/'1066A with Q-model of PREM'/
      data gname(5)/'GB with Q-model of PREM'/
c
      data lkind / '==== Radial displacement ===',
     +             '== Tangential displacement =',
     +             '========= Gravity ==========',
     +             '=========== Tilt ===========',
     +             '========== Strain ==========',
     +             ' Deflection of the vertical '/
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
      data ntext / 1, 4, 2, 4, 6, 3 /
c
      data latsn / 'North   ','South   ' /
     +     lonsn / 'East    ','West    ' /
c
      data ((ltext(j,i,1),j=1,2),i=1,6) /
     +60hAmplitude : Unit in meter, upward positive.   Phase : Unit i,
     +60hn degree, lag positive.                                     ,
     +60h                                                            ,
     +60h                                                            ,
     +60h                                                            ,
     +60h                                                            ,
     +60h                                                            ,
     +60h                                                            ,
     +60h                                                            ,
     +60h                                                            ,
     +60h                                                            ,
     +60h                                                            /
c
      data ((ltext(j,i,2),j=1,2),i=1,6) /
     +60hAmplitude : Unit in meter.     Phase : Unit in degree, lag p,
     +60hositive.                                                    ,
     +60h"N-S" means N-S component tangential displacement (northward,
     +60h positive).                                                 ,
     +60h"E-W" means E-W component tangential displacement (eastward ,
     +60hpositive).                                                  ,
     +60h"Azimuth" means azimuthal component tangential displacement ,
     +60h(azimuthal positive).                                       ,
     +60h                                                            ,
     +60h                                                            ,
     +60h                                                            ,
     +60h                                                            /
c
      data ((ltext(j,i,3),j=1,2),i=1,6) /
     +60hAmplitude : Unit in meter per second square (m/s/s), upward ,
     +60hpositive.     Phase : Unit in degree, lag positive.         ,
     +60h"Total" means sum of newtonian part and elastic part in grav,
     +60hity.                                                        ,
     +60h                                                            ,
     +60h                                                            ,
     +60h                                                            ,
     +60h                                                            ,
     +60h                                                            ,
     +60h                                                            ,
     +60h                                                            ,
     +60h                                                            /
c
      data ((ltext(j,i,4),j=1,2),i=1,6) /
     +60hAmplitude : Unit in radian.     Phase : Unit in degree, lag ,
     +60hpositive.                                                   ,
     +60h"U-S" means U-S component tilt (positive sign indicates upwa,
     +60hrd movement of northern ground).                            ,
     +60h"E-W" menas E-W component tilt (positive sign indicates upwa,
     +60hrd movement of eastern ground).                             ,
     +60h"Azimuth" means azimuthal component tilt (positive sign indi,
     +60hcates upward movement of azimuthal ground).                 ,
     +60h"N-part" means newtonian part in azimuthal component tilt.  ,
     +60h                                                            ,
     +60h"E-part" means elastic part in azimuthal component tilt.    ,
     +60h                                                            /
c
      data ((ltext(j,i,5),j=1,2),i=1,6) /
     +60hAmplitude : Unitless, extension positive.     Phase : Unit i,
     +60hn degree, lag positive.                                     ,
     +60h"N-S" means N-S component principal strain (dv/dy).         ,
     +60h                                                            ,
     +60h"E-W" means E-W component principal strain (du/dx).         ,
     +60h                                                            ,
     +60h"Shear" means shear strain ((du/dy+dv/dx)/2).               ,
     +60h                                                            ,
     +60h"Azimuth" means azimuthal component principal strain.       ,
     +60h                                                            ,
     +60h"Areal" means areal dilatation (du/dx+dv/dy) and "Cubic" mea,
     +60hns cubic dilatation (du/dx+dv/dy+dw/dz).                    /
c
      data ((ltext(j,i,6),j=1,2),i=1,6) /
     +60hAmplitude : Unit in radian.     Phase : Unit in degree, lag ,
     +60hpositive.                                                   ,
     +60h"N-S" means N-S component deflection of the vertical (positi,
     +60hve sign indicates northward movement of upward vector).     ,
     +60h"E-W" means E-W component deflection of the vertical (positi,
     +60hve sign indicates eastward movement of upward vector).      ,
     +60h"Azimuth" means azimuthal component of deflection of the ver,
     +60htical (upward vector azimuthal positive).                   ,
     +60h                                                            ,
     +60h                                                            ,
     +60h                                                            ,
     +60h                                                            /
c
c -----< Header >-----
c
      ilt  = 1
      iln  = 1
      ltd  = slat(istat,1)
      ltm  = slat(istat,2)
      alts = slat(istat,3)
      lnd  = slon(istat,1)
      lnm  = slon(istat,2)
      alns = slon(istat,3)
c
      if (ltd.lt.0.d0) then
         ilt  = 2
         ltd  = -ltd
         ltm  = -ltm
         alts = -alts
      endif
c
      if (lnd.lt.0.d0) then
         iln  = 2
         lnd  = -lnd
         lnm  = -lnm
         alns = -alns
      endif
c
      ncmp = ncomp(kind)
      ntxt = ntext(kind)
      is   = istat
      k    = kind
c
      write(6,6001)
      write(6,6001)
      write(6,599)
      write(6,601) lkind(kind)
      write(6,599)
      write(6,6001)
 599  format(1x,'================================================',
     +          '====================')
 601  format(1x,'====================',a28,'====================')
c
      write(6,600) sname(istat)
 600  format(1x,'Station',7x,a10/)
c
      write(6,603)ltd,ltm,alts,latsn(ilt)
 603  format(1x,'Latitude',6x,i3,'d',i3,'m',f5.1,'s',1x,a8)
c
      write(6,604)lnd,lnm,alns,lonsn(iln)
 604  format(1x,'Longitude',5x,i3,'d',i3,'m',f5.1,'s',1x,a8)
c
      write(6,605)altd(istat)
 605  format(1x,'Altitude',4x,f8.2,' m')
c
      dazm = azmth(istat)*deg
      write(6,606)dazm
 606  format(1x,'Azimuth',6x,f7.2,' degree')
c
      write(6,650) gname(igrn)
 650  format(1x,'Earth model',2x,a80)
c
      radi1 = area1/rad
      radi2 = area2/rad
      write(6,655) radi1,radi2
 655  format(1x,'Range of integration      ',f7.0,' to',f7.0,' deg.')
c
      write(6,6001)
c
      do i = 1,ntxt
         write (6,615) (ltext(j,i,kind),j=1,2)
 615     format(6x,2a60)
      enddo
c
      write(6,612)
 612  format(6x,'"G-phase" means phase with respect to that of ',
     +       'tidal potential at Greenwich.')
c
      write(6,613)
 613  format(6x,'"A-phase" means phase with respect to +cos-argume',
     +       'nt of local potential.')
c
      write(6,614)
 614  format(6x,'"R-phase" means phase with respect to +cos-argume',
     +       'nt of equilibrium tide.')
c
      write(6,6001)
 6001 format(' ')
      write(6,6002)
 6002 format(' ****************************************',
     +       '*****************')
      write(6,6003)
 6003 format(' **                Oceanic tidal effects ',
     +       '               **')
      write(6,6002)
      write(6,6001)
c
c -----< Amplitude and phase for easch mesh >-----
c
      write(6,610)
 610  format(12x,'1-st order mesh',9x,'2-nd order mesh',
     +        9x,'3-rd order mesh',9x,'4-th order mesh',
     +       13x,'Total')
c
      write(6,609)
 609  format(4x,5(7x,'Amplitude G-phase'))
c
      do nc = 1,ncmp
c
         write(6,616) lcomp(nc,kind)
 616     format(1x,a8)
c
         do iw = 1,nwave
c
            write(6,602) wn(ncnt(iw)) ,
     +                   amps(1,k,nc,is,iw), phsg(1,k,nc,is,iw),
     +                   amps(2,k,nc,is,iw), phsg(2,k,nc,is,iw),
     +                   amps(3,k,nc,is,iw), phsg(3,k,nc,is,iw),
     +                   amps(4,k,nc,is,iw), phsg(4,k,nc,is,iw),
     +                   amps(5,k,nc,is,iw), phsg(5,k,nc,is,iw)
 602        format(1x,a3,1x,5(3x,1pe12.4,1(0pf9.3)))
c
         enddo                  ! iw
c
         write(6,6001)
c
         if (kind.eq.3) then
c
            write(6,6004)
 6004       format(' Attraction (Newtonian) part')
c
            do iw = 1,nwave
c
               write(6,602) wn(ncnt(iw)),
     +                      ampa(1,is,iw)  , phsa(1,is,iw),
     +                      ampa(2,is,iw)  , phsa(2,is,iw),
     +                      ampa(3,is,iw)  , phsa(3,is,iw),
     +                      ampa(4,is,iw)  , phsa(4,is,iw),
     +                      ampa(5,is,iw)  , phsa(5,is,iw)
c
            enddo               ! iw
c
c
            write(6,6001)
            write(6,6005)
 6005       format(' Loading (Elastic) part')
c
            do iw = 1,nwave
c
               write(6,602) wn(ncnt(iw)),
     +                      ampe(1,is,iw)  , phse(1,is,iw),
     +                      ampe(2,is,iw)  , phse(2,is,iw),
     +                      ampe(3,is,iw)  , phse(3,is,iw),
     +                      ampe(4,is,iw)  , phse(4,is,iw),
     +                      ampe(5,is,iw)  , phse(5,is,iw)
c
               if (nc.ne.ncmp .and. iw.eq.nwave) then
                  write(6,6001)
                  write(6,6001)
               endif
c
            enddo               ! iw
c
         endif
c
      enddo                     ! nc
c
      return
      end
c
