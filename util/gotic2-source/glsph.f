c$glsph
c------------------------------------------------------------
      double precision function glsph(cl , m , id)
c------------------------------------------------------------
c
c     FUNCTION SUBROUTINE TO COMPUTE GENERALIZED SPHERICAL HARMONICS
c     FUNCTION BELOW 4TH DEGREE
c
      implicit double precision (a-h,o-z)
c
      c1 = dcos(cl)
      c2 = c1*c1
      c4 = c2*c2
c
      if (m.eq.0) then
c
         if (id.eq.1) then
            a1    = 3.d0/(4.d0*dsqrt(5.d0))
            a2    = 35.d0*c4 - 30.d0*c2 + 3.d0
            a3    = 1.d0 - 3.d0*c2 !!
            glsph = a1*a2/a3
         else if (id.eq.2) then
            a1    = 2.d0/dsqrt(5.d0)
            a2    = 1.d0
            a3    = 1.d0 - 3.d0*c2 !!
            glsph = a1*a2/a3
         endif
c
      else if (m.eq.1) then
c
         a1    = dsqrt(3.d0)/(2.d0*dsqrt(2.d0))
         a2    = 7.d0*c2 - 3.d0
         glsph = a1*a2
c
      else if (m.eq.2) then
c
         a1    = dsqrt(3.d0)/2.d0
         a2    = 7.d0*c2 - 1.d0
         glsph = a1*a2
c
      endif
c
      return
      end
c
