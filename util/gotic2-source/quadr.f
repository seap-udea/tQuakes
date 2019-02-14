c$quadr
c------------------------------------------------------------------
      subroutine quadr (x , y , xp , yp , a , b , c)
c------------------------------------------------------------------
c
      implicit double precision (a-h,o-z)
c
      dimension x(3), y(3)
c
      xa = x(2) - x(1)
      ya = y(2) - y(1)
      xb = x(3) - x(2)
      yb = y(3) - y(2)
      xc = x(1) - x(3)
c
      xxa = xa*(x(1) + x(2))
      xxb = xb*(x(2) + x(3))
      xya = y(1)*x(2)*x(3)
      xyb = x(1)*y(2)*x(3)
      xyc = x(1)*x(2)*y(3)
      xxc = 1.0d0/(xa*xb*xc)
      a   = -(xa*yb  - xb*ya )*xxc
      b   = -(ya*xxb - yb*xxa)*xxc
      c   = -(xya*xb + xyb*xc + xyc*xa)*xxc
      yp  = xp*(a*xp + b) + c
c
      return
      end
c
