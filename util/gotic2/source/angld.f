c$angld
c------------------------------------------------------------------
      subroutine angld (alat  , alon  , blat  , blon  , angr)
c------------------------------------------------------------------
c
      implicit double precision (a-h,o-z)
c
      tmp = dsin(alat)*dsin(blat)
     +    + dcos(alat)*dcos(blat)*dcos(alon - blon)
c
      if (tmp.gt. 1.d0) tmp =  1.d0
      if (tmp.lt.-1.d0) tmp = -1.d0
c
      angr = dacos(tmp)
c
      return
      end
c
