c$rdprein
c----------------------------------------------------------------
      subroutine rdprein(iu, ikind)
c----------------------------------------------------------------
c
      implicit double precision (a-h,o-z)
c
      Logical Lpr186, Lkey
c
      common /amphs/  amps(5,6,6,10,21), phsg(5,6,6,10,21),
     +                phsl(5,6,6,10,21),
     +                ampa(5,10,21), phsa(5,10,21),
     +                ampe(5,10,21), phse(5,10,21),
     +                ampst(6,6,10,21), ampot(6,6,10,21),
     +                ampt (6,6,10,21), phsea(6,6,10,21),
     +                phsoa(6,6,10,21), phsta(6,6,10,21),
     +                phser(6,6,10,21), phsor(6,6,10,21),
     +                phstr(6,6,10,21)
      common /name/   sname(10)
      common /predr/  prsmjd, premjd, prdt, prein
      common /predi/  iprfm1, iprfm2, iprcmp, Lpr186
c
      character*10  sname, site
      character*80  prein, ckey
      character*120 buf
c
      dimension ikind(6)
c
c-----------------------------------------------------------------------
c
      k = ikind(1)
c
      do nc = 1,6
         do iw = 1,21
            ampst(k,nc,1,iw) = 0.d0
            phsea(k,nc,1,iw) = 0.d0
            ampot(k,nc,1,iw) = 0.d0
            phsoa(k,nc,1,iw) = 0.d0
            ampt (k,nc,1,iw) = 0.d0
            phsta(k,nc,1,iw) = 0.d0
         enddo
      enddo
c
      open(iu,file=prein,status='old',err=901)
c
c---------------------------------------------------------
c
 10   read(iu,'(a120)',end=999) buf
c
c -----< Radial displacement info >-----
c
      ckey = '= Radial d'
      call csearc(buf,ckey,Lkey)
c
      if (Lkey .and. k.eq.1) then
c
         Lkey = .false.
         ckey = 'Station'
         do while (.not.Lkey)
            read(iu,'(a120)') buf
            call csearc(buf,ckey,Lkey)
         enddo
c
         if (buf(1:1).eq.' ') then
            read(buf,'(15x,a10)') site
         else
            read(buf,'(14x,a10)') site ! For WINDOWS
         endif
         if (site.ne.sname(1)) goto 10
c
         Lkey = .false.
         ckey = 'Amplitude  A-phase  R-phase'
         do while (.not.Lkey)
            read(iu,'(a120)') buf
            call csearc(buf,ckey,Lkey)
         enddo
c
         read(iu,'(a120)') buf
         read(iu,'(a120)') buf
         call setap(iu,1,1,1)
c
      endif
c
c -----< Tangential displacement info >-----
c
      ckey = '= Tangential d'
      call csearc(buf,ckey,Lkey)
c
      if (Lkey .and. k.eq.2) then
c
         Lkey = .false.
         ckey = 'Station' 
         do while (.not.Lkey)
            read(iu,'(a120)') buf
            call csearc(buf,ckey,Lkey)
         enddo
c
         if (buf(1:1).eq.' ') then
            read(buf,'(15x,a10)') site
         else
            read(buf,'(14x,a10)') site ! For WINDOWS
         endif
         if (site.ne.sname(1)) goto 10
c
         Lkey = .false.
         ckey = 'Amplitude  A-phase  R-phase'
         do while (.not.Lkey)
            read(iu,'(a120)') buf
            call csearc(buf,ckey,Lkey)
         enddo
c
         read(iu,'(a120)') buf
         read(iu,'(a120)') buf
         call setap(iu,2,1,1)
         read(iu,'(a120)') buf
         call setap(iu,2,2,1)
         read(iu,'(a120)') buf
         call setap(iu,2,3,1)
c
      endif
c
c -----< Gravity info >-----
c
      ckey = '= Gravity =' 
      call csearc(buf,ckey,Lkey)
c
      if (Lkey .and. k.eq.3) then
c
         Lkey = .false.
         ckey = 'Station'
         do while (.not.Lkey)
            read(iu,'(a120)') buf
            call csearc(buf,ckey,Lkey)
         enddo
c
         if (buf(1:1).eq.' ') then
            read(buf,'(15x,a10)') site
         else
            read(buf,'(14x,a10)') site ! For WINDOWS
         endif
         if (site.ne.sname(1)) goto 10
c
         Lkey = .false.
         ckey = 'Amplitude  A-phase  R-phase'
         do while (.not.Lkey)
            read(iu,'(a120)') buf
            call csearc(buf,ckey,Lkey)
         enddo
c
         read(iu,'(a120)') buf
         read(iu,'(a120)') buf
         call setap(iu,3,1,1)
c
      endif
c
c -----< Tilt info >-----
c
      ckey = '= Tilt ='
      call csearc(buf,ckey,Lkey)
c
      if (Lkey .and. k.eq.4) then
c
         Lkey = .false.
         ckey = 'Station' 
         do while (.not.Lkey)
            read(iu,'(a120)') buf
            call csearc(buf,ckey,Lkey)
         enddo
c
         if (buf(1:1).eq.' ') then
            read(buf,'(15x,a10)') site
         else
            read(buf,'(14x,a10)') site ! For WINDOWS
         endif
         if (site.ne.sname(1)) goto 10
c
         Lkey = .false.
         ckey = 'Amplitude  A-phase  R-phase'
         do while (.not.Lkey)
            read(iu,'(a120)') buf
            call csearc(buf,ckey,Lkey)
         enddo
c
         read(iu,'(a120)') buf
         read(iu,'(a120)') buf
         call setap(iu,4,1,1)
         read(iu,'(a120)') buf
         call setap(iu,4,2,1)
         read(iu,'(a120)') buf
         call setap(iu,4,3,1)
c
      endif
c
c -----< Strain info >-----
c
      ckey = '= Strain ='
      call csearc(buf,ckey,Lkey)
c
      if (Lkey .and. k.eq.5) then
c
         Lkey = .false.
         ckey = 'Station' 
         do while (.not.Lkey)
            read(iu,'(a120)') buf
            call csearc(buf,ckey,Lkey)
         enddo
c
         if (buf(1:1).eq.' ') then
            read(buf,'(15x,a10)') site
         else
            read(buf,'(14x,a10)') site ! For WINDOWS
         endif
         if (site.ne.sname(1)) goto 10
c
         Lkey = .false.
         ckey = 'Amplitude  A-phase  R-phase'
         do while (.not.Lkey)
            read(iu,'(a120)') buf
            call csearc(buf,ckey,Lkey)
         enddo
c
         read(iu,'(a120)') buf
         read(iu,'(a120)') buf
         call setap(iu,5,1,1)
         read(iu,'(a120)') buf
         call setap(iu,5,2,1)
         read(iu,'(a120)') buf
         call setap(iu,5,3,1)
         read(iu,'(a120)') buf
         call setap(iu,5,4,1)
         read(iu,'(a120)') buf
         call setap(iu,5,5,1)
         read(iu,'(a120)') buf
         call setap(iu,5,6,1)
c
      endif
c
c -----< Deflection of the vertical info >-----
c
      ckey = '= Deflection o'
      call csearc(buf,ckey,Lkey)
c
      if (Lkey .and. k.eq.6) then
c
         Lkey = .false.
         ckey = 'Station' 
         do while (.not.Lkey)
            read(iu,'(a120)') buf
            call csearc(buf,ckey,Lkey)
         enddo
c
         if (buf(1:1).eq.' ') then
            read(buf,'(15x,a10)') site
         else
            read(buf,'(14x,a10)') site ! For WINDOWS
         endif
         if (site.ne.sname(1)) goto 10
c
         Lkey = .false.
         ckey = 'Amplitude  A-phase  R-phase'
         do while (.not.Lkey)
            read(iu,'(a120)') buf
            call csearc(buf,ckey,Lkey)
         enddo
c
         read(iu,'(a120)') buf
         read(iu,'(a120)') buf
         call setap(iu,6,1,1)
         read(iu,'(a120)') buf
         call setap(iu,6,2,1)
c
      endif
c
      goto 10
c
 901  print*,'!!! Error in opening the file : ',prein
      print*,'!!! Stop at souboutine <rdprein>'
      stop
c
 999  return
      end
c





