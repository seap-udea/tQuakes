c$vset
c------------------------------------------------------------------
      block data vset
c------------------------------------------------------------------
c
      implicit double precision (a-h,o-z)
c
      Logical Lfirst, Lvryfst, Lminfo
c
      common /comp/   ncomp(6)
      common /const/  rearth, earthm, gravct, pi , rad, deg,
     +                dens  , rls1  , rls2  , egv, elp
      common /nodupl/ Lfirst, Lvryfst, Lminfo
      common /wavei/  ncnt(21), isp(21)
      common /waver/  xlambda(21)
      common /wavec/  wn(21)
c
      character*3 wn
c
c
c Taken from Wahr, J. M., Body tides on an elliptical, rotating,
c elastic and Oceanless earth, Geophys. J. R. astr. Soc., 64, 677-703, 1981
c      data rearth  /6.371d+6/     ! Earth's mean radius (m)
c      data egv     /9.798529d0/   ! Equatorial gravity (m s^-2)
c      data elp     /0.00334/      ! Flattening
c
c Taken from "Global Earth Physics: A Handbook of Physical Constants"
c             Thomas J. Ahrens, Editor, 1995
      data rearth  /6.37101d+6/     ! Earth's mean radius (m)
      data egv     /9.7803267715d0/ ! Equatorial gravity (m s^-2)
      data elp     /0.0033528132d0/ ! Flattening (IAU,1976)
      data earthm  /5.9736d+24/     ! Earth's mass (kg)
      data dens    /1.035d3/        ! Sea water density (kg m^-3)
      data gravct  /6.67259d-11/    ! Gravitational constant 
c                                   !            (kg^-1 m^3 s^-2) 
c
c
      data rls1    /0.3311d0/       ! L/(L+2*G) for G-B model
      data rls2    /0.3958d0/       ! L/(L+2*G) for 1066A model
c
c
c
      data pi      /3.14159265358979d0/
      data rad     /1.745329251994329d-2/
      data deg     /5.729577951308232d+1/
c
c
c
      data Lfirst  /.true./
      data Lvryfst /.true./
      data Lminfo  /.true./
c
c
c
      data ncomp   /1, 3, 1, 3, 6, 2/
c
      data xlambda/ 2.d0, 2.d0, 1.d0, 1.d0, 2.d0, 1.d0, 2.d0, 1.d0,
     +              1.d0, 1.d0, 1.d0, 2.d0, 2.d0, 2.d0, 2.d0, 2.d0,
     +              0.d0, 0.d0, 0.d0, 0.d0, 0.d0                   /
      data wn     /'M2 ','S2 ','K1 ','O1 ','N2 ','P1 ','K2 ','Q1 ',
     +             'M1 ','J1 ','OO1','2N2','Mu2','Nu2','L2 ','T2 ',
     +             'Mtm','Mf ','Mm ','Ssa','Sa '                   /
      data isp    /    1,    1,    2,    2,    1,    2,    1,    2,
     +                 2,    2,    2,    1,    1,    1,    1,    1,
     +                 3,    3,    3,    3,    3                   /
c
      end
c



