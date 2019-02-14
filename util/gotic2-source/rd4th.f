c$rd4th
c------------------------------------------------------------------
      subroutine rd4th(iu, cmesh4, m2, n2, m3, n3, ndx4, ndy4)
c------------------------------------------------------------------
c
      implicit double precision (a-h,o-z)
c
      dimension cmesh4(20,20), cbuf(400)
      character*1 cmesh4, cbuf
c
 10   read(iu,101,end=901) iar,mm1,nn1,mm2,nn2,mm3,nn3,
     +                     (cbuf(i),i=1,200),(cbuf(i),i=201,400)
 101  format(i1,2i3,2i1,2i2,200a1,200a1)
c     
      if ( (m2.ne.mm2).or.(n2.ne.nn2).or.
     +     (m3.ne.mm3).or.(n3.ne.nn3)    ) goto 10
c     
      do n4 = 1,ndy4
         do m4 = 1,ndx4
            ipos = (n4-1)*ndx4 + m4
            cmesh4(m4,n4) = cbuf(ipos)
         enddo
      enddo
c
      return
c
 901  print*,'!!! Error in reading 4rd-order mesh.'
      print*,'!!! End of file detected.'
      print*,'!!! Stop at souboutine <rd4th>'
c
      stop
c       
      end
c

