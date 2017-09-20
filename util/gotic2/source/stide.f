c$stide
c------------------------------------------------------------------
      subroutine stide(istat, kind  ,nw ,camp ,samp)
c------------------------------------------------------------------
c
c     PROGRAM TO COMPUTE EQUILIBRIUM SOLID TIDE
c             BY USING J.WAHR'S TABLE OF LOVE  NUMBERS
c             FOR 1066A EARTH MODEL
c             ( GEOPHYS. J. R. ASTR. SOC. 1981 VOL.64   677-703 )
c
c             Ref. for delta factor
c             Dehant, V. and B. Ducarme
c               Comparison between the theoretical and observed
c               tidal gravimetric factors, PEPI, 49, 192-212, 1987
c
c------------------------------------------------------------------
c
c     KIND: INTEGER NUMBER INDICATING TIDAL COMPONENT TO BE COMPUTED
c          NO.       COMPONENT                  +SIGHN CONVENTION
c           1    RADIAL DISPLACEMENT             UP WARD
c           2    HORIZONTAL DISPLACEMENT
c                   1:NS                         NORTH WARD
c                   2:EW                         EAST  WARD
c                   3:AZIMUTHAL                  AZIMURTHAL
c           3    GRAVITATIONAL ATRACTION         UP WARD ATTRACTION
c           4    TILT
c                   1:NS                    UP WARD MOTION OF N-GROUND
c                   2:EW                    UP WARD MOTION OF E-GROUND
c                   3:AZIMUTHAL             UP WARD MOTION OF A-GROUND
c           5    STRAIN
c                   1:NS(FAI-FAI)                EXPANSION
c                   2:EW(RAMDA-RAMDA)            EXPANSION
c                   3:SHEAR(FAI-RAMDA)           N TO E
c                   4:AZIMUTHAL                  EXPANSION
c                   5 AREAL STRAIN               EXPANSION
c                   6:CUBIC DILATATION           EXPANSION
c           6    DEFLECTION OF LOCAL VERTICAL
c                   1:NS
c                   2:EW
c
c     NW:   INTEGER NUMBER REPRESENTING THE PARTIAL WAVES
c                   1   2   3   4   5   6   7   8
c                   M2  S2  K1  O1  N2  P1  K2  Q1
c                   9   10  11  12  13  14  15  16
c                   M1  J1  OO1 2N2 Mu2 Nu2 L2  T2
c                   17  18  19  20  21
c                   Mtm Mf  Mm  Ssa Sa
c
c     THE PHASE OF EQUILIBURIUM SOLID TIDE IS GIVEN AS THAT
c     WITH RESPECT TO THE PLUS COS-ARGUMENT OF THE TIDAL POTENTAL.
c     THE EXPRESSIONS FOR THE COS-ARGUMENT OFEACH TIDAL CONSTITUENT
c     ARE GIVEN IN THE PAPER BY SCHWIDERSKI.
c
c     HLS: ABSOLUTE AMPLITUDE OF PARTIAL WAVE OF TIDAL POTENTIAL
c     CAMP,SAMP: REAL AND IMAGINALY PART OF TIDAL AMPLITUDE
c
c     SUBROUTINES CALLED BY THIS PROGRAM
c
c        1) SPHARM(CL,L,M,ID): FUNCTION TO COMPUTE SPHERICAL HARMONICS
c                   CL: STATION COLATITUDE IN RADIAN
c                   L : ORDER NUMBER, M: DEGREE NUMBER,
c                   ID: NUMBER SHOWING DEGREE OF DIFFERENTIAL
c
c        2) TCTL(M)         : FUNCTION TO COMPUTE FACTORIAL OF M
c
c------------------------------------------------------------------
c
      implicit double precision (a-h,o-z)
c
      common /const/  rearth, earthm, gravct, pi , rad, deg,
     +                dens  , rls1  , rls2  , egv, elp
      common /gfile/  ang(50), grn(50,6), cgrn(50,2,3), igrn, idelta
      common /inela/  anel1, anel2
      common /stat99/ slat(10,3), slon(10,3),
     +                altd(10), azmth(10), slt(10), sln(10)
      common /gtimes/ igtime, igy, igm, igd
c
      dimension camp(6), samp(6), hlm(21), lp(21), mp(21)
      dimension crd(2,21), chd(6,21), cgrw(3,21), cgrd(3,21), 
     +          ctl(2,4,21), cst(3,21), cvd(2,4,21)
c
c               M2         S2         K1         O1
      data hlm/ 0.63192d0, 0.29400d0, 0.36878d0, 0.26221d0,
c
c               N2         P1         K2         Q1
     +          0.12099d0, 0.12203d0, 0.07996d0, 0.05020d0,
c
c               M1         J1         OO1        2N2
     +          0.02062d0, 0.02062d0, 0.01129d0, 0.01601d0,
c
c               Mu2        Nu2        L2         T2
     +          0.01932d0, 0.02298d0, 0.01786d0, 0.01720d0,
c
c               Mtm        Mf         Mm         Ssa
     +          0.01276d0, 0.06663d0, 0.03518d0, 0.03100d0,
c
c               Sa
     +          0.00492d0/
c
      data lp/2, 2, 2, 2, 2, 2, 2, 2,
     +        2, 2, 2, 2, 2, 2, 2, 2,
     +        2, 2, 2, 2, 2/
c
      data mp/2, 2, 1, 1, 2, 1, 2, 1,
     +        1, 1, 1, 2, 2, 2, 2, 2,
     +        0, 0, 0, 0, 0/
c
c Radial Displacement
c
      data ((crd(j,k),k=1,21),j=1,2)
     +     / 0.6090d0, 0.6090d0, 0.5200d0, 0.6030d0,
     +       0.6090d0, 0.5810d0, 0.6090d0, 0.6030d0,
     +       0.6000d0, 0.6110d0, 0.6080d0, 0.6090d0,
     +       0.6090d0, 0.6090d0, 0.6090d0, 0.6090d0,
     +       0.6060d0, 0.6060d0, 0.6060d0, 0.6060d0,
     +       0.6060d0,
c
     +       0.0010d0, 0.0010d0, 0.0010d0, 0.0010d0,
     +       0.0010d0, 0.0010d0, 0.0010d0, 0.0010d0,
     +       0.0010d0, 0.0010d0, 0.0010d0, 0.0010d0,
     +       0.0010d0, 0.0010d0, 0.0010d0, 0.0010d0,
     +       0.0010d0, 0.0010d0, 0.0010d0, 0.0010d0,
     +       0.0010d0/
c
c
c Holizontal Displacement
c
      data ((chd(j,k),k=1,21),j=1,2)
     +     / 0.0852d0, 0.0852d0, 0.0868d0, 0.0841d0,
     +       0.0852d0, 0.0849d0, 0.0852d0, 0.0841d0,
     +       0.0842d0, 0.0839d0, 0.0840d0, 0.0852d0,
     +       0.0852d0, 0.0852d0, 0.0852d0, 0.0852d0,
     +       0.0840d0, 0.0840d0, 0.0840d0, 0.0840d0,
     +       0.0840d0,
c
     +       0.0140d0, 0.0140d0, 0.0110d0, 0.0140d0,
     +       0.0140d0, 0.0130d0, 0.0140d0, 0.0140d0,
     +       0.0140d0, 0.0140d0, 0.0140d0, 0.0140d0,
     +       0.0140d0, 0.0140d0, 0.0140d0, 0.0140d0,
     +       0.0140d0, 0.0140d0, 0.0140d0, 0.0140d0,
     +       0.0140d0/
c
      data ((chd(j,k),k=1,21),j=3,4)
     +    / -0.0010d0,-0.0010d0,-0.0010d0,-0.0020d0,
     +      -0.0010d0,-0.0020d0,-0.0010d0,-0.0020d0,
     +      -0.0020d0,-0.0020d0,-0.0020d0,-0.0010d0,
     +      -0.0010d0,-0.0010d0,-0.0010d0,-0.0010d0,
     +      -0.0020d0,-0.0020d0,-0.0020d0,-0.0020d0,
     +      -0.0020d0,
c
     +       0.0010d0, 0.0010d0, 0.0000d0, 0.0000d0,
     +       0.0010d0, 0.0000d0, 0.0010d0, 0.0000d0,
     +       0.0000d0, 0.0000d0, 0.0000d0, 0.0010d0,
     +       0.0010d0, 0.0010d0, 0.0010d0, 0.0010d0,
     +       0.0000d0, 0.0000d0, 0.0000d0, 0.0000d0,
     +       0.0000d0/
c
c
c Gravity
c
c     Wahr(1981) delta factors for 1066A Earth model
c
      data ((cgrw(j,k),k=1,21),j=1,3)
     +     / 1.1600d0, 1.1600d0, 1.1320d0, 1.1520d0,
     +       1.1600d0, 1.1470d0, 1.1600d0, 1.1520d0,
     +       1.1520d0, 1.1550d0, 1.1540d0, 1.1600d0,
     +       1.1600d0, 1.1600d0, 1.1600d0, 1.1600d0,
     +       1.1550d0, 1.1550d0, 1.1550d0, 1.1550d0,
     +       1.1550d0,
c
     +      -0.0050d0,-0.0050d0,-0.0060d0,-0.0060d0,
     +      -0.0050d0,-0.0060d0,-0.0050d0,-0.0060d0,
     +      -0.0060d0,-0.0060d0,-0.0060d0,-0.0060d0,
     +      -0.0060d0,-0.0060d0,-0.0060d0,-0.0060d0,
     +      -0.0070d0,-0.0070d0,-0.0070d0,-0.0070d0,
     +      -0.0070d0,
c
     +       0.0000d0, 0.0000d0, 0.0000d0, 0.0000d0,
     +       0.0000d0, 0.0000d0, 0.0000d0, 0.0000d0,
     +       0.0000d0, 0.0000d0, 0.0000d0, 0.0000d0,
     +       0.0000d0, 0.0000d0, 0.0000d0, 0.0000d0,
     +       0.0050d0, 0.0050d0, 0.0050d0, 0.0050d0,
     +       0.0050d0/
c
c     Dehant(1987) delta factors for 1066A Earth model
c
      data ((cgrd(j,k),k=1,21),j=1,3)
     +     / 1.1613d0, 1.1613d0, 1.1348d0, 1.1551d0,
     +       1.1613d0, 1.1500d0, 1.1613d0, 1.1551d0,
     +       1.1551d0, 1.1577d0, 1.1571d0, 1.1613d0,
     +       1.1613d0, 1.1613d0, 1.1613d0, 1.1613d0,
     +       1.1573d0, 1.1573d0, 1.1573d0, 1.1573d0,
     +       1.1573d0,
c
     +      -0.0009d0,-0.0009d0,-0.0019d0,-0.0014d0,
     +      -0.0009d0,-0.0015d0,-0.0009d0,-0.0014d0,
     +      -0.0014d0,-0.0013d0,-0.0013d0,-0.0009d0,
     +      -0.0009d0,-0.0009d0,-0.0009d0,-0.0009d0,
     +      -0.0016d0,-0.0016d0,-0.0016d0,-0.0016d0,
     +      -0.0016d0,
c
     +       0.0000d0, 0.0000d0, 0.0000d0, 0.0000d0,
     +       0.0000d0, 0.0000d0, 0.0000d0, 0.0000d0,
     +       0.0000d0, 0.0000d0, 0.0000d0, 0.0000d0,
     +       0.0000d0, 0.0000d0, 0.0000d0, 0.0000d0,
     +       0.0053d0, 0.0053d0, 0.0053d0, 0.0053d0,
     +       0.0053d0/
c
c N-S Tilt
c
      data ((ctl(1,j,k),k=1,21),j=1,2)
     +     / 0.6920d0, 0.6920d0, 0.7300d0, 0.6890d0,
     +       0.6920d0, 0.7000d0, 0.6920d0, 0.6890d0,
     +       0.6900d0, 0.6850d0, 0.6870d0, 0.6920d0,
     +       0.6920d0, 0.6920d0, 0.6920d0, 0.6920d0,
     +       0.6890d0, 0.6890d0, 0.6890d0, 0.6890d0,
     +       0.6890d0,
c
     +      -0.0010d0,-0.0010d0,-0.0010d0,-0.0010d0,
     +      -0.0010d0,-0.0010d0,-0.0010d0,-0.0010d0,
     +      -0.0010d0,-0.0010d0,-0.0010d0,-0.0010d0,
     +      -0.0010d0,-0.0010d0,-0.0010d0,-0.0010d0,
     +      -0.0010d0,-0.0010d0,-0.0010d0,-0.0010d0,
     +      -0.0010d0/
c
      data ((ctl(1,j,k),k=1,21),j=3,4)
     +    / -0.0010d0,-0.0010d0,-0.0010d0,-0.0010d0,
     +      -0.0010d0,-0.0010d0,-0.0010d0,-0.0010d0,
     +      -0.0010d0,-0.0010d0,-0.0010d0,-0.0010d0,
     +      -0.0010d0,-0.0010d0,-0.0010d0,-0.0010d0,
     +       0.0000d0, 0.0000d0, 0.0000d0, 0.0000d0,
     +       0.0000d0,
c
     +       0.0000d0, 0.0000d0, 0.0040d0, 0.0040d0,
     +       0.0000d0, 0.0040d0, 0.0000d0, 0.0040d0,
     +       0.0040d0, 0.0040d0, 0.0040d0, 0.0000d0,
     +       0.0000d0, 0.0000d0, 0.0000d0, 0.0000d0,
     +       0.0000d0, 0.0000d0, 0.0000d0, 0.0000d0,
     +       0.0000d0/
c
c E-W Tilt
c
      data ((ctl(2,j,k),k=1,21),j=1,3)
     +     / 0.6890d0, 0.6890d0, 0.7300d0, 0.6890d0,
     +       0.6890d0, 0.7000d0, 0.6890d0, 0.6880d0,
     +       0.6900d0, 0.6850d0, 0.6860d0, 0.6890d0,
     +       0.6890d0, 0.6890d0, 0.6890d0, 0.6890d0,
     +       0.0000d0, 0.0000d0, 0.0000d0, 0.0000d0,
     +       0.0000d0,
c
     +      -0.0020d0,-0.0020d0,-0.0010d0,-0.0010d0,
     +      -0.0020d0,-0.0010d0,-0.0020d0,-0.0010d0,
     +      -0.0010d0,-0.0010d0,-0.0010d0,-0.0020d0,
     +      -0.0020d0,-0.0020d0,-0.0020d0,-0.0020d0,
     +       0.0000d0, 0.0000d0, 0.0000d0, 0.0000d0,
     +       0.0000d0,
c
     +       0.0000d0, 0.0000d0, 0.0020d0, 0.0020d0,
     +       0.0000d0, 0.0020d0, 0.0000d0, 0.0020d0,
     +       0.0020d0, 0.0020d0, 0.0020d0, 0.0000d0,
     +       0.0000d0, 0.0000d0, 0.0000d0, 0.0000d0,
     +       0.0000d0, 0.0000d0, 0.0000d0, 0.0000d0,
     +       0.0000d0/
c
c Strain
c
      data ((cst(j,k),k=1,21),j=1,3)
     +     / 0.6090d0, 0.6090d0, 0.5200d0, 0.6030d0,
     +       0.6090d0, 0.5810d0, 0.6090d0, 0.6040d0,
     +       0.6010d0, 0.6110d0, 0.6080d0, 0.6090d0,
     +       0.6090d0, 0.6090d0, 0.6090d0, 0.6090d0,
     +       0.6060d0, 0.6060d0, 0.6060d0, 0.6060d0,
     +       0.6060d0,
c
     +       0.0850d0, 0.0850d0, 0.0870d0, 0.0840d0,
     +       0.0850d0, 0.0850d0, 0.0850d0, 0.0840d0,
     +       0.0840d0, 0.0840d0, 0.0840d0, 0.0850d0,
     +       0.0850d0, 0.0850d0, 0.0850d0, 0.0850d0,
     +       0.0840d0, 0.0840d0, 0.0840d0, 0.0840d0,
     +       0.0840d0,
c
     +       0.0010d0, 0.0010d0, 0.0010d0, 0.0010d0,
     +       0.0010d0, 0.0010d0, 0.0010d0, 0.0010d0,
     +       0.0010d0, 0.0010d0, 0.0010d0, 0.0010d0,
     +       0.0010d0, 0.0010d0, 0.0010d0, 0.0010d0,
     +       0.0010d0, 0.0010d0, 0.0010d0, 0.0010d0,
     +       0.0010d0/
c
c N-S Vertical Deflection
c
      data ((cvd(1,j,k),k=1,21),j=1,2)
     +     /-1.2170d0,-1.2170d0,-1.1670d0,-1.2120d0,
     +      -1.2170d0,-1.2000d0,-1.2170d0,-1.2120d0,
     +      -1.2100d0,-1.2160d0,-1.2150d0,-1.2170d0,
     +      -1.2170d0,-1.2170d0,-1.2170d0,-1.2170d0,
     +      -1.2150d0,-1.2150d0,-1.2150d0,-1.2150d0,
     +      -1.2150d0,
c
     +       0.0010d0, 0.0010d0, 0.0010d0, 0.0010d0,
     +       0.0010d0, 0.0010d0, 0.0010d0, 0.0010d0,
     +       0.0010d0, 0.0010d0, 0.0010d0, 0.0010d0,
     +       0.0010d0, 0.0010d0, 0.0010d0, 0.0010d0,
     +       0.0010d0, 0.0010d0, 0.0010d0, 0.0010d0,
     +       0.0010d0/
c
      data ((cvd(1,j,k),k=1,21),j=3,4)
     +     / 0.0040d0, 0.0040d0, 0.0050d0, 0.0050d0,
     +       0.0040d0, 0.0050d0, 0.0040d0, 0.0050d0,
     +       0.0050d0, 0.0050d0, 0.0050d0, 0.0040d0,
     +       0.0040d0, 0.0040d0, 0.0040d0, 0.0040d0,
     +       0.0050d0, 0.0050d0, 0.0050d0, 0.0050d0,
     +       0.0050d0,
c
     +       0.0000d0, 0.0000d0,-0.0080d0,-0.0080d0,
     +       0.0000d0,-0.0090d0, 0.0000d0,-0.0080d0,
     +      -0.0090d0,-0.0090d0,-0.0090d0, 0.0000d0,
     +       0.0000d0, 0.0000d0, 0.0000d0, 0.0000d0,
     +      -0.0080d0,-0.0080d0,-0.0080d0,-0.0080d0,
     +      -0.0080d0/
c
c E-W Vertical Deflection
c
      data ((cvd(2,j,k),k=1,21),j=1,3)
     +     /-1.2160d0,-1.2160d0,-1.1660d0,-1.2100d0,
     +      -1.2160d0,-1.1990d0,-1.2160d0,-1.2110d0,
     +      -1.2090d0,-1.2150d0,-1.2130d0,-1.2160d0,
     +      -1.2160d0,-1.2160d0,-1.2160d0,-1.2160d0,
     +       0.0000d0, 0.0000d0, 0.0000d0, 0.0000d0,
     +       0.0000d0,
c
     +       0.0000d0, 0.0000d0, 0.0000d0, 0.0000d0,
     +       0.0000d0, 0.0000d0, 0.0000d0, 0.0000d0,
     +       0.0000d0, 0.0000d0, 0.0000d0, 0.0000d0,
     +       0.0000d0, 0.0000d0, 0.0000d0, 0.0000d0,
     +       0.0000d0, 0.0000d0, 0.0000d0, 0.0000d0,
     +       0.0000d0,
c
     +       0.0000d0, 0.0000d0,-0.0050d0,-0.0050d0,
     +       0.0000d0,-0.0050d0, 0.0000d0,-0.0050d0,
     +      -0.0050d0,-0.0050d0,-0.0050d0, 0.0000d0,
     +       0.0000d0, 0.0000d0, 0.0000d0, 0.0000d0,
     +       0.0000d0, 0.0000d0, 0.0000d0, 0.0000d0,
     +       0.0000d0/
c
c-----------------------------------------------------------------------
c
      erd = rearth
c
      fai = slt(istat)
      alt = altd(istat)
      clr = (90.d0 - fai)*rad  ! Station Colatitude (radian)
c
      do i = 1,6
         camp(i) = 0.d0
         samp(i) = 0.d0
      enddo
c
c -----< RADIAL DISPLACEMENT >-----
c
      if (kind.eq.1) then
c
         rh  = hlm(nw)
         L1  = lp(nw)
         m1  = mp(nw)
         id1 = 0
c
         y1 = spharm(clr, L1, m1, id1)
         c0 = crd(1,nw)
         c1 = crd(2,nw)/2.d0*(3.d0*dcos(clr)**2 - 1.d0)
         camp(1) = rh*c0*(1.d0 + c1)*y1
         samp(1) = 0.d0
c
         return
c
      endif
c
c -----< HORIZONTAL DISPLACEMENT >-----
c
      if (kind.eq.2) then
c
         rh = hlm(nw)
c
c # NS COMPONENT    NORTH WARD: PLUS
c
         L1  = lp(nw)
         m1  = mp(nw)
         id1 = 1
         L2  = L1 + 2
         m2  = m1
         id2 = 1
         L3  = L1 + 1
         m3  = m1
         id3 = 0
c
         y1 = spharm(clr, L1, m1, id1)
         y2 = spharm(clr, L2, m2, id2)
         y3 = spharm(clr, L3, m3, id3)
         c0 = chd(1,nw)
         c1 = 1.d0 + chd(2,nw)/2.d0*(3.d0*dcos(clr)**2 - 1.d0)
         c2 = chd(3,nw)
         c3 = dfloat(m1)/dsin(clr)*chd(4,nw)
         camp(1) = (-1.d0)*rh*c0*(c1*y1 + c2*y2 + c3*y3)
         samp(1) = 0.d0
c     
c # EW COMPONENT    EASTWARD : PLUS
c
         L1  = lp(nw)
         m1  = mp(nw)
         id1 = 0
         L2  = L1 + 2
         m2  = m1
         id2 = 0
         L3  = L1 + 1
         m3  = m1
         id3 = 1
c
         y1  = spharm(clr, L1, m1, id1)
         y2  = spharm(clr, L2, m2, id2)
         y3  = spharm(clr, L3, m3, id3)
         c0  = chd(1,nw)
         c3  = chd(4,nw)
         sm1 = dfloat(m1)/dsin(clr)
         camp(2) = 0.d0
         samp(2) = (-1.d0)*rh*c0*(sm1*(c1*y1 + c2*y2) + c3*y3)
c
c # AZIMUTHAL COMPONENT
c
         az  = azmth(istat)
         caz = dcos(az)
         saz = dsin(az)
         camp(3) = camp(1)*caz + camp(2)*saz
         samp(3) = samp(1)*caz + samp(2)*saz
c
         return
c
      endif
c
c -----< GRAVITY >-----  UP WARD FORCE: PLUS
c
      if (kind.eq.3) then
c
         rh  = egv*hlm(nw)/erd
         L1  = lp(nw)
         L2  = L1 + 2
         L3  = L1 - 2
         m1  = mp(nw)
         m2  = m1
         m3  = m1
         id1 = 0
         id2 = 0
         id3 = 0
c
c # Rigid Earth tide
c
         call gellip(fai   , alt   , nw    , m1    , igy  , igm   ,
     +               igd   , igtime, efact , riga                   )
         ramp  = riga
         efact = 1.d0
c
c # Delta factor
c
         if (idelta.eq.1) then
c     
            c1 = cgrw(1,nw)
            c2 = cgrw(2,nw)
            c3 = cgrw(3,nw)
c
         else if (idelta.eq.2) then
c
            c1 = cgrd(1,nw)
            c2 = cgrd(2,nw)
            c3 = cgrd(3,nw)
c
         else
c
            print*,'!!! Error : Wrong idelta value : ',idelta
            print*,'!!! Stop in subroutine <stide>'
            stop
c     
         endif
c
c # Genelarized spherical hamonic functions
c
         if (m1.eq.0) then
            z2 = glsph(clr, m1, 1)
            z3 = glsph(clr, m1, 2)
         else
            z2 = glsph(clr, m1, 1)
            z3 = 0.d0
         endif
c
         tfact1 = c1 + (c2*z2 + c3*z3)
         tfact2 = tfact1 + (tfact1 - 1.d0)*anel1
         camp(1) = ramp*tfact2
         samp(1) = ramp*anel2
c
         return
c
      endif
c
c -----< TILT >-----
c
      if (kind.eq.4) then
c
         rh = hlm(nw)/erd
c
c # NS COMPONENT
         L1  = lp(nw)
         m1  = mp(nw)
         id1 = 1
         L2  = L1 + 2
         m2  = m1
         id2 = 1
         L3  = L1 + 1
         m3  = m1
         id3 = 0
         L4  = L1 - 1
         m4  = m1
         id4 = 0
c
         y1 = spharm(clr, L1, m1, id1)
         y2 = spharm(clr, L2, m2, id2)
         y3 = spharm(clr, L3, m3, id3)
         y4 = spharm(clr, L4, m4, id4)
         c1 = ctl(1,1,nw)
         c2 = ctl(1,2,nw)
         c3 = ctl(1,3,nw)*dfloat(m1)/dsin(clr)
         c4 = ctl(1,4,nw)*dfloat(m1)/dsin(clr)
         camp(1) = rh*(c1*y1 + c2*y2 + c3*y3 + c4*y4)
         samp(1) = 0.d0
c
c # EW COMPONENT   PLUS SIGN: UPWARD MOTION OF EAST SIDE GROUND
         L1  = lp(nw)
         m1  = mp(nw)
         id1 = 0
         L2  = L1 + 1
         m2  = m1
         id2 = 1
         L3  = L1 - 1
         m3  = m1
         id3 = 1
c
         y1 = spharm(clr, L1, m1, id1)
         y2 = spharm(clr, L2, m2, id2)
         y3 = spharm(clr, L3, m3, id3)
         c1 = ctl(2,1,nw)*dfloat(m1)/dsin(clr)
         c2 = ctl(2,2,nw)
         c3 = ctl(2,3,nw)
         camp(2) = 0.d0
         samp(2) = rh*(c1*y1 + c2*y2 + c3*y3)
c
c # AZIMUTHAL COMPONENT
         az  = azmth(istat)
         caz = dcos(az)
         saz = dsin(az)
         camp(3) = camp(1)*caz + camp(2)*saz
         samp(3) = samp(1)*caz + samp(2)*saz
c
         return
c
      endif
c
c -----< TENSOR STRAIN >-----
c
      if (kind.eq.5) then
c
         cz  = 3.d0*dcos(clr)**2 - 1.d0
         cot = dcos(clr)/dsin(clr)
         rh  = hlm(nw)/(erd*(1.d0 - 1.d0/3.d0*elp*cz))
c
c # NS COMPONENT: FAI-FAI COMPONENT
         L1  = lp(nw)
         m1  = mp(nw)
         id1 = 0
         L2  = L1
         m2  = m1
         id2 = 2
c
         L3  = L1
         m3  = m1
         id3 = 2
c
         y1  = spharm(clr, L1, m1, id1)
         y2  = spharm(clr, L2, m2, id2)
         y3  = spharm(clr, L3, m3, id3)
         c1  = cst(1,nw)
         c2  = cst(2,nw)
         c3  = cst(3,nw)*0.5d0*cz
         camp(1) = rh*(c1*y1 + c2*y2 + c3*y3)
         samp(1) = 0.d0
c
c# EW COMPONENT: RAMDA-RAMDA COMPONENT
         L1  = lp(nw)
         m1  = mp(nw)
         id1 = 0
         L2  = L1
         m2  = m1
         id2 = 1
c     
         y1  = spharm(clr, L1, m1, id1)
         y2  = spharm(clr, L2, m2, id2)
         c1  = cst(1,nw)
         c2  = cst(2,nw)
         c3  = cst(3,nw)
         sm1 = dfloat(m1)/dsin(clr)
         sm2 = sm1*sm1
         camp(2) = rh*(c1*y1 - (c2 + c3/2.d0*cz)*(sm2*y1 - cot*y2))
         samp(2) = 0.d0
c
c # SHEAR : FAI-RAMDA COMPONENT OF TENSOR
         camp(3) = 0.d0
         samp(3) = (-1.d0)*rh*sm1*(c2 + c3/2.d0*cz)*(cot*y1 - y2)
c
c # AZIMUTHAL COMPONENT
         az  = azmth(istat)
         caz = dcos(az)
         saz = dsin(az)
         cca = caz*caz
         ssa = saz*saz
         csa = caz*saz
         camp(4) = camp(1)*cca + 2.d0*camp(3)*csa + camp(2)*ssa
         samp(4) = samp(1)*cca + 2.d0*samp(3)*csa + samp(2)*ssa
c
c # AREAL STRAIN
         camp(5) = camp(1) + camp(2)
         samp(5) = samp(1) + samp(2)
c
c # CUBIC DILATATION
c # RLS=L/(L+2*G), L AND G ARE LAME'S CONST. AND RIGIDITY AT THE SURFACE.
         if (igrn .eq. 1) rls = rls1
         if (igrn .eq. 2) rls = rls2
         camp(6) = (1.d0 - rls)*camp(5)
         samp(6) = (1.d0 - rls)*samp(5)
c
         return
c
      endif
c
c -----< DEFLECTION OF LOCAL VERTICAL >-----
c
      if (kind.eq.6) then
c
c # NS COMPONENT  NORTH WARD DEFLECTION IS PLUS SIGN.
         cz  = 3.d0*dcos(clr)**2 - 1.d0
         sn  = dsin(clr)
         rr  = 1.d0/(erd*(1.d0 - 1.d0/3.d0*elp*cz))
         rh  = rr*hlm(nw)
         L1  = lp(nw)
         m1  = mp(nw)
         id1 = 1
         L2  = L1 + 2
         m2  = m1
         id2 = 1
         L3  = L1 + 1
         m3  = m1
         id3 = 0
         L4  = L1 - 1
         m4  = m1
         id4 = 0
c
         y1 = spharm(clr, L1, m1, id1)
         y2 = spharm(clr, L2, m2, id2)
         y3 = spharm(clr, L3, m3, id3)
         y4 = spharm(clr, L4, m4, id4)
         c1 = cvd(1,1,nw)
         c2 = cvd(1,2,nw)
         c3 = cvd(1,3,nw)/sn
         c4 = cvd(1,4,nw)/sn
         camp(1) = (-1.d0)*rh*(c1*y1 + c2*y2 + c3*y3 + c4*y4)
         samp(1) = 0.d0
c
c # EW COMPONENT   EAST WARD DEFLECTION IS PLUS SIGN.
         L1  = lp(nw)
         m1  = mp(nw)
         id1 = 0
         L2  = L1 + 1
         m2  = m1
         id2 = 1
         L3  = L1 - 1
         m3  = m1
         id3 = 1
c
         y1 = spharm(clr, L1, m1, id1)
         y2 = spharm(clr, L2, m2, id2)
         y3 = spharm(clr, L3, m3, id3)
         c1 = cvd(2,1,nw)*dfloat(m1)/sn
         c2 = cvd(2,2,nw)
         c3 = cvd(2,3,nw)
         camp(2) = 0.d0
         samp(2) = rh/sn*(c1*y1 + c2*y2 + c3*y3)
c
         return
c
      endif
c
      stop 'Wrong kind ID!'
c
      end
c
