c$gellip
c---------------------------------------------------------------
      subroutine gellip(faid  , alti  , nw    , isp   , iy    ,
     +                  im    , id    , itime , efact , rigd   )
c---------------------------------------------------------------
c
c     This computes the gtavity tide on a rigid Earth
c     which is used in the program BAYTAP-G by Tamura et al.(1991)
c
      implicit double precision (a-h,o-z)
c
      common /const/  rearth, earthm, gravct, pi , rad, deg,
     +                dens  , rls1  , rls2  , egv, elp
c
      dimension ampl2(21)
      dimension tampl(21)
c
c     1   2   3   4   5   6   7   8   9   10  11
c     M2  S2  K1  O1  N2  P1  K2  Q1  M1  J1  OO1
c     12  13  14  15  16  17  18  19  20  21
c     2N2 Mu2 Nu2 L2  T2  Mtm Mf  Mm  Ssa Sa
c
c -----< Amplitude of P2 potential >-----
c
      data (ampl2(i),i=1,21)
     +     /  0.908184d0,  0.422535d0, -0.529876d0,  0.376763d0,
     +        0.173881d0,  0.175307d0,  0.114860d0,  0.072136d0,
     +       -0.029631d0, -0.029630d0, -0.016212d0,  0.023009d0,
     +        0.027768d0,  0.033027d0, -0.025670d0,  0.024701d0,
     +        0.029926d0,  0.156303d0,  0.082569d0,  0.072732d0,
     +        0.011549d0 /
c
c -----< Time variation of tidal amplitude >-----
c
      data (tampl(i),i=1,21)
     +     /  0.000086d0,  0.000040d0,  0.000224d0, -0.000178d0,
     +        0.000015d0, -0.000083d0, -0.000121d0, -0.000035d0,
     +        0.000013d0,  0.000012d0,  0.000026d0,  0.000003d0,
     +        0.000002d0,  0.000002d0, -0.000002d0, -0.000059d0,
     +       -0.000033d0, -0.000165d0,  0.000027d0, -0.000081d0,
     +       -0.000024d0 /
c
      data  re     / 6378.137d3 /
      data  flat   / 3.35292d-3 /
      data  ge     / 3.98600448d20 /
      data  fmu    / 0.012300034d0 /
      data  etmut  / 58.0d0 /
      data  timsys / 0.d0 /
      data  sinpi  / 3422.448d0 /
c
      phi = faid*rad
c
c Amplitude of tide generating potential for each wave
c at the epoch 00:00:00 UTC OF IY-IM-ID
c
      cv   = 3.d0 / 4.d0 * fmu * ge * ( sinpi/3600.d0*rad )**3 / re**2
      cv6  =  -1.d6*cv
c
      if (itime.eq.0) then
         amp  =  ampl2(nw)
      else
         tu0  = (   tjulid( iy,im,id, 0, 0, 0 )
     +            - 2451545.d0 + timsys/24.d0 ) / 36525.d0
         td0  = tu0 + etmut/86400.d0/36525.d0
         dap  =  tampl(nw) * td0
         amp  =  ampl2(nw) + dap
       endif
c
c Coefficients concerning the normal direction to a reference ellipsoid
c
      cosphi = dcos( phi )
      sinphi = dsin( phi )
      e2     = 2.d0*flat - flat**2
      roe    = (  1.d0      / dsqrt( 1.d0 - e2*sinphi**2 ) + alti/re)
     +       * cosphi
      rop    = (( 1.d0-e2 ) / dsqrt( 1.d0 - e2*sinphi**2 ) + alti/re)
     +       * sinphi
c
c # for Zonal
c
      if (isp.eq.0) then
c
         efact = roe*cosphi - 2.d0*rop*sinphi
         gc    = 1.d0 * cv6 * efact
c
c # for Diurnal
c
      elseif(isp.eq.1) then
c
         efact = rop*cosphi + roe*sinphi
         gc    = 2.d0 * cv6 * efact
c
c # for Semidiurnal
c
      elseif(isp.eq.2) then
c
         efact = roe * cosphi
         gc    = 2.d0 * cv6 * efact
c
      else
         print*,'!!! Error at <gellip>. Wrong isp value.'
         stop
      endif
c
c -----< Amplitude on a rigid Earth >-----
c
      rigd  = -gc*dabs(amp) * 1.d-12 ! Upward positive
c
      return
      end
c
