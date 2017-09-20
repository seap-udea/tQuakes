c$csearc
c----------------------------------------------------------------
      subroutine csearc(buf, ckey, Lkey)
c----------------------------------------------------------------
c
      Logical Lkey
c
      character*120 buf
      character*80  ckey
c
      Lkey = .false.
c
      call chop(ckey,ic)
c
      do i = 1,120
         if (buf(i:i+ic-1).eq.ckey(1:ic)) then
            Lkey = .true.
            return
         endif
      enddo
c
      return
      end
c
