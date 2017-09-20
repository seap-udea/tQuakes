c$greenf
c------------------------------------------------------------------
      subroutine greenf (ang4 , grna , grnb , grnc , ind)
c------------------------------------------------------------------
c
      implicit double precision (a-h, o-z)
c
      common /gfile/ ang(50), grn(50,6), cgrn(50,2,3), igrn, idelta
c
      dimension ang4(4), grnf(3), angf(3), in(3)
c
      call minmax (ang4, 4, amin, amax)
c
      n = 50
c
      if (amax.le.ang(1)) goto 1
c
      do i = 2,n
         if (amax.le.ang(i)) goto 2
      enddo
c
 1    print*,'!!! Error : <amax> is out of range in subroutine <greenf>'
      return
c
 2    in(3) = i
c
      j = n
      do while ( (amin.lt.ang(j)) .and. (j.gt.1) )
         j = j - 1
      enddo
c
 3    in(1) = j
c
      if ( in(3) .eq. in(1) ) then
c
         print*,'!!! Error : <amin> is greater than <amax>',
     +        'in subroutine <greenf>'
         return
c
      elseif ( in(3) .eq. (in(1) + 1) ) then
c
         in(2) = in(3) + 1
c
      else
c
         in(2) = (in(1) + in(3))/2
c
      endif
c
      do i = 1,3
         angf(i) = ang(in(i))
         grnf(i) = grn(in(i),ind)
      enddo
c
      call quadr (angf, grnf, amin, grnp, grnc, grnb, grna)
c
      return
      end
c
