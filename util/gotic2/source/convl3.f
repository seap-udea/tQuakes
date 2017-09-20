c$convl3
c------------------------------------------------------------------
      subroutine convl3(istat , kind  , mgmax , ngmax , ampj  ,
     +                  phsj  , x2    , y2    , m2    , n2    ,
     +                  cmesh3, dx2   , dy2   , ndx3  , ndy3  ,
     +                  ndx4  , ndy4  , gsize , xmin  , ymax  ,
     +                  mend  , nend                           )
c------------------------------------------------------------------
c
c     CONVOLUTION INTEGRAL WITH THIRD ORDER MESH
c
      implicit double precision (a-h,o-z)
c
      Logical Lmapout, Lmesh1, Lmesh2 , Lmesh3, Lmesh4, Lpoint, Lmascor
      Logical Latan2 , Lfirst, Lvryfst, Lminfo, Lverbo, Lpred , Lprein
      Logical Lhavej , Loutj , Lfullm , Lmapln
      Logical Lc3    , Lc4
c
      common /areas/  area1, area2, abnd12, abnd23, abnd34
      common /comp/   ncomp(6)
      common /const/  rearth, earthm, gravct, pi , rad, deg,
     +                dens  , rls1  , rls2  , egv, elp
      common /flag/   Lmapout, Lmesh1, Lmesh2, Lmesh3, Lmesh4, Lpoint,
     +                Lmascor, Latan2, Lverbo, Lpred , Lprein, Lhavej,
     +                Loutj  , Lmapln, Lfullm
      common /jmap/   xminj, xmaxj, yminj, ymaxj, gsizej, mendj, nendj
      common /nodupl/ Lfirst, Lvryfst, Lminfo
      common /meshi/  nd2nd , nd3rd , nd4th , nintg1, nintg2, nintg3,
     +                nintg4, land1 , land2 , land3 , land4 , nd3rdj
      common /meshr/  adist , olnm  , oltm
      common /pgrd/   xb1, xb2, yb1, yb2
      common /stat99/ slat(10,3), slon(10,3),
     +                altd(10), azmth(10), slt(10), sln(10)
      common /sums/   sum(5,2,6), suma(5,2), sume(5,2)
c
      character*1  c3, cmesh3, cmesh4
c
      dimension ampj(mgmax,ngmax), phsj(mgmax,ngmax)
      dimension cov(2,6)
      dimension cmesh3(10,10), cmesh4(20,20)
c
      data ndx3dv, ndy3dv /10,10/
c
c -----< Initialize parameters >-----
c
      if (ndx3.eq.0) then
         ndx3 = ndx3dv
         ndy3 = ndy3dv
      endif
c
      ncmp   = ncomp(kind)
      rln    = sln(istat)*rad
      rlt    = slt(istat)*rad
      alt    = altd(istat)
      azm    = azmth(istat)
c
      dx3    = dx2/dfloat(ndx3)
      dy3    = dy2/dfloat(ndy3)
      wlt    = dx3*rad
      wln    = dy3*rad
      halfx3 = 0.5d0*dx3
      halfy3 = 0.5d0*dy3
c
      x2w = x2 - 0.5d0*dx2
      y2n = y2 + 0.5d0*dy2
c
      do n3 = 1,ndy3
c
         y3 = y2n - (dfloat(n3)-0.5d0)*dy3
         olt = y3*rad
c
         do m3 = 1,ndx3
c
            Lc3 = .true.
            c3  = cmesh3(m3,n3)
c
            x3  = x2w + (dfloat(m3)-0.5d0)*dx3
            oln = x3*rad
c
            if (c3.eq.'#') goto 19
c
            if (Lhavej .and. .not.Loutj) then
               call getapj(x3    , y3    , ampj  , phsj  , mgmax ,
     +              ngmax , hight , phase                  )
            else
               call getapw(x3    , y3    , gsize , xmin  , ymax  ,
     +              mend  , nend  , hight , phase          )
            endif
c
            call angld(rlt, rln, olt, oln, angd)
            dang   = angd/rad   
c
            if ( (dang.le.abnd34) .and. Lmesh4 ) then
c
               Lc4 = .false.
c
               if ( (c3.eq.'.').and. Lfullm ) then
                  do n4 = 1,20
                     do m4 = 1,20
                        cmesh4(m4,n4) = '.'
                     enddo
                  enddo
                  Lc4 = .true.
               endif
c
               if (c3.ne.'.') then
                  call rd4th(30, cmesh4, m2, n2, m3, n3, ndx4, ndy4)
                  Lc4 = .true.
               endif

               if (Lc4) then
c
                  call convl4(istat , kind  , hight , phase , x3    ,
     +                        y3    , cmesh4, dx3   , dy3   , ndx4  ,
     +                        ndy4                                   )
c
                  Lc3 = .false.
c
               endif            ! Lc4
c
            endif               ! Angular distance test
c
c -----< Calculation with 3rd order mesh >-----
c     
 19         if (Lc3) then
c
               if (c3.eq.'.') then
                  ar0 = 1.d0
               else if (c3.eq.'#') then
                  ar0 = 0.d0
               else
                  read(c3,'(i1)') iar
                  ar0 = (9.5d0-dfloat(iar))/9.0d0
               endif
c
               if ( (ar0.gt.0.d0).and.(hight.lt.9.998d0) ) then 
c
                  if (dang.le.adist) then
                     adist = dang
                     oltm  = olt/rad
                     olnm  = oln/rad
                  endif
c
                  nintg3 = nintg3 + 1
c     
                  call cintgl(rlt   , rln   , alt   , azm   , kind  ,
     +                        olt   , oln   , wlt   , wln   , ar0   ,
     +                        hight , phase , cov                   )
c
                  do k2 = 1,2
c
                     if (Lfirst) then
                        suma(3,k2) = suma(3,k2) + cov(k2,2)
                     endif
c     
                     sume(3,k2) = sume(3,k2) + cov(k2,3)
c     
                     do k3 = 1,ncmp
                        sum(3,k2,k3) = sum(3,k2,k3) + cov(k2,k3)
                     enddo
c     
                  enddo         ! k2
c     
               else
c     
                  land3 = land3 + 1
c
               endif            ! Not land and tide defined
c
c -----< Printing mesh information >-----
c
               if ( Lmapout.and.(x3.ge.xb1).and.(x3.le.xb2).and.
     +              (y3.ge.yb1).and.(y3.le.yb2).and.Lvryfst     ) then
c
                  if ( ((ar0.gt.0.d0).and.(.not.Lmapln)).or.
     +                 ((ar0.eq.0.d0).and.(     Lmapln))    ) then
c
                     write(99,101)
 101                 format('>')
                     write(99,'(2f11.6)') x3 + halfx3, y3 + halfy3
                     write(99,'(2f11.6)') x3 - halfx3, y3 + halfy3
                     write(99,'(2f11.6)') x3 - halfx3, y3 - halfy3
                     write(99,'(2f11.6)') x3 + halfx3, y3 - halfy3
                     write(99,'(2f11.6)') x3 + halfx3, y3 + halfy3
c
                  endif
c
               endif
c     
            endif               ! Lc3
c
         enddo                  ! m3
      enddo                     ! n3
c
      return
      end
c




