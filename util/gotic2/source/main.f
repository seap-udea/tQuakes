c$main
c
c****************************************************
c* PROGRAM TO COMPUTE SOLID TIDE AND OCEAN LOAD     *
c* FOR OBSERVATION SITES IN JAPAN.                  *
c*                                                  *
c* ORIGINALY CODED BY T.SATO & H. HANADA OF NAO     *
c*                                                  *
c* Modified by K. MATSUMOTO of NAO                  *
c* Version 2004.09.16                               *
c* Email contact -> matumoto@miz.nao.ac.jp          *
c*                                                  *
c*+**************************************************
c
      program gotic2
c
      implicit double precision (a-h,o-z)
c
      Logical Lmapout, Lmesh1, Lmesh2, Lmesh3, Lmesh4, Lpoint, Lmascor
      Logical Latan2 , Lfirst,Lvryfst, Lminfo, Lverbo, Lpred , Lprein
      Logical Loutj  , Lhavej, Lpr186, Lfullm, Lmapln 
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
      common /areas/  area1, area2, abnd12, abnd23, abnd34
      common /comp/   ncomp(6)
      common /const/  rearth, earthm, gravct, pi , rad, deg,
     +                dens  , rls1  , rls2  , egv, elp
      common /flag/   Lmapout, Lmesh1, Lmesh2, Lmesh3, Lmesh4, Lpoint,
     +                Lmascor, Latan2, Lverbo, Lpred , Lprein, Lhavej,
     +                Loutj  , Lmapln, Lfullm
      common /gfile/  ang(50), grn(50,6), cgrn(50,2,3), igrn, idelta
      common /gotd/   oamp(721,361), ophs(721,361)
      common /inela/  anel1, anel2
      common /jmap/   xminj, xmaxj, yminj, ymaxj, gsizej, mendj, nendj
      common /name/   sname(10)
      common /nodupl/ Lfirst, Lvryfst, Lminfo
      common /meshi/  nd2nd , nd3rd , nd4th , nintg1, nintg2, nintg3,
     +                nintg4, land1 , land2 , land3 , land4 , nd3rdj
      common /meshr/  adist , olnm  , oltm
      common /pgrd/   xb1, xb2, yb1, yb2
      common /predr/  prsmjd, premjd, prdt, prein
      common /predi/  iprfm1, iprfm2, iprcmp, Lpr186
      common /stat99/ slat(10,3), slon(10,3),
     +                altd(10), azmth(10), slt(10), sln(10)
      common /sums/   sum(5,2,6), suma(5,2), sume(5,2)
      common /gtimes/ igtime, igy, igm, igd
      common /wavei/  ncnt(21), isp(21)
      common /waver/  xlambda(21)
      common /wavec/  wn(21)
c
      character    wn*3, sname*10, kn*2
      character*80 tmapw(21), tmapj(21), tm1, tm2, grn1, grn2, grn3,
     +             grn4, grn5, fmap1, prein, datdir, omodel
c
      parameter (mgmax   = 662, ngmax = 542  )
c
      dimension ikind(6)
      dimension sumr(4,6), sumi(4,6)
      dimension sumar(4), sumai(4), sumer(4), sumei(4)
c
      dimension ampj(mgmax,ngmax)  , phsj(mgmax,ngmax)
      dimension kn(6)
c
      data kn /'RD','HD','GV','TL','ST','DV'/
c
      data ivery  /2004/
      data iverm  /10/
      data iverd  /25/
c
      data iunt10 /10/
      data iunt20 /20/
c
c -----< Banner >-----
c
      call banner(ivery, iverm, iverd)
c
c -----< Read control parameters >-----
c
      call readin(nstat, nwave, nkind, ikind, datdir, omodel)
c
c -----< File conf >-----
c
      call fconf(tmapw  , tmapj , grn1  , grn2  , grn3  ,
     +           grn4   , grn5  , fmap1 , datdir, omodel)
c
c -----< Not PREDICTION mode >-----
c      
      if (.not. Lprein) then
c
c -----< Read Green's functions >-----
c
      call earth(iunt10, grn1, grn2, grn3, grn4, grn5)
c
c -----< Warning related to Green's function availavility >-----
c
      do kk = 1,nkind
c
         kind = ikind(kk)
c
         if ((igrn.eq.4.or.igrn.eq.5).and.(kind.ne.3)) then
c
            print*,'!!! Error : Complex Green function is available',
     +             ' only for gravity.'
            stop
c
         endif
c
      enddo
c
c -----< Tidal wave loop >-----
c
      do iwave = 1,nwave
c
         iw = ncnt(iwave)
c
         if (Lverbo) then
            write(6,6001)
            write(6,6032) wn(iw)
 6032       format(' Computation for wave ',a3)
            write(6,6001)
         endif
c
c -----< Read ocean tide models >-----
c     
         tm1 = tmapw(iw)
         tm2 = tmapj(iw)
c
         call gmodel(tm1   , tm2   , xmin  , ymax  , gsize ,
     +               ampj  , phsj  , mgmax , ngmax , mend  ,
     +               nend                                   )
c
c -----< Station loop >-----
c
         do istat = 1,nstat
c
            xc = sln(istat)
            yc = slt(istat)

            if ( (xc.lt.xminj) .or. (xc.gt.xmaxj) .or.
     +           (yc.lt.yminj) .or. (yc.gt.ymaxj)     ) then
               Loutj  = .true.
            else
               Loutj  = .false.
               Lmesh3 = .true.
            endif
c
c -----< Kind loop >-----
c
            do kk = 1,nkind
c     
               kind  = ikind(kk)
               ncmp  = ncomp(kind)
c
               if (Lverbo) then
                  write(6,6033) wn(iw),sname(istat),kn(kind)
 6033             format(3x,'Wave : ',a3,', Station : ',a10,
     +                   ', Kind : ',a2)
               endif
c
c -----< init >-----
c
               do mc = 1,ncmp
                  do mm = 1,4
                     sumr(mm,mc) = 0.d0
                     sumi(mm,mc) = 0.d0
                     sumar(mm)   = 0.d0
                     sumai(mm)   = 0.d0
                     sumer(mm)   = 0.d0
                     sumei(mm)   = 0.d0
                  enddo
               enddo
c
c -----< Computation with Green's function for an elastic Earth >-----
c
               if (igrn.le.3) then
c
                  Lfirst = .true.
c
                  if (Lmesh1) then
                     call convl1(istat , kind  , xmin  , ymax  , gsize ,
     +                           mgmax , ngmax , ampj  , phsj  , mend  ,
     +                           nend  , fmap1 , datdir                )
                  endif
c
c -----< Computation with Green's function for an anelastic Earth >-----
c
               else if ( (igrn.ge.4).and.(igrn.le.5) ) then
c
                  msp = isp(ncnt(iwave)) ! 1 : semi-diurnal, 2 : diurnal,
c                                          3 : zonal
                  do mri = 1,2  ! 1 : real green, 2 : imaginary green
c
c -----< Message & avoid duplicated calculation of attraction >-----
c
                     if (Lverbo) then
                        if (mri.eq.1) then
                           Lfirst = .true.
                           write(6,6034)
 6034                      format('    Computing real part.')
                        else
                           Lfirst = .false.
                           write(6,6035)
 6035                      format('    Computing imaginary part.')
                        endif
                     endif
c
c -----< Green's function >-----
c
                     do mdeg = 1,50
                        grn(mdeg,kind) = cgrn(mdeg,mri,msp)
                     enddo
c
c -----< Convolution >-----
c
                     if (Lmesh1) then
                        call convl1(istat , kind  , xmin  , ymax  ,
     +                              gsize , mgmax , ngmax , ampj  ,
     +                              phsj  , mend  , nend  , fmap1 ,
     +                              datdir                        )
                     endif
c[
c -----< Buffering >-----
c
                     if (mri.eq.1) then
c
                        do mc = 1,ncmp
                           do mm = 1,4
c
                              sumr(mm,mc) = sumr(mm,mc) + sum(mm,1,mc)
                              sumi(mm,mc) = sumi(mm,mc) + sum(mm,2,mc)
                              sumar(mm)   = sumar(mm) + suma(mm,1)
                              sumai(mm)   = sumai(mm) + suma(mm,2)
                              sumer(mm)   = sumer(mm) + sume(mm,1)
                              sumei(mm)   = sumei(mm) + sume(mm,2)
c
                           enddo
                        enddo
c
                     else
c
                        do mc = 1,ncmp
                           do mm = 1,4
c
                              sumr(mm,mc) = sumr(mm,mc) - sum(mm,2,mc)
                              sumi(mm,mc) = sumi(mm,mc) + sum(mm,1,mc)
                              sumer(mm)   = sumer(mm) - sume(mm,2)
                              sumei(mm)   = sumei(mm) + sume(mm,1)
c
                           enddo
                        enddo
c
                     endif      ! real green or imaginary green
c
                  enddo         ! mri
c     
                  do mc = 1,ncmp
                     do mm = 1,4
c     
                        sum(mm,1,mc) = sumr(mm,mc)
                        sum(mm,2,mc) = sumi(mm,mc)
                        suma(mm,1)   = sumar(mm)
                        suma(mm,2)   = sumai(mm)
                        sume(mm,1)   = sumer(mm)
                        sume(mm,2)   = sumei(mm)
c
                     enddo
                  enddo
c
               else
c
                  print*,'!!! Error : @ main.f, igrn = ',igrn
                  stop
c     
               endif            ! elastic or complex
c
c -----< Store results >-----
c
               call result(istat, iwave, kind)
               call reslt2(istat, iwave, kind)
c
               if (Lvryfst) then
                  Lvryfst = .false.
               endif
c
            enddo               ! kind loop
c
c -----< Print mesh information >-----
c
            if (Lminfo .and. Lverbo) then
c
               write(6,6001)
               write(6,6011)
               write(6,6002) nintg1
               write(6,6003) nintg2
               write(6,6004) nintg3
               write(6,6013) nintg4
               write(6,6005) land1
               write(6,6006) land2
               write(6,6007) land3
               write(6,6014) land4
               write(6,6008) olnm
               write(6,6009) oltm
               write(6,6010) adist
               write(6,6012)
               write(6,6001)
c     
               Lminfo = .false.
c     
            endif
c
         enddo                  ! station loop
c     
      enddo                     ! tidal wave loop
c
c -----< Print out results >-----
c
      write(6,6001)
      write(6,6001)
c
      do istat = 1,nstat
         do kk = 1,nkind
c
            kind = ikind(kk)
c
            call lpout (istat, nwave, kind)
            call lpout2(istat, nwave, kind)
c
         enddo
      enddo
c
c -----< PREDICT and PREIN card exist : PREDICT only mode >-----
c
      else if (Lpred) then
c     
         call rdprein(iunt10, ikind)
c
      endif
c
c -----< Prediction >-----
c
      if (Lpred) then
c
         call predic(iunt20, nstat, nwave, nkind, ikind) 
c
      endif
c
 6001 format(' ')
 6011 format('   -----------------< Mesh Information >',
     +       '-----------------')
 6002 format(3x,'Number of 1st order ocean meshes = ',i8)
 6003 format(3x,'Number of 2nd order ocean meshes = ',i8)
 6004 format(3x,'Number of 3rd order ocean meshes = ',i8)
 6013 format(3x,'Number of 4th order ocean meshes = ',i8)
 6005 format(3x,'Number of 1st order land meshes  = ',i8)
 6006 format(3x,'Number of 2nd order land meshes  = ',i8)
 6007 format(3x,'Number of 3rd order land meshes  = ',i8)
 6014 format(3x,'Number of 4th order land meshes  = ',i8)
 6008 format(3x,'Nearest ocean grid : Lon = ',f10.5,' (deg)')
 6009 format(3x,'                     Lat = ',f10.5,' (deg)')
 6010 format(24x,'Angular Distance = ',f8.5,' (deg)')
 6012 format('   ---------------------------------',
     +       '---------------------')
c
      stop
      end
c




