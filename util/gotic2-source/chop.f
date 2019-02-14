c$chop
c----------------------------------------------------------------
      subroutine chop(buf, ic)
c----------------------------------------------------------------
c
      character*80 buf
c
      do i = 80,1,-1
         if (buf(i:i).ne.' ') then
            ic = i
            goto 9
         endif
      enddo
c
 9    return
      end
c
