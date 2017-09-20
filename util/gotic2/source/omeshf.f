c$omeshf
c---------------------------------------------------------------
      subroutine omeshf(iunit , datdir, m1    , n1    )
c---------------------------------------------------------------
c
      character*3   c3m, c3n
      character*80  datdir, fmesh1
c
      if (m1.lt.10) then
         write(c3m,101) m1
 101     format('00',i1)
      else if (m1.lt.100) then
         write(c3m,102) m1
 102     format('0',i2)
      else
         write(c3m,'(i3)') m1
      endif
c
      if (n1.lt.10) then
         write(c3n,101) n1
      else if (n1.lt.100) then
         write(c3n,102) n1
      else
         write(c3n,'(i3)') n1
      endif
c 
      call chop(datdir, ic)
      if (datdir(ic:ic).ne.'/') then
         ic = ic + 1
         datdir(ic:ic) = '/'
      endif
c
      fmesh1 = datdir(1:ic)//'mesh/'//c3m//c3n//'.mesh'
c
      open(iunit,file=fmesh1,status='old',err=901)
c
      return
c
 901  print*,'!!! Error in opening the file : ',fmesh1
      print*,'!!! Stop at souboutine <omeshf>'
      stop
c
      end
c
