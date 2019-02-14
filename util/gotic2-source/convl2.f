c$convl2
c------------------------------------------------------------------
      subroutine convl2(istat , kind  , mgmax , ngmax , ampj  ,
     +                  phsj  , x1    , y1    , cmesh2, gsizecm,
     +                  ndx2  , ndy2  , ndx3  , ndy3  , ndx4  ,
     +                  ndy4  , xmin  , ymax  , mend  , nend  ,gsize )
c------------------------------------------------------------------
c
c     CONVOLUTION INTEGRAL WITH SECOND ORDER MESH
c
      implicit double precision (a-h,o-z)
c
      Logical Lmapout, Lmesh1, Lmesh2 , Lmesh3, Lmesh4, Lpoint, Lmascor
      Logical Latan2 , Lfirst, Lvryfst, Lminfo, Lverbo, Lpred , Lprein
      Logical Lhavej , Loutj , Lfullm , Lmapln
      Logical Lc2    , Lc3
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
      character*1  c2, cmesh2, cmesh3
c
      dimension cov(2,6)
      dimension ampj(mgmax,ngmax)  , phsj(mgmax,ngmax)
      dimension cmesh2(6,6), cmesh3(10,10)
c
c -----< Initialize parameters >-----
c
      ncmp   = ncomp(kind)
      rln    = sln(istat)*rad
      rlt    = slt(istat)*rad
      alt    = altd(istat)
      azm    = azmth(istat)
c
      dx2    = gsizecm/dfloat(ndx2)
      dy2    = gsizecm/dfloat(ndy2)
      wlt    = dx2*rad
      wln    = dy2*rad
      halfx2 = 0.5d0*dx2
      halfy2 = 0.5d0*dy2
c
      x1w = x1 - 0.5d0*gsizecm
      y1n = y1 + 0.5d0*gsizecm
c     
      do n2 = 1,ndy2
c
         y2  = y1n - (dfloat(n2)-0.5d0)*dy2
         olt = y2*rad
c
         do m2 = 1,ndx2
c
            Lc2 = .true.
            c2  = cmesh2(m2,n2)
c
            x2  = x1w + (dfloat(m2)-0.5d0)*dx2
            oln = x2*rad
c
            if (c2.eq.'#') goto 19
c
            call angld(rlt, rln, olt, oln, angd)
            dang   = angd/rad   
c
            if ( (dang.le.abnd23) .and. Lmesh3 ) then
c
               Lc3 = .false.
c
               if ( (c2.eq.'.').and. Lfullm ) then
                  do n3 = 1,10
                     do m3 = 1,10
                        cmesh3(m3,n3) = '.'
                     enddo
                  enddo
                  Lc3 = .true.
               endif
c
               if (c2.ne.'.') then
                  call rd3rd(30, cmesh3, m2, n2, ndx3, ndy3)
                  Lc3 = .true.
               endif
c
               if (Lc3) then
c
                  call convl3(istat , kind  , mgmax , ngmax , ampj  ,
     +                        phsj  , x2    , y2    , m2    , n2    ,
     +                        cmesh3, dx2   , dy2   , ndx3  , ndy3  ,
     +                        ndx4  , ndy4  , gsize , xmin  , ymax  ,
     +                        mend  , nend                           )
c
                  Lc2 = .false.
c
               endif            ! Lc3
c
            endif               ! Angular distance test
c
c -----< Calculation with 2nd order mesh >-----
c     
 19         if (Lc2) then
c
               if (c2.eq.'.') then
                  ar0 = 1.d0
               else if (c2.eq.'#') then
                  ar0 = 0.d0
               else
                  read(c2,'(i1)') iar
                  ar0 = (9.5d0-dfloat(iar))/9.0d0
               endif
c
               if (Lhavej .and. .not.Loutj) then
                  call getapj(x2    , y2    , ampj  , phsj  , mgmax ,
     +                        ngmax , hight , phase                  )
               else
                  call getapw(x2    , y2    , gsize , xmin  , ymax  ,
     +                        mend  , nend  , hight , phase          )
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
                  nintg2 = nintg2 + 1
c
                  call cintgl(rlt   , rln   , alt   , azm   , kind  ,
     +                        olt   , oln   , wlt   , wln   , ar0   ,
     +                        hight , phase , cov                    )
c     
                  do k2 = 1,2
c     
                     if (Lfirst) then
                        suma(2,k2) = suma(2,k2) + cov(k2,2)
                     endif
c     
                     sume(2,k2) = sume(2,k2) + cov(k2,3)
c     
                     do k3 = 1,ncmp
                        sum(2,k2,k3) = sum(2,k2,k3) + cov(k2,k3)
                     enddo
c     
                  enddo         ! k2
c
               else             ! land grid
c
                  land2 = land2 + 1
c
               endif            ! Not land and tide defined
c     
c -----< Printing mesh information >-----
c
               if ( Lmapout.and.(x2.ge.xb1).and.(x2.le.xb2).and.
     +              (y2.ge.yb1).and.(y2.le.yb2).and.Lvryfst     ) then
c
                  if ( ((ar0.gt.0.d0).and.(.not.Lmapln)).or.
     +                 ((ar0.eq.0.d0).and.(     Lmapln))    ) then
c
                     write(99,101)
 101                 format('>')
                     write(99,'(2f11.6)') x2 + halfx2, y2 + halfy2
                     write(99,'(2f11.6)') x2 - halfx2, y2 + halfy2
                     write(99,'(2f11.6)') x2 - halfx2, y2 - halfy2
                     write(99,'(2f11.6)') x2 + halfx2, y2 - halfy2
                     write(99,'(2f11.6)') x2 + halfx2, y2 + halfy2
c     
                  endif
c     
               endif
c     
            endif               ! Lc2
c     
         enddo                  ! m2
      enddo                     ! n2
c
      return
      end
c
