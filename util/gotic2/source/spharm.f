c$spharm
c------------------------------------------------------------------
      double precision function spharm(cL ,L ,m ,id)
c------------------------------------------------------------------
c
c     FUNCTION SUBROUTINE TO COMPUTE ASSOCIATED LEGIANDRE
c     FUNCTION BELOW 4TH DEGREE
c
      implicit double precision (a-h,o-z)
c
      common /const/  rearth, earthm, gravct, pi , rad, deg,
     +                dens  , rls1  , rls2  , egv, elp
c
      if (L.lt.m) then
         spharm = 0.d0
         return
      endif
c
      x1 = dcos(cL)
      y1 = dsin(cL)
      x2 = x1*x1
      y2 = y1*y1
      x3 = x1*x2
      y3 = y1*y2
      x4 = x1*x3
      y4 = y1*y3
c
c     NORMALIZATION FACTOR
c
      mL1 = L - m
      mL2 = L + m
      fLm = factl(mL1)
      fLp = factl(mL2)
c
c     IN THIS COMPUTATION, WE TAKE THE DEPENDENCY OF (-1.)**M
c     INTO THE ARGUMENT OF EACH TIDAL SPECIES.
c     THUS
c
      cnr = dsqrt( ((2.d0*dfloat(L) + 1.d0)*fLm)/(4.d0*pi*fLp) )
c
c     ZEROTH DERIVATIVE
c
      if (id.eq.0) then
c
         if (L.eq.0 .and. m.eq.0) pLm = -1.d0
         if (L.eq.1 .and. m.eq.0) pLm = x1
         if (L.eq.1 .and. m.eq.1) pLm = y1
         if (L.eq.2 .and. m.eq.0) pLm = 0.5d0*(1.d0 - 3.d0*x2)
         if (L.eq.2 .and. m.eq.1) pLm = 3.d0*x1*y1
         if (L.eq.2 .and. m.eq.2) pLm = 3.d0*y2
         if (L.eq.3 .and. m.eq.0) pLm = 0.5d0*x1*(5.d0*x2 - 3.d0)
         if (L.eq.3 .and. m.eq.1) pLm = 1.5d0*y1*(5.d0*x2 - 1.d0)
         if (L.eq.3 .and. m.eq.2) pLm = 15.d0*x1*y2
         if (L.eq.3 .and. m.eq.3) pLm = 15.d0*y3
         if (L.eq.4 .and. m.eq.0) pLm = -1.d0/8.d0*(35.d0*x4
     +                                            - 30.d0*x2 + 3.d0)
         if (L.eq.4 .and. m.eq.1) pLm = 2.5d0*x1*y1*(7.d0*x2 - 3.d0)
         if (L.eq.4 .and. m.eq.2) pLm = 7.5d0*y2*(7.d0*x2 - 1.d0)
         if (L.eq.4 .and. m.eq.3) pLm = 105.d0*x1*y3
         if (L.eq.4 .and. m.eq.4) pLm = 105.d0*y4
c
c     FIRST DERIVATIVE
c
      else if (id.eq.1) then
c
         if (L.eq.0 .and. m.eq.0) pLm = 0.d0
         if (L.eq.1 .and. m.eq.0) pLm = -y1
         if (L.eq.1 .and. m.eq.1) pLm = x1
         if (L.eq.2 .and. m.eq.0) pLm = -3.d0*x1*y1
         if (L.eq.2 .and. m.eq.1) pLm = 3.d0*(2.d0*x2 - 1.d0)
         if (L.eq.2 .and. m.eq.2) pLm = 6.d0*x1*y1
         if (L.eq.3 .and. m.eq.0) pLm = 1.5d0*y1*(-5.d0*x2 + 1.d0)
         if (L.eq.3 .and. m.eq.1) pLm = 1.5d0*x1*(15.d0*x2 - 11.d0)
         if (L.eq.3 .and. m.eq.2) pLm = 15.d0*y1*(3.d0*x2 - 1.d0)
         if (L.eq.3 .and. m.eq.3) pLm = 45.d0*y2*x1
         if (L.eq.4 .and. m.eq.0) pLm = 2.5d0*x1*y1*(3.d0 - 7.d0*x2)
         if (L.eq.4 .and. m.eq.1) pLm = 2.5d0*(28.d0*x4
     +                                       - 27.d0*x2 + 3.d0)
         if (L.eq.4 .and. m.eq.2) pLm = 30.d0*x1*y1*(7.d0*x2 - 4.d0)
         if (L.eq.4 .and. m.eq.3) pLm = 105.d0*y2*(4.d0*x2 - 1.d0)
         if (L.eq.4 .and. m.eq.4) pLm = 420.d0*y3*x1
c
c     SECOND DERIVATIVE
c
      else if (id.eq.2) then
c
         if (L.eq.0 .and. m.eq.0) pLm = 0.d0
         if (L.eq.1 .and. m.eq.0) pLm = -x1
         if (L.eq.1 .and. m.eq.1) pLm = -y1
         if (L.eq.2 .and. m.eq.0) pLm = 3.d0*(1.d0 - 2.d0*x2)
         if (L.eq.2 .and. m.eq.1) pLm = -12.d0*x1*y1
         if (L.eq.2 .and. m.eq.2) pLm = 6.d0*(2.d0*x2 - 1.d0)
         if (L.eq.3 .and. m.eq.0) pLm = 1.5d0*x1*(11.d0 - 15.d0*x2)
         if (L.eq.3 .and. m.eq.1) pLm = 1.5d0*y1*(11.d0 - 45.d0*x2)
         if (L.eq.3 .and. m.eq.2) pLm = 15.d0*x1*(9.d0*x2 - 7.d0)
         if (L.eq.3 .and. m.eq.3) pLm = 45.d0*y1*(3.d0*x2 - 1.d0)
         if (L.eq.4 .and. m.eq.0) pLm = 2.5d0*(-28.d0*x4
     +                                        + 27.d0*x2 - 3.d0)
         if (L.eq.4 .and. m.eq.1) pLm = 5.d0*x1*y1*(27.d0 - 56.d0*x2)
         if (L.eq.4 .and. m.eq.2) pLm = 30.d0*(28.d0*x4
     +                                       - 29.d0*x2 + 4.d0)
         if (L.eq.4 .and. m.eq.3) pLm = 210.d0*(8.d0*x2 - 5.d0)
         if (L.eq.4 .and. m.eq.4) pLm = 420.d0*y2*(4.d0*x2 - 1.d0)
c
      endif
c
      spharm = cnr*pLm
c
      return
      end
c
