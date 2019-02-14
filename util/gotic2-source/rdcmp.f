c$rdcmp
c----------------------------------------------------------------
      subroutine rdcmp(iu    , amp   , phs   , mend  , nend  ,
     +                 mmax  , nmax  , fmt   , aunit , punit  )
c----------------------------------------------------------------
c
      implicit double precision (a-h,o-z)
c
      parameter (kc = 10)
c
      dimension amp(mmax,nmax), phs(mmax,nmax)
      dimension iamp(mmax)    , iphs(mmax)
      character fmt*6
c
c -----< Reading loop >-----
c
      kend = mend/kc
      krem = mod(mend,kc)
c
      do n = 1,nend
c
         do k = 1,kend
c
            m1 = (k-1)*kc + 1
            m2 = m1 + kc - 1
            read(iu,fmt) (iamp(m),m=m1,m2)
c
         enddo
c
         if (krem.ne.0) then
c
            m1 = kend*kc + 1
            m2 = kend*kc + krem
            read(iu,fmt) (iamp(m),m=m1,m2)
c
         endif
c
         do k = 1,kend
c
            m1 = (k-1)*kc + 1
            m2 = m1 + kc - 1
            read(iu,fmt) (iphs(m),m=m1,m2)
c
         enddo
c
         if (krem.ne.0) then
c
            m1 = kend*kc + 1
            m2 = kend*kc + krem
            read(iu,fmt) (iphs(m),m=m1,m2)
c
         endif
c
         do m = 1,mend
c
            amp(m,n) = dfloat(iamp(m))*aunit  ! in centimeters
            phs(m,n) = dfloat(iphs(m))*punit  ! in degrees
c
         enddo
c
      enddo
c
      close(iu)
c
      return
      end
c
