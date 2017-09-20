c$gmodel
c---------------------------------------------------------------
      subroutine gmodel(tm1   , tm2   , xmin  , ymax  , gsize ,
     +                  ampj  , phsj  , mgmax , ngmax , mend  ,
     +                  nend                                   )
c---------------------------------------------------------------
c
      implicit double precision (a-h,o-z)
c
      Logical Lmapout, Lmesh1, Lmesh2 , Lmesh3, Lmesh4, Lpoint, Lmascor
      Logical Latan2 , Lverbo, Lpred  , Lprein
      Logical Lhavej , Loutj , Lfullm , Lmapln
c
      common /const/  rearth, earthm, gravct, pi , rad, deg,
     +                dens  , rls1  , rls2  , egv, elp
      common /flag/   Lmapout, Lmesh1, Lmesh2, Lmesh3, Lmesh4, Lpoint,
     +                Lmascor, Latan2, Lverbo, Lpred , Lprein, Lhavej,
     +                Loutj  , Lmapln, Lfullm
      common /gotd/   oamp(721,361), ophs(721,361)
      common /jmap/   xminj, xmaxj, yminj, ymaxj, gsizej, mendj, nendj
c
      parameter (mmax = 721, nmax = 542)
      parameter (xminj0  = 110.d0, xmaxj0 = 165.d0)
      parameter (yminj0  =  20.d0, ymaxj0 =  65.d0)
      parameter (gsizej0 =  1.d0/12.d0)
c
      dimension amp0(mmax ,nmax ), phs0(mmax ,nmax )
      dimension ampj(mgmax,ngmax), phsj(mgmax,ngmax)
c
      character*80 tm1, tm2
      character    fmt*6, wave*2, name*50, date*50
c
      data iunt10 /10/
c
c
c
      if (Lverbo) then
         write(6,6006)
 6006    format('   ---------------< Ocean tide model information >',
     +          '---------------')
      endif
c
      if (tm2.ne.' ') then
         Lhavej = .true.
      else
         Lhavej = .false.
      endif
c
      smass = 0.d0
      cmass = 0.d0
      area  = 0.d0
c
      do n = 1,361
         do m = 1,721
            oamp(m,n) =   9.999d0
            ophs(m,n) = 999.999d0
         enddo
      enddo
c
      do n = 1,ngmax
         do m = 1,mgmax
            ampj(m,n) =   9.999d0
            phsj(m,n) = 999.999d0
         enddo
      enddo
c
      if (.not.Lhavej) then
         xminj  = xminj0
         xmaxj  = xmaxj0
         yminj  = yminj0
         ymaxj  = ymaxj0
         gsizej = gsizej0
      endif
c
c -----< Read local ocean tide model >-----
c
      if ( Lhavej ) then
c
         iocean = 0
         iland  = 0
c
         if (Lverbo) then
            write(6,6001) tm2
 6001       format('   Local ocean tide model file : ',a80)
         endif
c
         open(iunt10,file=tm2,status='old',err=901)
c     
         call rdhead(iunt10, name  , wave  , date  , xminj ,
     +               xmaxj , yminj , ymaxj , dxj   , dyj   ,
     +               mendj , nendj , ideff , fmt   , aunit ,
     +               punit                                  )
c
         if (Lverbo) then
            write(6,6002) name
 6002       format('     Model name   = ',a50)
            write(6,6003) date
 6003       format('     Created date = ',a50)
            write(6,101) xminj, xmaxj, yminj, ymaxj
            write(6,102) dxj, dyj, mendj, nendj
            write(6,103) aunit, punit
         endif
c
 101     format(5x,'xmin = ',f6.2,', xmax = ',f6.2,', ymin = ',f6.2,
     +             ', ymax = ',f6.2)
 102     format(5x,'dx   = ',f6.3,', dy =   ',f6.3,', mend = ',i4,
     +             '  , nend = ',i4)
 103     format(5x,'amplitude unit = ',f6.3,', phase unit =  ',f6.3)
c
         undef  = dfloat(ideff)*aunit
         gsizej = dxj
         yleng  = 2.d0*dsin(0.5d0*dyj*rad)
c
         do n = 1, nendj
            do m = 1, mendj
               amp0(m,n) = undef
               phs0(m,n) = undef
            enddo
         enddo
c     
         call rdcmp(iunt10, amp0  , phs0  , mendj  , nendj  ,
     +              mmax  , nmax  , fmt   , aunit  , punit   )
c
         do n = 1,nendj
            do m = 1,mendj
c
               if (amp0(m,n).ge.undef-0.1d0) then
c
                  iland = iland + 1
c
                  ampj(m,n) =   9.999d0
                  phsj(m,n) = 999.999d0
c
               else
c
                  iocean    = iocean + 1
c
                  ampj(m,n) = amp0(m,n)*1.d-2 ! in meter
                  phsj(m,n) = phs0(m,n)       ! in degree
c     
                  x = xminj + (dfloat(m)-1.d0)*dxj
                  y = ymaxj - (dfloat(n)-1.d0)*dyj
c     
                  xleng = 2.d0*dsin(0.5d0*dxj*rad*dcos(y*rad))
                  area0 = dabs(xleng*yleng)
                  area  = area + area0
                  cmass = cmass + ampj(m,n)*dcos(phsj(m,n)*rad)*area0
                  smass = smass + ampj(m,n)*dsin(phsj(m,n)*rad)*area0
c
               endif            ! Land or ocean
c
            enddo
         enddo
c
         if (Lverbo) then
            write(6,6004) iocean
 6004       format('     Number of ocean grids = ',i8)
            write(6,6005) iland
 6005       format('     Number of land  grids = ',i8)
         endif
c
         close (iunt10)
c
      endif                     ! (Short-period and NAO model) or not
c
c ---< Read global ocean tide model >-----
c
      iocean = 0
      iland  = 0
c
      if (Lverbo) then
         write(6,6007)
 6007    format(' ')
         write(6,6008) tm1
 6008    format('   Global ocean tide model file : ',a80)
      endif
c
      open(iunt10,file=tm1,status='old',err=902)
c
      call rdhead(iunt10, name  , wave  , date  , xmin  ,
     +            xmax  , ymin  , ymax  , dx    , dy    ,
     +            mend  , nend  , ideff , fmt   , aunit ,
     +            punit                                  )
c
      if (Lverbo) then
         write(6,6002) name
         write(6,6003) date
         write(6,101) xmin, xmax, ymin, ymax
         write(6,102) dx, dy, mend, nend
         write(6,103) aunit, punit
      endif
c
      undef = dfloat(ideff)*aunit
      gsize = dx
      yleng = 2.d0*dsin(0.5d0*dy*rad)
c
      do n = 1,nend
         do m = 1,mend
            amp0(m,n) = undef
            phs0(m,n) = undef
         enddo
      enddo
c
      call rdcmp(iunt10, amp0  , phs0  , mend  , nend  ,
     +           mmax  , nmax  , fmt   , aunit , punit  )
c
      do n = 1,nend
         do m = 1,mend
c
            if (amp0(m,n).ge.undef-0.1d0) then
c
               iland     = iland + 1
               oamp(m,n) =   9.999d0
               ophs(m,n) = 999.999d0
c
            else
c
               iocean = iocean + 1
c
               oamp(m,n) = amp0(m,n)*1.d-2 ! in meter
               ophs(m,n) = phs0(m,n)       ! in degree
c
               x = xmin + (dfloat(m-1))*dx
               y = ymax - (dfloat(n-1))*dy
c
               if ( (x.lt.xminj).or.(x.gt.xmaxj).or.
     +              (y.lt.yminj).or.(y.gt.ymaxj)    ) then
                  Loutj = .true.
               else
                  Loutj = .false.
               endif
c
               if ( (.not.Lhavej) .or. (Lhavej .and. Loutj) ) then
c
                  xleng = 2.d0*dsin(0.5d0*dx*rad*dcos(y*rad))
                  area0 = dabs(xleng*yleng)
                  area  = area + area0
                  cmass = cmass + oamp(m,n)*dcos(ophs(m,n)*rad)*area0
                  smass = smass + oamp(m,n)*dsin(ophs(m,n)*rad)*area0
c
               endif
c
            endif               ! Land or ocean
c
         enddo
      enddo
c
      if (Lverbo) then
         write(6,6004) iocean
         write(6,6005) iland
      endif
c
      close (iunt10)
c
c -----< Mass conservation >-----
c
      if (Lmascor) then
c
         ccorr = cmass/area
         scorr = smass/area
         acorr = dsqrt(ccorr*ccorr+scorr*scorr)
         pcorr = datan2(scorr,ccorr)/rad
         opert = area/(4.d0*pi)*100.d0
c
         if (Lverbo) then
            write(6,*) ' '
            write(6,*) '  Unconserved mass information'
            write(6,*) '  Total area of ocean meshes (rad)   =', area
            write(6,*) '  Ocean percentage : total/(4pi)*100 =', opert
            write(6,*) '  Real part of unconserved mass (m)  =', ccorr
            write(6,*) '  Imag part of unconserved mass (m)  =', scorr
            write(6,*) '  Amplitude (m)                      =', acorr
            write(6,*) '  Phase  (deg)                       =', pcorr
            write(6,*) ' '
         endif
c
         if ( Lhavej ) then
c
            do n = 1,nendj
               do m = 1,mendj
c
                  a = ampj(m,n)
                  p = phsj(m,n)*rad
c
                  if (a.lt.9.998d0) then
c
                     ac = a*dcos(p) - ccorr
                     as = a*dsin(p) - scorr
                     ampj(m,n) = dsqrt(ac*ac + as*as)
                     phsj(m,n) = datan2(as,ac)/rad
c
                  endif
c
               enddo
            enddo
c
         endif                  ! Have regional model or not.
c
         do n = 1,nend
            do m = 1,mend
c
               a = oamp(m,n)
               p = ophs(m,n)*rad
c
               if (a.lt.9.998d0) then
c
                  ac = a*dcos(p) - ccorr
                  as = a*dsin(p) - scorr
                  oamp(m,n) = dsqrt(ac*ac + as*as)
                  ophs(m,n) = datan2(as,ac)/rad
c
               endif
c
            enddo
         enddo
c
      endif
c
c -----< Make 0.5deg local map from 5min map >-----
c
      if ( Lhavej ) then
c
         mgmax5 = mgmax/6
         ngmax5 = ngmax/6
c
         do n = 1,ngmax5
            do m = 1,mgmax5
c     
               sumc = 0.d0
               sums = 0.d0
               ndat = 0
c
               do iy = 1,6
                  nn = (n-1)*6 + iy
c
                  do ix = 1,6
                     mm = (m-1)*6 + ix
c
                     a = ampj(mm,nn)
                     p = phsj(mm,nn)*rad
c
                     if (a.lt.9.998d0) then
                        sumc = sumc + a*dcos(p)
                        sums = sums + a*dsin(p)
                        ndat = ndat + 1
                     endif
c     
                  enddo         ! ix
               enddo            ! iy
c     
               x     = xminj + (dfloat(m) - 0.5d0)*dx
               y     = ymaxj - (dfloat(n) - 0.5d0)*dy
               m5    = (x - xmin)/dx + 1.d0
               n5    = (ymax - y)/dy + 1.d0
c     
               if (ndat.gt.0) then
c
                  sumc  = sumc/dfloat(ndat)
                  sums  = sums/dfloat(ndat)
                  ampj5 = dsqrt(sumc*sumc + sums*sums)
                  phsj5 = datan2(sums,sumc)/rad
c
               else
c     
                  ampj5 =   9.999d0
                  phsj5 = 999.999d0
c
               endif
c
               oamp(m5,n5) = ampj5
               ophs(m5,n5) = phsj5
c
            enddo               ! m
         enddo                  ! n
c
      endif
c
      if (Lverbo) then
         write(6,6009)
 6009    format('   ----------------------------------------',
     +          '----------------------')
         write(6,6007)
      endif
c
      return
c
 901    print*,'!!! Error in opening the file : ',tm2
        print*,'!!! Stop at souboutine <gmodel>'
        stop
c
 902    print*,'!!! Error in opening the file : ',tm1
        print*,'!!! Stop at souboutine <gmodel>'
        stop
c
      end
c
