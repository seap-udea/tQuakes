c$factl
c------------------------------------------------------------------
      double precision function factl(m)
c------------------------------------------------------------------
c
c     FUNCTION SUB. ROUTINE TO COMPUTE FACTORIAL OF M
c
      implicit double precision (a-h,o-z)
c
      if (m.eq.0) then
c
         factl = 1.d0
c
      else
c
         f = 1.d0
c
         do i = 1,m
            f = f*dfloat(i)
         enddo
c
         factl = f
c
      endif
c
      return
      end
c
