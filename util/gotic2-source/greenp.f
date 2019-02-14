c$greenp
c------------------------------------------------------------------
      subroutine greenp (angp , grnp , ind)
c------------------------------------------------------------------
c
      implicit double precision (a-h,o-z)
c
      common /gfile/ ang(50), grn(50,6), cgrn(50,2,3), igrn, idelta
c
      parameter (n = 50)
      parameter (m = n - 1)
      dimension x(3), y(3)
c
c     GREENP COMPUTES THE GREEN'S FUNCTION AT ANGULAR DISTANCE ANGP.
c
c     INPUT PARAMETERS:
c             ANGP             :  ANGULAR DISTANCE FROM THE OBSERVATION
c                                 FROM THE OBSERVATION POINT TO THE
c                                 POINT MASS LOAD (UNIT IN RADIAN).
c
c             IND              :  INDEX OF THE COMPONENT OF THE GREEN'S
c                                 FUNCTIONS.
c                                 1 : RADIAL DISPLACEMENT
c                                 2 : TANGENTIAL DISPLACEMENT
c                                 3 : GRAVITY
c                                 4 : TILT
c                                 5 : STRAIN
c
c       OUTPUT PARAMETERS:
c
c             GRNP             :  GREEN'S FUNCTION AT ANGULAR DISTANCE
c                                 ANGP.
      i = 1
c
      if (angp.lt.ang(i)) then
c     
         print*,'!!! Error : <angp> is out of range in ',
     +          'subroutine <greenp>'
         return
c
      else if (angp.eq.ang(i)) then
c
         grnp = grn(i,ind)
         return
c
      endif
c
      i = 2
c
      do while ( (angp.gt.ang(i)) .and. (i.lt.n) )
         i = i + 1
      enddo
c
      if (angp.eq.ang(i)) then
c
         grnp = grn(i,ind)
         return
c
      else if (i.eq.n) then
c
         if (angp.gt.ang(i)) then
            print*,'!!! Error : <angp> is out of range in ',
     +             'subroutine <greenp>'
            return
         else
            i = m
         endif
c         
      endif
c
      do j = 1,3
         x(j) = ang(i + j - 2)
         y(j) = grn(i + j - 2, ind)
      enddo
c
      call quadr (x, y, angp, grnp, a, b, c)
c
      return
      end
c
