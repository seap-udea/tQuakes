c$earth
c---------------------------------------------------------------
      subroutine earth(iu, grn1, grn2, grn3, grn4, grn5)
c---------------------------------------------------------------
c
c Read Green's functions
c 1998.02.05
c
      implicit double precision (a-h,o-z)
c
      Logical Lmapout, Lmesh1, Lmesh2, Lmesh3, Lmesh4, Lpoint, Lmascor
      Logical Latan2 , Lverbo, Lpred , Lprein
      Logical Lhavej , Loutj , Lfullm , Lmapln
c
      common /const/  rearth, earthm, gravct, pi , rad, deg,
     +                dens  , rls1  , rls2  , egv, elp
      common /flag/   Lmapout, Lmesh1, Lmesh2, Lmesh3, Lmesh4, Lpoint,
     +                Lmascor, Latan2, Lverbo, Lpred , Lprein, Lhavej,
     +                Loutj  , Lmapln, Lfullm
      common /gfile/ ang(50), grn(50,6), cgrn(50,2,3), igrn, idelta
c
      dimension xdeg(50)
c
      character*80 grn1, grn2, grn3, grn4, grn5
c
      if (Lverbo) then
         write(6,6001)
 6001    format('--------------------< Green''s function >',
     +          '--------------------')
      endif
c
      if (igrn.eq.1) then
c
         open(iu,file=grn1,status='old',err=901)
c
         if (Lverbo) then
            write(6,6002)
 6002       format(' ')
            write(6,6003)
 6003       format('***** Elastic Earth model (GB model) *****')
            write(6,6002)
            write(6,6005)
 6005       format(' Ang. dist.      RD           HD           GV',
     +             '           TL           ST           DV')
         endif
c
         do i = 1,50
c
            read(iu,500,end=19) xdeg(i),(grn(i,j),j=1,6)
            write(6,500) xdeg(i),(grn(i,j),j=1,6)
 500        format(f10.4,6(e13.3))
c
         enddo
c
      else if (igrn.eq.2) then
c
         open(iu,file=grn2,status='old',err=902)
c
         if (Lverbo) then
            write(6,6002)
            write(6,6004)
 6004       format('***** Elastic Earth model (1066A model) *****')
            write(6,6002)
            write(6,6005)
         endif
c
         do i = 1,50
c
            read(iu,500,end=19) xdeg(i),(grn(i,j),j=1,6)
c
            if (Lverbo) then
               write(6,500) xdeg(i),(grn(i,j),j=1,6)
            endif
c
         enddo
c
      else if (igrn.eq.3) then
c
         open(iu,file=grn3,status='old',err=903)
c
         if (Lverbo) then
            write(6,6002)
            write(6,6008)
 6008       format('***** Elastic Earth model (PREM model) *****')
            write(6,6002)
            write(6,6009)
 6009       format('  Ang. dist.         RD              HD',
     +             '              GV',
     +             '              TL              ST')
c     +             '              TL              ST              DV')
         endif
c
         do i = 1,50
c
            read(iu,503,end=19) xdeg(i),(grn(i,j),j=1,5)
 503        format(f12.4,5(e16.6))
c
            if (Lverbo) then
               write(6,503) xdeg(i),(grn(i,j),j=1,5)
            endif
c
         enddo
c
      else if (igrn.eq.4) then
c
         open(iu,file=grn4,status='old',err=904)
c
         if (Lverbo) then
            write(6,6002)
            write(6,6006)
 6006       format('***** Inelastic Earth model (1066A + PREM)',
     +             ' [Gravity] *****')
            write(6,6002)
            write(6,6007)
 6007       format(' Ang. Dist.          Semi-diurnal               ',
     +             '      Diurnal                        Zonal')
         endif
c
         do i = 1,50
c
            read(iu,501,end=19) xdeg(i),((cgrn(i,j,k),j=1,2),k=1,3)
c
            if (Lverbo) then
               write(6,502) xdeg(i),((cgrn(i,j,k),j=1,2),k=1,3)
            endif
c
 501        format(f10.4,6(d13.6))
 502        format(f10.4,6(d15.6))
c
         enddo
c
      else if (igrn.eq.5) then
c
         open(iu,file=grn5,status='old',err=905)
c
         if (Lverbo) then
            write(6,6002)
            write(6,6056)
 6056       format('***** Inelastic Earth model (GB + PREM)',
     +             ' [Gravity] *****')
            write(6,6002)
            write(6,6057)
 6057       format(' Ang. Dist.          Semi-diurnal               ',
     +             '      Diurnal                        Zonal')
         endif
c
         read(iu,*)
         read(iu,*)
c
         do i = 1,50
c
            read(iu,551,end=19) xdeg(i),((cgrn(i,j,k),j=1,2),k=1,3)
c
            if (Lverbo) then
               write(6,552) xdeg(i),((cgrn(i,j,k),j=1,2),k=1,3)
            endif
c
 551        format(f10.4,27x,3(d14.5,d13.5))
 552        format(f10.4,6(d15.6))
c
         enddo
c
      else
         print*,'!!! Error : igrn is wrong, igrn = ',igrn
         print*,'!!! Stop in subroutine <earth>'
         stop
      endif
c
 19   continue
c
      do i = 1,50
         ang(i) = xdeg(i)*rad
      enddo
c
      close(iu)
c
      if (Lverbo) then
         write(6,6011)
 6011    format('-------------------------------------------',
     +          '-------------------------------------------')
         write(6,6002)
         write(6,6002)
      endif
c     
      return
c
 901  print*,'!!! Error in opening the file : ',grn1
      print*,'!!! Stop at souboutine <earth>'
      stop
c
 902  print*,'!!! Error in opening the file : ',grn2
      print*,'!!! Stop at souboutine <earth>'
      stop
c
 903  print*,'!!! Error in opening the file : ',grn3
      print*,'!!! Stop at souboutine <earth>'
      stop
c
 904  print*,'!!! Error in opening the file : ',grn4
      print*,'!!! Stop at souboutine <earth>'
      stop
c
 905  print*,'!!! Error in opening the file : ',grn5
      print*,'!!! Stop at souboutine <earth>'
      stop
c
      end
c
