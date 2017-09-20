c$convl1
c---------------------------------------------------------------
      subroutine convl1(istat , kind  , xmin  , ymax  , gsize ,
     +                  mgmax , ngmax , ampj  , phsj  , mend  ,
     +                  nend  , fmap1 , datdir                 )
c---------------------------------------------------------------
c
      implicit double precision (a-h,o-z)
c
      Logical Lmapout, Lmesh1, Lmesh2 , Lmesh3, Lmesh4, Lpoint, Lmascor
      Logical Latan2 , Lfirst, Lvryfst, Lminfo, Lverbo, Lpred , Lprein
      Logical Lhavej , Loutj , Lfullm , Lmapln
      Logical Lc1    , Lc2
c
c     Setting parameters of convolution mesh
      parameter (xmincm = 0.25d0, ymaxcm = 89.75d0, gsizecm = 0.5d0)
      parameter (mendcm = 720   , nendcm = 360)
c 
      common /areas/  area1, area2, abnd12, abnd23, abnd34
      common /comp/   ncomp(6)
      common /const/  rearth, earthm, gravct, pi , rad, deg,
     +                dens  , rls1  , rls2  , egv, elp
      common /flag/   Lmapout, Lmesh1, Lmesh2, Lmesh3, Lmesh4, Lpoint,
     +                Lmascor, Latan2, Lverbo, Lpred , Lprein, Lhavej,
     +                Loutj  , Lmapln, Lfullm
      common /gotd/   oamp(721,361), ophs(721,361)
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
      character*1  c1, cmesh1, cmesh2
      character*80 fmap1, datdir
c
      dimension ampj(mgmax,ngmax), phsj(mgmax,ngmax)
      dimension cov(2,6)
      dimension cmesh1(mendcm,nendcm), cmesh2(6,6)
c
c -----< Initialize parameters >-----
c
      oltm   = 0.d0             ! Latitude  of nearest point
      olnm   = 0.d0             ! Longitude of nearest point
      land1  = 0
      land2  = 0
      land3  = 0
      land4  = 0
      nintg1 = 0
      nintg2 = 0
      nintg3 = 0
      nintg4 = 0
c
      adist  = 180.d0
      ncmp   = ncomp(kind)
      rln    = sln(istat)*rad   ! Station coordinate, longitude
      rlt    = slt(istat)*rad   ! Station coordinate, latitude
      alt    = altd(istat)
      azm    = azmth(istat)
c
      wlt = gsizecm*rad
      wln = gsizecm*rad
c
      half1 = gsizecm*0.5d0
c
      do k1 = 1,5
         do k2 = 1,2
c
            suma(k1,k2) = 0.d0
            sume(k1,k2) = 0.d0
c
            do k3 = 1,6
               sum(k1,k2,k3) = 0.d0
            enddo
c
         enddo
      enddo
c
c -----< Read 1st-order mesh >-----
c
      call rd1st(cmesh1, fmap1, mendcm, nendcm)
c
c -----< Loop for 1st-order mesh >-----
c
      do n1 = 1,nendcm
c
         y1  = ymaxcm - dfloat(n1-1)*gsizecm
         olt = y1*rad
c
         do m1 = 1,mendcm
c
            Lc1 = .true.
            c1  = cmesh1(m1,n1)
c
            x1  = xmincm + dfloat(m1-1)*gsizecm
            oln = x1*rad
c
            if (c1.eq.'#') goto 19
c
            call angld(rlt, rln, olt, oln, angd)
            dang = angd/rad     ! in degrees
c
            if ( (dang.le.abnd12) .and. Lmesh2 ) then
c
               Lc2 = .false.
c
               if ( (c1.eq.'.') .and. Lfullm ) then
                  do n2 = 1,6
                     do m2 = 1,6
                        cmesh2(m2,n2) = '.'
                     enddo
                  enddo
                  Lc2 = .true.
                  if (Loutj) then
                     ndx2 = 6
                  else
                     ndx2 = 4
                  endif
                  ndy2 = 6
               endif                  
c
               if (c1.ne.'.') then
                  call omeshf(30, datdir, m1, n1)
                  call rd2nd(30    , cmesh2, m1    , n1    , ndx2  ,
     +                       ndy2  , ndx3  , ndy3  , ndx4  , ndy4   )
                  Lc2 = .true.
               endif
c
               if (Lc2) then
c
                  call convl2(istat , kind  , mgmax , ngmax , ampj  ,
     +                        phsj  , x1    , y1    , cmesh2, gsizecm,
     +                        ndx2  , ndy2  , ndx3  , ndy3  , ndx4  ,
     +                        ndy4  , xmin  , ymax  , mend  , nend  ,
     +                        gsize                                  )
c     
                  Lc1 = .false.
c
               endif            ! Lc2
c
            endif               ! Angular distance test
c
 19         if (Lc1) then
c
               if (c1.eq.'.') then
                  ar0 = 1.d0
               else if (c1.eq.'#') then
                  ar0 = 0.d0
               else
                  read(c1,'(i1)') iar
                  ar0 = (9.5d0-dfloat(iar))/9.0d0
               endif
c
               call getapw(x1    , y1    , gsize , xmin  , ymax  ,
     +                     mend  , nend  , hight , phase          )
c
               if ( (ar0.gt.0.d0).and.(hight.lt.9.998d0) ) then 
c     
                  nintg1 = nintg1 + 1
c
                  if (dang.le.adist) then
                     adist = dang
                     oltm  = olt/rad
                     olnm  = oln/rad
                  endif
c
                  call cintgl(rlt   , rln   , alt   , azm   , kind  ,
     +                        olt   , oln   , wlt   , wln   , ar0   ,
     +                        hight , phase , cov                    )
c
                  do k2 = 1,2
c
                     if (Lfirst) then
                        suma(1,k2)  = suma(1,k2) + cov(k2,2)
                     endif
c     
                     sume(1,k2)  = sume(1,k2) + cov(k2,3)
c     
                     do k3 = 1,ncmp
                        sum(1,k2,k3) = sum(1,k2,k3) + cov(k2,k3)
                     enddo
c     
                  enddo
c
               else
c
                  land1 = land1 + 1
c
               endif            ! Not land and tide defined
c
c -----< Printing mesh information >-----
c
               if ( Lmapout.and.(x1.ge.xb1).and.(x1.le.xb2).and.
     +              (y1.ge.yb1).and.(y1.le.yb2).and.Lvryfst     ) then
c
                  if ( ((ar0.gt.0.d0).and.(.not.Lmapln)).or.
     +                 ((ar0.eq.0.d0).and.(     Lmapln))    ) then
c
                     write(99,101)
 101                 format('>')
                     write(99,'(2f11.6)') x1 + half1, y1 + half1
                     write(99,'(2f11.6)') x1 - half1, y1 + half1
                     write(99,'(2f11.6)') x1 - half1, y1 - half1
                     write(99,'(2f11.6)') x1 + half1, y1 - half1
                     write(99,'(2f11.6)') x1 + half1, y1 + half1
c
                  endif
c
               endif            ! tide defined
c
            endif               ! Lc1
c
         enddo
      enddo
c
      return
      end
c
