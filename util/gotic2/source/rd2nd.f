c$rd2nd
c------------------------------------------------------------------
      subroutine rd2nd(iu    , cmesh2, m1    , n1    , ndx2  ,
     +                 ndy2  , ndx3  , ndy3  , ndx4  , ndy4   )
c------------------------------------------------------------------
c
      implicit double precision (a-h,o-z)
c
      dimension cmesh2(6,6), cbuf(36)
      character*1 cmesh2, cbuf
c
      read(iu,'(6i3)')ndx2,ndy2,ndx3,ndy3,ndx4,ndy4
      read(iu,'(i1,2i3,36a1)') iar,mm1,nn1,(cbuf(i),i=1,36)
c
      if ( (m1.ne.mm1).or.(n1.ne.nn1) ) then
         print*,'!!! Error: Illegal 1st-order mesh file.'
         print*,'!!!        m1,n1,mm1,nn1 = ',m1,n1,mm1,nn1
         print*,'!!! Stop at subroutine <rd2nd>'
         stop
      endif
c
      do n2 = 1,ndy2
         do m2 = 1,ndx2
            ipos = (n2-1)*ndx2 + m2
            cmesh2(m2,n2) = cbuf(ipos)
         enddo
      enddo
c
      return
      end
c

