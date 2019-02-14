c$rd1st
c------------------------------------------------------------------
      subroutine rd1st(cmesh1, fmap1, mendcm, nendcm)
c------------------------------------------------------------------
c
      implicit double precision (a-h,o-z)
c
      character*720 cbuf
      character*1  cmesh1(mendcm,nendcm)
      character*80 fmap1
c
      do n = 1,nendcm
         do m = 1,mendcm
            cmesh1(m,n) = '#'
         enddo
      enddo
c
      open(30,file=fmap1,status='old',err=901)
c
      do n1 = 1,nendcm
         read(30,'(a720)') cbuf
         do m1 = 1,mendcm
            cmesh1(m1,n1) = cbuf(m1:m1)
         enddo
      enddo
c
      close(30)
c
      return
c
 901  print*,'!!! Error in opening the file : ',fmap1
      print*,'!!! Stop at souboutine <rd1st>'
      stop
c
      end




