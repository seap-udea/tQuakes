c$astro
c -----------------------------------------------------------
      subroutine astro(arg, arg2, smjd)
c -----------------------------------------------------------
c
      implicit   double precision(a-h,o-z)
c
      common /const/  rearth, earthm, gravct, pi , rad, deg,
     +                dens  , rls1  , rls2  , egv, elp
c
      dimension iarg(7,21), iarg2(7,21), xarg(7,21)
      dimension arg(21)   , arg2(21), fr(3,6)
c
      data  etmut  / 58.0d0 /
c
c Major 8
c
      data ((iarg(i,j),i=1,7),j=1,8)
     +         /2, 0, 0, 0, 0, 0,  0, ! M2      1
     +          2, 2,-2, 0, 0, 0,  0, ! S2      2
     +          1, 1, 0, 0, 0, 0, 90, ! K1      3
     +          1,-1, 0, 0, 0, 0,-90, ! O1      4
     +          2,-1, 0, 1, 0, 0,  0, ! N2      5
     +          1, 1,-2, 0, 0, 0,-90, ! P1      6
     +          2, 2, 0, 0, 0, 0,  0, ! K2      7
     +          1,-2, 0, 1, 0, 0,-90/ ! Q1      8
c               m  s  h  p  n  ps
c
c Minor 8
c
      data ((iarg(i,j),i=1,7),j=9,16)
     +         /1, 0, 0, 1, 0, 0, 90, ! M1      9
     +          1, 2, 0,-1, 0, 0, 90, ! J1     10
     +          1, 3, 0, 0, 0, 0, 90, ! OO1    11
     +          2,-2, 0, 2, 0, 0,  0, ! 2N2    12
     +          2,-2, 2, 0, 0, 0,  0, ! Mu2    13
     +          2,-1, 2,-1, 0, 0,  0, ! Nu2    14
     +          2, 1, 0,-1, 0, 0,180, ! L2     15
     +          2, 2,-3, 0, 0, 1,  0/ ! T2     16
c               m  s  h  p  n  ps
c
c Long period
c
      data ((iarg(i,j),i=1,7),j=17,21)
     +         /0, 3, 0,-1, 0, 0,  0, ! Mtm    17
     +          0, 2, 0, 0, 0, 0,  0, ! Mf     18
     +          0, 1, 0,-1, 0, 0,  0, ! Mm     19
     +          0, 0, 2, 0, 0, 0,  0, ! Ssa    20
     +          0, 0, 1, 0, 0,-1,  0/ ! Sa     21
c               m  s  h  p  n  ps
c
c Major 8 Sideband
c
      data ((iarg2(i,j),i=1,7),j=1,8)
     +         /2, 0, 0, 0,-1, 0,180, ! M2'     1
     +          2, 2,-2, 0,-1, 0,  0, ! S2'     2
     +          1, 1, 0, 0, 1, 0, 90, ! K1'     3
     +          1,-1, 0, 0,-1, 0,-90, ! O1'     4
     +          2,-1, 0, 1,-1, 0,180, ! N2'     5
     +          1, 1,-2, 0,-1, 0, 90, ! P1'     6
     +          2, 2, 0, 0, 1, 0,  0, ! K2'     7
     +          1,-2, 0, 1,-1, 0,-90/ ! Q1'     8
c               m  s  h  p  n  ps
c
c Minor 8 Sideband
c
      data ((iarg2(i,j),i=1,7),j=9,16)
     +         /1, 0, 0, 1, 1, 0, 90, ! M1'     9
     +          1, 2, 0,-1, 1, 0, 90, ! J1'    10
     +          1, 3, 0, 0, 1, 0, 90, ! OO1'   11
     +          2,-2, 0, 2,-1, 0,180, ! 2N2'   12
     +          2,-2, 2, 0,-1, 0,180, ! Mu2'   13
     +          2,-1, 2,-1,-1, 0,180, ! Nu2'   14
     +          2, 1, 0,-1,-1, 0,  0, ! L2'    15
     +          2, 2,-3, 0,-1, 1,  0/ ! T2'    16
c               m  s  h  p  n  ps
c
c Long period Sideband
c
      data ((iarg2(i,j),i=1,7),j=17,21)
     +         /0, 3, 0,-1, 1, 0,  0, ! Mtm'   17
     +          0, 2, 0, 0, 1, 0,  0, ! Mf'    18
     +          0, 1, 0,-1,-1, 0,180, ! Mm'    19
     +          0, 0, 2, 0, 1, 0,180, ! Ssa'   20
     +          0, 0, 1, 0,-1,-1,  0/ ! Sa'    21
c               m  s  h  p  n  ps
c
      data fr/280.4606184d0,  36000.7700536d0,  0.00038793d0,
     +        218.3166560d0, 481267.8813420d0, -0.00133000d0,
     +        280.4664490d0,  36000.7698220d0,  0.00030360d0,
     +         83.3532430d0,   4069.0137110d0, -0.01032400d0,
     +        234.9554440d0,   1934.1361850d0, -0.00207600d0,
     +        282.9373480d0,      1.7195330d0,  0.00045970d0/
c
c ----------------------------------------------------------------------
c
      tu  = (smjd - 51544.5d0) / 36525.d0
      tu2 = tu*tu
      tu3 = tu2*tu
      td  = tu + etmut/86400.d0/36525.d0
      td2 = td*td
      frac = smjd - dint(smjd)
c
      f2 = fr(1,2) + fr(2,2)*td + fr(3,2)*td2 
     +   + 0.0040d0*dcos((29.d0+133.d0*td)*rad)
c
      f1 = fr(1,1) + fr(2,1)*tu + fr(3,1)*tu2 
     +   - 0.0000000258d0*tu3   + 360.d0*frac - f2
c
      f3 = fr(1,3) + fr(2,3)*td + fr(3,3)*td2
     +   + 0.0018d0*dcos((159.d0+19.d0*td)*rad)
c
      f4 = fr(1,4) + fr(2,4)*td + fr(3,4)*td2
c
      f5 = fr(1,5) + fr(2,5)*td + fr(3,5)*td2
c
      f6 = fr(1,6) + fr(2,6)*td + fr(3,6)*td2
c
c
c
      do j = 1,21
         do i = 1,7
            xarg(i,j) = dfloat(iarg(i,j))
         enddo
      enddo
c
      do j = 1,21
c
         temp = f1*xarg(1,j) + f2*xarg(2,j) + f3*xarg(3,j)
     +        + f4*xarg(4,j) + f5*xarg(5,j) + f6*xarg(6,j)
     +        +    xarg(7,j)
         temp = mod(temp,360.d0)
         if (temp.lt.0.d0) temp = temp + 360.d0
c
         arg(j) = temp*rad ! in radian
c
      enddo
c
c
c
      do j = 1,21
         do i = 1,7
            xarg(i,j) = dfloat(iarg2(i,j))
         enddo
      enddo
c
      do j = 1,21
c
         temp = f1*xarg(1,j) + f2*xarg(2,j) + f3*xarg(3,j)
     +        + f4*xarg(4,j) + f5*xarg(5,j) + f6*xarg(6,j)
     +        +    xarg(7,j)
         temp = mod(temp,360.d0)
         if (temp.lt.0.d0) temp = temp + 360.d0
c
         arg2(j) = temp*rad ! in radian
c
      enddo
c
      return
      end
c
