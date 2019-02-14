c$banner
c----------------------------------------------------------------
      subroutine banner(ivery,iverm,iverd)
c----------------------------------------------------------------
c
      implicit double precision (a-h,o-z)
c
      write(6,101)
      write(6,102)
      write(6,103)ivery,iverm,iverd
      write(6,101)
      write(6,104)
c
 101  format('********************************************************')
 102  format('******************       GOTIC2       ******************')
 103  format('****************** Version ' ,i4,'.',i2.2,'.',i2.2,
     +       ' ******************')
 104  format(' ')
c
      return
      end
