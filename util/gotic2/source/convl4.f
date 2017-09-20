c$convl4
c------------------------------------------------------------------
      subroutine convl4(istat , kind  , hight , phase , x3    ,
     +                  y3    , cmesh4, dx3   , dy3   , ndx4  ,
     +                  ndy4                                   )
c------------------------------------------------------------------
c
c     CONVOLUTION INTEGRAL WITH SECOND ORDER MESH
c
      implicit double precision (a-h,o-z)
c
      Logical Lmapout, Lmesh1, Lmesh2, Lmesh3, Lmesh4, Lpoint, Lmascor
      Logical Latan2 , Lfirst, Lvryfst,Lminfo, Lverbo, Lpred , Lprein
      Logical Lhavej , Loutj , Lfullm ,Lmapln
c
      common /comp/   ncomp(6)
      common /const/  rearth, earthm, gravct, pi , rad, deg,
     +                dens  , rls1  , rls2  , egv, elp
      common /flag/   Lmapout, Lmesh1, Lmesh2, Lmesh3, Lmesh4, Lpoint,
     +                Lmascor, Latan2, Lverbo, Lpred , Lprein, Lhavej,
     +                Loutj  , Lmapln, Lfullm
      common /nodupl/ Lfirst, Lvryfst, Lminfo
      common /meshi/  nd2nd , nd3rd , nd4th , nintg1, nintg2, nintg3,
     +                nintg4, land1 , land2 , land3 , land4 , nd3rdj
      common /meshr/  adist , olnm  , oltm
      common /pgrd/   xb1, xb2, yb1, yb2
      common /stat99/ slat(10,3), slon(10,3),
     +                altd(10), azmth(10), slt(10), sln(10)
      common /sums/   sum(5,2,6), suma(5,2), sume(5,2)
c
      character*1 c4, cmesh4
c
      dimension cov(2,6)
      dimension cmesh4(20,20)
c
      data ndx4dv, ndy4dv /20,20/
c
c -----< Initialize parameters >-----
c
      if (ndx4.eq.0) then
         ndx4 = ndx4dv
         ndy4 = ndy4dv
      endif
c
      ncmp   = ncomp(kind)
      rln    = sln(istat)*rad
      rlt    = slt(istat)*rad
      alt    = altd(istat)
      azm    = azmth(istat)
c
      dx4    = dx3/dfloat(ndx4)
      dy4    = dy3/dfloat(ndy4)
      wlt    = dx4*rad
      wln    = dy4*rad
      halfx4 = 0.5d0*dx4
      halfy4 = 0.5d0*dy4
c
      x3w = x3 - 0.5d0*dx3
      y3n = y3 + 0.5d0*dy3
c
c -----< Calc. on 4th-order mesh >-----
c
      do n4 = 1,ndy4
c
         y4  = y3n - (dfloat(n4)-0.5d0)*dy4
         olt = y4*rad
c
         do m4 = 1,ndx4
c
            x4  = x3w + (dfloat(m4)-0.5d0)*dx4
            oln = x4*rad
c
            c4  = cmesh4(m4,n4)
c
            call angld(rlt, rln, olt, oln, angd)
            dang   = angd/rad
c     
            if (dang.lt.0.0001d0) then
c     
               print*,'### Warning in <convl4> : ',
     +              '***Too near ! ***'
               print*,'### ',rln/rad,rlt/rad,x4,y4,dang
c     
            else
c     
               if (c4.eq.'.') then
                  ar0 = 1.d0
               else if (c4.eq.'#') then
                  ar0 = 0.d0
               else
                  read(c4,'(i1)') iar
                  ar0 = (9.5d0-dfloat(iar))/9.0d0
               endif
c     
               if ( (ar0.gt.0.d0).and.(hight.lt.9.998d0) ) then 
                  
                  if (dang.le.adist) then
                     adist = dang
                     oltm  = olt/rad
                     olnm  = oln/rad
                  endif
c     
                  nintg4 = nintg4 + 1
c     
                  call cintgl(rlt   , rln   , alt   , azm   ,
     +                        kind  , olt   , oln   , wlt   ,
     +                        wln   , ar0   , hight , phase ,
     +                        cov                            )
c     
                  do k2 = 1,2
c     
                     if (Lfirst) then
                        suma(4,k2) = suma(4,k2) + cov(k2,2)
                     endif
c     
                     sume(4,k2) = sume(4,k2) + cov(k2,3)
c     
                     do k3 = 1,ncmp
                        sum(4,k2,k3) = sum(4,k2,k3) + cov(k2,k3)
                     enddo
c     
                  enddo         ! k2
c     
               else             ! land grid
c     
                  land4 = land4 + 1
c     
               endif ! Not land and tide defined
c     
c -----< Printing mesh information >-----
c     
               if ( Lmapout.and.(x4.ge.xb1).and.(x4.le.xb2).and.
     +              (y4.ge.yb1).and.(y4.le.yb2).and.Lvryfst     ) then
c
                  if ( ((ar0.gt.0.d0).and.(.not.Lmapln)).or.
     +                 ((ar0.eq.0.d0).and.(     Lmapln))    ) then
c     
                     write(99,101)
 101                 format('>')
                     write(99,'(2f12.7)') x4 + halfx4, y4 + halfy4
                     write(99,'(2f12.7)') x4 - halfx4, y4 + halfy4
                     write(99,'(2f12.7)') x4 - halfx4, y4 - halfy4
                     write(99,'(2f12.7)') x4 + halfx4, y4 - halfy4
                     write(99,'(2f12.7)') x4 + halfx4, y4 + halfy4
c     
                  endif
c     
               endif
c     
            endif               ! Green's function defined or not
c
         enddo                  ! m4
      enddo                     ! n4
c
      return
      end
c

