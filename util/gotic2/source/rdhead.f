c$rdhead
c----------------------------------------------------------------
      subroutine rdhead(iu    , name  , wave  , date  , xmin  ,
     +                  xmax  , ymin  , ymax  , dx    , dy    ,
     +                  mend  , nend  , ideff , fmt   , aunit ,
     +                  punit                                  )
c----------------------------------------------------------------
c
      implicit double precision (a-h,o-z)
c
      character fmt*6, wave*2, name*50, date*50, buf*50
      character cdx*8, cdy*8
c
      read(iu,'(13x,a50)') name
      read(iu,'(13x,a2 )') wave
      read(iu,'(13x,f5.3,19x,f4.2)') aunit,punit
      read(iu,'(13x,a50)') date
      read(iu,'(7x,f7.2,3(9x,f7.2))') xmin,xmax,ymin,ymax
      read(iu,'(6x,a8,8x,a8,2(9x,i7))') cdx,cdy,mend,nend
      read(iu,'(16x,i6,11x,a6)') ideff, fmt
c
      if (cdx(3:3).eq.'/') then
         read(cdx,'(6x,i2)') idx
         read(cdy,'(6x,i2)') idy
         dx = 1.d0/dfloat(idx)
         dy = 1.d0/dfloat(idy)
      else
         read(cdx,'(f8.2)')dx
         read(cdy,'(f8.2)')dy
      endif
c
      return
      end
c
