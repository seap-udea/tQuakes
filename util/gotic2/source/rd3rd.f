c$rd3rd
c------------------------------------------------------------------
      subroutine rd3rd(iu, cmesh3, m2, n2, ndx3, ndy3)
c------------------------------------------------------------------
c
      implicit double precision (a-h,o-z)
c
      dimension cmesh3(10,10), cbuf(100)
      character*1 cmesh3, cbuf
c
c
 10   read(iu,101,end=901) iar,mm1,nn1,mm2,nn2,(cbuf(i),i=1,100)
 101  format(i1,2i3,2i1,100a1)
c
      if ( (m2.ne.mm2).or.(n2.ne.nn2) ) goto 10
c     
      do n3 = 1,ndy3
         do m3 = 1,ndx3
            ipos = (n3-1)*ndx3 + m3
            cmesh3(m3,n3) = cbuf(ipos)
         enddo
      enddo
c     
      return
c
 901  print*,'!!! Error in reading 3rd-order mesh.'
      print*,'!!! End of file detected.'
      print*,'!!! Stop at souboutine <rd3rd>'
c
      stop
c       
      end
c

