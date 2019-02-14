c$minmax
c------------------------------------------------------------------
      subroutine minmax (x , n , xmin , xmax)
c------------------------------------------------------------------
c
      implicit double precision (a-h, o-z)
c
      dimension x(n)
c
      xmin = x(1)
      xmax = xmin
c
      do i = 2,n
c
         if (x(i).lt.xmin) then
            xmin = x(i)
         endif
c
         if (x(i).gt.xmax) then
            xmax = x(i)
         endif
c
      enddo
c
      return
      end
c
