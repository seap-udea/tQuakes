c$readin
c----------------------------------------------------------------
      subroutine readin(nstat, nwave, nkind, ikind, datdir, omodel)
c----------------------------------------------------------------
c
      implicit double precision (a-h,o-z)
c
      Logical Lmapout, Lmesh1, Lmesh2, Lmesh3, Lmesh4, Lpoint, Lmascor
      Logical Latan2 , Lverbo, Lpred , Lprein, Lftn20, Lpr186
      Logical Lhavej , Loutj , Lfullm , Lmapln
c
      parameter (ab12mx = 60.d0, ab23mx = 30.d0, ab34mx = 30.d0)
c
      common /areas/  area1, area2, abnd12, abnd23, abnd34
      common /const/  rearth, earthm, gravct, pi , rad, deg,
     +                dens  , rls1  , rls2  , egv, elp
      common /flag/   Lmapout, Lmesh1, Lmesh2, Lmesh3, Lmesh4, Lpoint,
     +                Lmascor, Latan2, Lverbo, Lpred , Lprein, Lhavej,
     +                Loutj  , Lmapln, Lfullm
      common /gfile/  ang(50), grn(50,6), cgrn(50,2,3), igrn, idelta
      common /inela/  anel1, anel2
      common /name/   sname(10)
      common /pgrd/   xb1, xb2, yb1, yb2
      common /predr/  prsmjd, premjd, prdt, prein
      common /predi/  iprfm1, iprfm2, iprcmp, Lpr186
      common /stat99/ slat(10,3), slon(10,3),
     +                altd(10), azmth(10), slt(10), sln(10)
      common /gtimes/ igtime, igy, igm, igd
      common /wavei/  ncnt(21), isp(21)
      common /waver/  xlambda(21)
      common /wavec/  wn(21)
c
      character*100 buf, buf2, buf3, bufbuf(200)
      character*80  prein, prtxt, pftxt1, pftxt2, pftxt3, datdir,
     +              ftn99, ftn06, ftn20, omodel
      character*10  site, sname
      character*4   wtest1, wtest2
      character*3   wn, wtest3, wtest4
      character*2   kn(6), wn2
c
      dimension     ikind0(7), ikind(6)
      dimension     ncnt0(50)
      dimension     prtxt(3), pftxt1(5), pftxt2(6,2), pftxt3(6,2)
c
      data kn /'RD','HD','GV','TL','ST','DV'/
c
      data prtxt/'Solid Earth Tide + Ocean Loading Tide',
     +           'Solid Earth Tide                     ',
     +           'Ocean Loding Tide                    '/
c
      data pftxt1/'day','hour','minute','second','YYYY/MM/DD HH:MM'/
      data pftxt2/'RD : upward positive',
     +            'HD : northward, eastward positive',
     +            'GV : upward positive',
     +            'TL : upward-N, upward-E, upward-Azimuth positive',
     +            'ST : extension positive',
     +            'DV : upward-N, upward-E positive',
     +            'RD : downward positive',
     +            'HD : thouthward, westward positive',
     +            'GV : downward positive',
     +         'TL : downward-N, downward-E, downward-Azimuth positive',
     +            'ST : compression positive',
     +            'DV : downward-N, downward-E positive'/
      data pftxt3/'RD (m)'  ,'HD (m)'             ,'GV (m/s/s)'   ,
     +            'TL (rad)','ST (nondimensional)','DV (rad)'     ,
     +            'RD (mm)' ,'HD (mm)'            ,'GV (microGal)',
     +            'TL (nanorad)','ST*10^9 (nondimensional)',
     +            'DV (nanorad)'/
c
      data ftn99/'mapout.xy'/
c
c -----< Init >-----
c
      nstat = 0
      do i = 1,10
         altd(i)  = 0.d0
         azmth(i) = 0.d0
         slt(i)   = 0.d0
         sln(i)   = 0.d0
         do j = 1,3
            slat(i,j) = 0.d0
            slon(i,j) = 0.d0
         enddo
      enddo
c
      nkind  = 0
      nkind0 = 0
      do i = 1,7
         ikind0(i) = 0
      enddo
c
      nwave  = 0
      do i = 1,50
         ncnt0(i) = 0
      enddo
c
      area1  = 0.d0
      area2  = 180.d0*rad
      xb1    = 0.d0
      xb2    = 0.d0
      yb1    = 0.d0
      yb2    = 0.d0
      abnd12 = 10.d0
      abnd23 =  5.d0
      abnd34 =  0.2d0
      anel1  = 0.d0
      anel2  = 0.d0
c
      igrn   = 2
      idelta = 2
      iprfm1 = 5
      iprfm2 = 1
      igtime = 0
c
      Lmesh1  = .true.
      Lmesh2  = .true.
      Lmesh3  = .false.
      Lmesh4  = .false.
      Lpoint  = .false.
      Lmapout = .false.
      Lmapln  = .true.
      Lmascor = .true.
      Latan2  = .false.
      Lverbo  = .true.
      Lpred   = .false.
      Lprein  = .false.
      Lftn20  = .false.
      Lpr186  = .true.
      Lfullm  = .false.
c
      nbuf = 0
c
      datdir = './data/'
      omodel = 'nao'
      prein  = ' '
      ftn20  = ' '
c
c -----< Reading Loop >-----
c
      do while (buf(1:3).ne.'END')
c
 10      read(5,'(a100)',end=900) buf
c
         nbuf = nbuf + 1
         bufbuf(nbuf) = buf
c
c -----< 1-1: STAPOSD card >-----
c
         if (buf(1:7).eq.'STAPOSD') then
c
            nstat = nstat + 1
c
            if (nstat.gt.10) then
               print*,'!!! Error : STAPOSD card'
               print*,'!!!         Number of station should be',
     +                ' smaller than 10.'
               stop 1
            endif
c
            buf2 = buf(8:100)
c
            read(buf2,*) site, x ,y, alt, azm
c
            sname(nstat)  = site
c
            if (x.lt.0.d0) then
               x = x + 360.d0
            endif
            if (x.gt.360.d0) then
               print*,'!!! Error : STAPOSD card'
               print*,'!!!         Invalid longitude for site ',site
               stop 1
            endif
            if ( (y.lt.-90.d0).or.(y.gt.90.d0) ) then
               print*,'!!! Error : STAPOSD card'
               print*,'!!!         Invalid latitude for site ',site
               stop 1
            endif
c
            sln(nstat) = x
            slt(nstat) = y
c
            ixd  = x
            iyd  = y
            xm  = (x - dfloat(ixd))*60.d0
            ixm = xm
            ym  = (y - dfloat(iyd))*60.d0
            iym = ym
            xs  = (xm - dfloat(ixm))*60.d0
            ys  = (ym - dfloat(iym))*60.d0
c            
            slon(nstat,1) = dfloat(ixd)
            slon(nstat,2) = dfloat(ixm)
            slon(nstat,3) = xs
            slat(nstat,1) = dfloat(iyd)
            slat(nstat,2) = dfloat(iym)
            slat(nstat,3) = ys
            altd(nstat)   = alt
            azmth(nstat)  = azm*rad
c
            goto 9
c
         endif
c
c -----< 1-2: STAPOS card >-----
c
         if (buf(1:6).eq.'STAPOS') then
c
            nstat = nstat + 1
c
            if (nstat.gt.10) then
               print*,'!!! Error : STAPOS card'
               print*,'!!!         Number of station should be',
     +                ' smaller than 10.'
               stop 1
            endif
c
            buf2 = buf(7:100)
c
            read(buf2,*) site, ixd, ixm, xs, iyd, iym, ys, alt, azm
            sname(nstat)  = site
            slat(nstat,1) = dfloat(iyd)
            slat(nstat,2) = dfloat(iym)
            slat(nstat,3) = ys
            slon(nstat,1) = dfloat(ixd)
            slon(nstat,2) = dfloat(ixm)
            slon(nstat,3) = xs
            altd(nstat)   = alt
            azmth(nstat)  = azm*rad
c
            if (slat(nstat,1).ge.0.d0) then
               y = slat(nstat,1) + slat(nstat,2)/60.d0
     +           + slat(nstat,3)/3600.d0
            else
               y = slat(nstat,1) - slat(nstat,2)/60.d0
     +           - slat(nstat,3)/3600.d0
            endif
c
            x = slon(nstat,1) + slon(nstat,2)/60.d0
     +        + slon(nstat,3)/3600.d0
            if (x.lt.0.d0) then
               x = x + 360.d0
            endif
c
            if (x.gt.360.d0) then
               print*,'!!! Error : STAPOS card'
               print*,'!!!         Invalid longitude for site ',site
               stop 1
            endif
            if ( (y.lt.-90.d0).or.(y.gt.90.d0) ) then
               print*,'!!! Error : STAPOS card'
               print*,'!!!         Invalid latitude for site ',site
               stop 1
            endif
c
            sln(nstat) = x
            slt(nstat) = y
c
         endif
c
 9       continue
c
c -----< 2: KIND card >-----
c
         if (buf(1:4).eq.'KIND') then
c
            do i = 5,100
c
               do j = 1,6
                  if (buf(i:i+1).eq.kn(j)) then
                     nkind = nkind + 1
                     ikind0(nkind) = j
                  endif
               enddo
c
               if (nkind.ne.nkind0) then
                  jj = nkind0
                  do j = 1,jj
                     if (ikind0(j).eq.ikind0(nkind)) then
                        nkind = nkind - 1
                        goto 29
                     endif
                  enddo
               endif
c
 29            nkind0 = nkind
c
            enddo
c            
         endif
c
c -----< 3: WAVE card >-----
c
         if (buf(1:4).eq.'WAVE') then
c
            do i = 5,100
c
               do jw = 1,21
                  wtest3 = wn(jw)
                  wn2    = wtest3(1:2)
                  wtest1 = ' '//wn(jw)
                  wtest2 = ','//wn(jw)
                  wtest3 = ' '//wn2
                  wtest4 = ','//wn2
                  if ( (buf(i:i+3).eq.wtest1) .or.
     +                 (buf(i:i+3).eq.wtest2) .or.
     +                 (buf(i:i+2).eq.wtest3) .or.
     +                 (buf(i:i+2).eq.wtest4)     ) then
                     nwave = nwave + 1
                     ncnt0(nwave) = jw
                  endif
               enddo
c
               if  (buf(i:i+5).eq.'MAJOR8') then
                  do kw = 1,8
                     nwave = nwave + 1
                     ncnt0(nwave) = kw
                  enddo
               endif
c
               if  (buf(i:i+5).eq.'SHORTP') then
                  do kw = 1,16
                     nwave = nwave + 1
                     ncnt0(nwave) = kw
                  enddo
               endif
c
               if  (buf(i:i+4).eq.'LONGP') then
                  do kw = 17,21
                     nwave = nwave + 1
                     ncnt0(nwave) = kw
                  enddo
               endif
c
               if  (buf(i:i+2).eq.'ALL') then
                  do kw = 1,21
                     nwave = nwave + 1
                     ncnt0(nwave) = kw
                  enddo
               endif
c
               do j = 1,nwave
                  do jj = j+1,nwave
                     if (ncnt0(j).eq.ncnt0(jj)) then
                        do jjj = jj+1,nwave
                           ncnt0(jjj-1) = ncnt0(jjj)
                        enddo
                        ncnt(nwave) = 0
                        nwave = nwave - 1
                     endif
                  enddo
               enddo
c
            enddo
c            
         endif
c
c -----< 4: GREENF card >-----
c
         if (buf(1:6).eq.'GREENF') then
c
            buf2 = buf(7:100)
            read(buf2,*) igrn
c
            if ( (igrn.lt.1).or.(igrn.gt.5) ) then
               print*,'!!! Error : GREENF card.'
               print*,'!!!         The value should be 1,2,3,4 or 5.'
               stop 4
            endif
c
         endif
c
c -----< 5: POINTL card >-----
c
         if (buf(1:6).eq.'POINTL') then
c
            do i = 7,100
c     
               if (buf(i:i+1).eq.'ON') then
                  Lpoint = .true.
                  goto 59
               endif
               if (buf(i:i+2).eq.'OFF') then
                  Lpoint = .false.
                  goto 59
               endif
c
            enddo
c
 59         continue
c
         endif
c
c -----< 6: MESH1 card >-----
c
         if (buf(1:5).eq.'MESH1') then
c
            do i = 6,100
c     
               if (buf(i:i+1).eq.'ON') then
                  Lmesh1 = .true.
                  goto 69
               endif
               if (buf(i:i+2).eq.'OFF') then
                  Lmesh1 = .false.
                  goto 69
               endif
c
            enddo
c
 69         continue
c
         endif
c
c -----< 7: MESH2 card >-----
c
         if (buf(1:5).eq.'MESH2') then
c
            do i = 6,100
c     
               if (buf(i:i+1).eq.'ON') then
                  Lmesh2 = .true.
                  goto 79
               endif
               if (buf(i:i+2).eq.'OFF') then
                  Lmesh2 = .false.
                  goto 79
               endif
c
            enddo
c
 79         continue
c
         endif
c
c -----< 8: MESH3 card >-----
c
         if (buf(1:5).eq.'MESH3') then
c
            do i = 6,100
c     
               if (buf(i:i+1).eq.'ON') then
                  Lmesh3 = .true.
                  goto 89
               endif
               if (buf(i:i+2).eq.'OFF') then
                  Lmesh3 = .false.
                  goto 89
               endif
c
            enddo
c
 89         continue
c
         endif
c
c -----< 9: INTEGA card >-----
c
         if (buf(1:6).eq.'INTEGA') then
c
            buf2 = buf(7:100)
c
            read(buf2,*) area1, area2
c
            if (area1.gt.area2) then
               print*,'!!! Error : INTEGA card.'
               print*,'!!!         area1 should be smaller than area2.'
               stop 9
            endif
c
            if (area1.lt.0.d0) then
               print*,'!!! Error : INTEGA card.'
               print*,'!!!         area1 should be positive.'
               stop 9
            endif
c
            if (area2.gt.180.d0) then
               print*,'!!! Error : INTEGA card.'
               print*,'!!!         area2 should be smaller than 180.'
               stop 9
            endif
c
            area1 = area1*rad
            area2 = area2*rad
c 
         endif
c
c -----< 10: MAPOUT card >-----
c
         if (buf(1:6).eq.'MAPOUT') then
c
            Lmapout = .true.
            buf2   = buf(7:100)
c
            read(buf2,*) isw,xb1,xb2,yb1,yb2
c
            if (xb1.ge.xb2) then
               print*,'!!! Error : MAPOUT card.'
               print*,'!!!         xb1 should be smaller than xb2.'
               stop 10
            endif
c
            if (yb1.ge.yb2) then
               print*,'!!! Error : MAPOUT card.'
               print*,'!!!         yb1 should be smaller than yb2.'
               stop 10
            endif
c
            if (isw.eq.1) then
               Lmapln = .true.
            else if (isw.eq.2) then
               Lmapln = .false.
            else
               print*,'!!! Error : MAPOUT card.'
               print*,'!!!         isw should be 1 or 2.'
               stop 10
            endif
c
            open(99,file=ftn99)
c
         endif
c
c -----< 11: MASSCON card >-----
c
         if (buf(1:7).eq.'MASSCON') then
c
            do i = 8,100
c     
               if (buf(i:i+1).eq.'ON') then
                  Lmascor = .true.
                  goto 119
               endif
               if (buf(i:i+2).eq.'OFF') then
                  Lmascor = .false.
                  goto 119
               endif
c
            enddo
c
 119         continue
c
         endif
c
c -----< 12: DELTAF card >-----
c
         if (buf(1:6).eq.'DELTAF') then
c
            buf2   = buf(7:100)
            read(buf2,*) idelta
c
            if ( (idelta.ne.1).and.(idelta.ne.2) ) then
               print*,'!!! Error : DELTAF card'
               print*,'!!!         The value should be 1 or 2.'
               stop 12
            endif
c
         endif
c
c -----< 13: BOUND12 card >-----
c
         if (buf(1:7).eq.'BOUND12') then
c
            buf2   = buf(8:100)
            read(buf2,*) abnd12
c
            if ( (abnd12.lt.0.d0) .or. (abnd12.gt.ab12mx) ) then
               print*,'!!! Error : BOUND12 card'
               print*,'!!!         The value should be between 0',
     +                ' and ',ab12mx
               stop 13
            endif
c
         endif
c
c -----< 14: BOUND23 card >-----
c
         if (buf(1:7).eq.'BOUND23') then
c
            buf2   = buf(8:100)
            read(buf2,*) abnd23
c
            if ( (abnd23.lt.0.d0) .or. (abnd23.gt.ab23mx) ) then
               print*,'!!! Error : BOUND23 card'
               print*,'!!!         The value should be between 0',
     +                ' and ',ab23mx
               stop 14
            endif
c
         endif
c
c -----< 15: PATAN2 card >-----
c
         if (buf(1:6).eq.'PATAN2') then
c
            do i = 7,100
c     
               if (buf(i:i+1).eq.'ON') then
                  Latan2 = .true.
                  goto 159
               endif
               if (buf(i:i+2).eq.'OFF') then
                  Latan2 = .false.
                  goto 159
               endif
c
            enddo
c
 159        continue
c
         endif
c
c -----< 16: ANELAST card >-----
c
         if (buf(1:7).eq.'ANELAST') then
            buf2   = buf(8:100)
            read(buf2,*) anel1, anel2
            anel1 = anel1*0.01  ! in percent
         endif
c
c -----< 17: VERBOUS card >-----
c
         if (buf(1:7).eq.'VERBOUS') then
c
            do i = 8,100
c     
               if (buf(i:i+1).eq.'ON') then
                  Lverbo = .true.
                  goto 179
               endif
               if (buf(i:i+2).eq.'OFF') then
                  Lverbo = .false.
                  goto 179
               endif
c
            enddo
c
 179        continue
c
         endif
c
c -----< 18: PREDICT card >-----
c
         if (buf(1:7).eq.'PREDICT') then
c
            Lpred = .true.
c
            read(buf(8:100),*) iprcmp, prstim, pretim, prdt
c
            tmp    = prstim*1.d-4
            ipsymd = tmp
            tmp    = (prstim - dfloat(ipsymd)*1.d+4)*1.d+2
            ipshms = tmp
            tmp    = pretim*1.d-4
            ipeymd = tmp
            tmp    = (pretim - dfloat(ipeymd)*1.d+4)*1.d+2
            ipehms = tmp
c
            iprdt = prdt
c
            prdt = dfloat(iprdt)
c
            call mjdymd(prsmjd, ipsymd, ipshms, 1)
            call mjdymd(premjd, ipeymd, ipehms, 1)
c            
            if ((prsmjd.lt.15079.d0).or.(prsmjd.gt.88127.d0)) then
               print*,'!!! Error : PREDICT card.'
               print*,'!!!         Start time = ',ipsymd,ipshms
               print*,'!!!         Start time should be within Mar.',
     +                ' 1, 1900 and Feb. 28, 2100'
               stop 18
            endif
c
            if ((premjd.lt.15079.d0).or.(premjd.gt.88127.d0)) then
               print*,'!!! Error : PREDICT card.'
               print*,'!!!         End time = ',ipeymd,ipehms
               print*,'!!!         End time should be within Mar.',
     +                ' 1, 1900 and Feb. 28, 2100'
               stop 18
            endif
c
            if (prsmjd.gt.premjd) then
               print*,'!!! Error : PREDICT card.'
               print*,'!!!         Start time = ',ipsymd,ipshms
               print*,'!!!         End   time = ',ipeymd,ipehms
               print*,'!!!         End time precedes start time.'
               stop 18
            endif
c
            if (prdt.lt.1.d0) then
               print*,'!!! Error : PREDICT card.'
               print*,'!!!         Time step  = ', iprdt
               print*,'!!!         Time step should be positive ',
     +                'integer.'
               stop 18
            endif
c
         endif
c
c -----< 19: PREXFL card >-----
c
         if (buf(1:6).eq.'PREXFL') then
c
            Lprein = .true.
            read(buf(7:100),*) prein
c
            if (prein.eq.' ') then
               print*,'!!! Error : PREXFL card.'
               print*,'!!! Specify external file name.'
               stop 19
            endif
c
         endif
c
c -----< 20: PREFMT card >-----
c
         if (buf(1:6).eq.'PREFMT') then
c
            read(buf(7:100),*) iprfm1,iprfm2
c
            if ((iprfm1.lt.1).or.(iprfm1.gt.5)) then
               print*,'!!! Error : PREFMT card.'
               print*,'!!! First number should be between 1 and 5.'
               stop 20
            endif
c
            if ((iprfm2.lt.1).or.(iprfm2.gt.4)) then
               print*,'!!! Error : PREFMT card.'
               print*,'!!! Second number should be between 1 and 4.'
               stop 20
            endif
c
         endif
c
c -----< 21: GTIME card >-----
c
         if (buf(1:5).eq.'GTIME') then
c
            read(buf(6:100),*)igy, igm, igd
c
            igtime = 1
c
            if ( (igy.lt.1900).or.(igy.gt.2100) ) then
               print*,'!!! Error : GTIME card.'
               print*,'!!! igy should be between 1900 and 2100'
               stop 21
            endif
c
            if ( (igm.lt.1).or.(igm.gt.12) ) then
               print*,'!!! Error : GTIME card.'
               print*,'!!! igm should be between 1 and 12'
               stop 21
            endif
c
            if ( (igd.lt.1).or.(igd.gt.31) ) then
               print*,'!!! Error : GTIME card.'
               print*,'!!! igm should be between 1 and 31'
               stop 21
            endif
c
         endif
c
c -----< 22: DATADIR card >-----
c
         if ( (buf(1:7).eq.'DATADIR') ) then
c
            do j = 8,100
               if (buf(j:j).ne.' ') then
                  datdir = buf(j:87)
                  goto 229
               endif
            enddo
c
         endif

 229     continue
c
c -----< 23: BOUND34 card >-----
c
         if (buf(1:7).eq.'BOUND34') then
c
            buf2   = buf(8:100)
            read(buf2,*) abnd34
c
            if ( (abnd34.lt.0.d0) .or. (abnd34.gt.ab34mx) ) then
               print*,'!!! Error : BOUND34 card'
               print*,'!!!         The value should be between 0',
     +                ' and ',ab34mx
               stop 23
            endif
c
         endif
c
c -----< 24: MESH4 card >-----
c
         if (buf(1:5).eq.'MESH4') then
c
            do i = 6,100
c     
               if (buf(i:i+1).eq.'ON') then
                  Lmesh4 = .true.
                  goto 249
               endif
               if (buf(i:i+2).eq.'OFF') then
                  Lmesh4 = .false.
                  goto 249
               endif
c
            enddo
c
 249         continue
c
         endif
c
c -----< 25: UNIT6 card >-----
c
         if (buf(1:5).eq.'UNIT6') then
c     
            buf2 = buf(6:100)
c
            read(buf2,'(a80)') ftn06
c
            write(6,259) ftn06
 259        format(' Output file = ',a80)
c
            open(6,file=ftn06)
c
         endif
c
c -----< 26: UNIT20 or PREOUT card >-----
c
         if ( (buf(1:6).eq.'UNIT20') .or. (buf(1:6).eq.'PREOUT') ) then
c     
            buf2 = buf(7:100)
c
            read(buf2,'(a80)') ftn20
            buf3 = ftn20
            do ic1 = 1,80
               if (buf3(ic1:ic1).ne.' ') goto 268
            enddo
c
 268        do ic2 = 80,1,-1
               if (buf3(ic2:ic2).ne.' ') goto 269
            enddo
c
 269        ftn20 = buf3(ic1:ic2)
c
            Lftn20 = .true.
c
         endif
c
c -----< 27: PRE186 card >-----
c
         if (buf(1:6).eq.'PRE186') then
c     
            do i = 7,100
c     
               if (buf(i:i+1).eq.'ON') then
                  Lpr186 = .true.
                  goto 279
               endif
               if (buf(i:i+2).eq.'OFF') then
                  Lpr186 = .false.
                  goto 279
               endif
c
            enddo
c
 279        continue
c
         endif
c
c -----< 28: FULLMESH card >-----
c
         if (buf(1:8).eq.'FULLMESH') then
c
            do i = 9,100
c     
               if (buf(i:i+1).eq.'ON') then
                  Lfullm = .true.
                  goto 289
               endif
               if (buf(i:i+2).eq.'OFF') then
                  Lfullm = .false.
                  goto 289
               endif
c
            enddo
c
 289        continue
c
         endif
c
c -----< 29: OMODEL card >-----
c
         if (buf(1:6).eq.'OMODEL') then
c
            do j = 7,100
               if (buf(j:j).ne.' ') then
                  omodel = buf(j:86)
                  goto 299
               endif
            enddo
c
         endif
c
 299     continue
c
c -----< END card >-----
c
      enddo                     ! Until END card
c     
      do i = 1,nwave
         ncnt(i) = ncnt0(i)
      enddo
c
      do i = 1,nkind
         ikind(i) = ikind0(i)
      enddo
c
c -----< Error reports >-----
c
 900  if (nstat.lt.1) then
         print*,' !!! Error : STAPOS or STAPOSD card is mandatory.'
         stop
      endif
c
      if (nkind.lt.1) then
         print*,' !!! Error : KIND card is mandatory.'
         stop
      endif
c
      if (nwave.lt.1) then
         print*,' !!! Error : WAVE card is mandatory.'
         stop
      endif
c
      if ( (.not.Lpred).and.(Lprein) ) then
         print*,' !!! Error : PREXFL card must be used with ',
     +          'PREDICT card.'
         stop
      endif
c
      if (abnd12.lt.abnd23) then
         print*,' !!! Error : BOUND12 should be larger than ',
     +          'BOUND23.'
      endif
c
      if (abnd23.lt.abnd34) then
         print*,' !!! Error : BOUND23 should be larger than ',
     +          'BOUND34.'
      endif
c
c -----< Standard output >----
c
c ***** Cards read *****
c
      if (Lverbo) then
c
         write(6,798)
 798     format('-------------------------------------------',
     +          '< INPUT CARD >',
     +          '------------------------------------------- No.')
c
         do i = 1,nbuf
            write(6,'(1x,a100,i3)') bufbuf(i), i
         enddo
c
         write(6,799)
 799     format('----------------------------------------',
     +          '< INPUT CARD (END) >',
     +          '----------------------------------------')
c
         write(6,*)
         write(6,*)
         write(6,890)
 890     format('--------------------< Configuration >',
     +          '--------------------')
c
c ***** Station info *****
c
         do i = 1,nstat
c
            write(6,800) i
            write(6,801) sname(i)
            write(6,802) sln(i)
            write(6,803) (slon(i,j),j=1,3)
            write(6,804) slt(i)
            write(6,803) slat(i,1),(dabs(slat(i,j)),j=2,3)
            write(6,805) altd(i), azmth(i)/rad
c
 800        format(' Station ',i2)
 801        format(4x,'Name : ',a10)
 802        format(4x,'Longitude = ',f10.6,' (deg)')
 803        format(14x,'= ',f5.1,' (deg), ',f5.1,' (min), ',f8.4,
     +             ' (sec)')
 804        format(4x,'Latitude  = ',f10.6,' (deg)')
 805        format(4x,'Altitude  = ',f7.2,' (m), Azimuth = ',
     +             f7.2,' (deg)')
c
         enddo
c
c ***** Kind info *****
c
         write(6,806) (kn(ikind(i)),i=1,nkind)
 806     format(' Kind                :',6a4)
c
c ***** Wave info *****
c
         nrem = mod(nwave,8)
         nitr = nwave/8
c
         if (nrem.eq.0) then
            do kw = 1,nitr
               kpos = (kw-1)*8 + 1
               write(6,807) (wn(ncnt(i)),i=kpos,kpos+7)
            enddo
         else
            do kw = 1,nitr
               kpos = (kw-1)*8 + 1
               write(6,807) (wn(ncnt(i)),i=kpos,kpos+7)
            enddo
            write(6,807) (wn(ncnt(i)),i=nitr*8+1,nitr*8+nrem)
         endif
 807     format(' Tidal waves         : ',8a4)
c
c ***** Prediction mode only. Suppress calculation mode output  *****
c
         if (Lprein) goto 825
c
c ***** Integ. area *****
c 
         write(6,808) area1/rad, area2/rad
 808     format(' Integration area    : ',f5.1,' - ',f5.1,' (deg)')
c
c ***** 1st order mesh *****
c     
         if (.not. Lmesh1) then
            write(6,815)
 815        format(' MESH1 OFF           : 1st order mesh not used.')
         endif
c
c ***** 2nd order mesh *****
c
         if (.not. Lmesh2) then
            write(6,816)
 816        format(' MESH2 OFF           : 2nd order mesh not used.')
         endif
c
c ***** 3rd order mesh *****
c
         if (Lmesh3) then
            write(6,817)
 817        format(' MESH3 ON            : 3rd order mesh to be used.')
         endif
c
c ***** 4th order mesh *****
c
         if (Lmesh4) then
            write(6,836)
 836        format(' MESH4 ON            : 4th order mesh to be used.')
         endif
c
c ***** 2nd mesh region *****
c
         write(6,811) abnd12
 811     format(' 2nd mesh region     : Within ',f5.1,' (deg)')
c
c ***** 3rd mesh region *****
c
         write(6,822) abnd23
 822     format(' 3rd mesh region     : Within ',f5.1,' (deg)')
c
c ***** 4th mesh region *****
c
         if (Lmesh4) then
            write(6,838) abnd34
 838        format(' 4th mesh region     : Within ',f5.1,' (deg)')
         endif
c
c ***** Grid mesh output region *****
c
         if (Lmapout) then
            write(6,809) xb1, xb2, yb1, yb2
 809        format(' Grid mesh output    : ',f5.1,'E - ',f5.1,
     +             'E, ',f5.1,'N - ',f5.1,'N')
         endif
c
c ***** Green's function info *****
c
         if (igrn.eq.1) then
            write(6,812)
 812        format(' Green''s function    : Green''s function based',
     +             ' on G-B model')
         else if (igrn.eq.2) then
            write(6,820)
 820        format(' Green''s function    : Green''s function based',
     +             ' on 1066A model')
         else if (igrn.eq.3) then
            write(6,842)
 842        format(' Green''s function    : Green''s function based',
     +             ' on PREM model')
         else if (igrn.eq.4) then
            write(6,843)
 843        format(' Green''s function    : Green''s function based',
     +             ' on 1066A model and PREM Q [Gravity]')
         else
            write(6,821)
 821        format(' Green''s function    : Complex Green''s functi',
     +             'on based on G-B model and PREM Q [Gravity]')
         endif
c     
c ***** Point load *****
c
         if (Lpoint) then
            write(6,818)
 818        format(' POINTL ON           : Point load only.')
         endif
c
c ***** Mass conservation *****
c
         if (Lmascor) then
            write(6,819)
 819        format(' MASSCON ON          : Mass conservation procedure',
     +             ' conducted.')
         endif
c
c ***** Phase print out style *****
c
         if (Latan2) then
            write(6,823)
 823        format(' PATAN2  ON          : Phases are printed between',
     +             ' -180 deg and 180 deg.')
         endif
c
c ***** Delta factor info *****
c
         do i = 1,nkind
            if (ikind(i).eq.3) then
               if (idelta.eq.1) then
                  write(6,813) 
               else
                  write(6,814)
               endif
            endif
         enddo
 813     format(' Delta factor        : ',
     +          'Wahr''s delta factor for gravity.')
 814     format(' Delta factor        : ',
     +          'Dehant''s delta factor for gravity.')
c
c ***** Anelasticity of the gravity body tide *****
c
         if ( (anel1.ne.0.d0) .or. (anel2.ne.0.d0) ) then
            write(6,824) anel1*100.d0, anel2
 824        format(' Anelasticity        : Real part = ',f10.7,
     +             '%, Imaginary part = ',f10.7)
c
         endif
c
c ***** GTIME *****
c
         if (igtime.eq.1) then
c
            do i = 1,nkind
               if (ikind(i).eq.3) then
                  write(6,834) igy, igm, igd
 834              format(' Mearsurement center time : ',i4,
     +                   '/',i2,'/',i2)
               endif
            enddo
c
         endif
c
c ***** DATADIR *****
c
         if (datdir.ne.'./data/') then
            write(6,835) datdir
         endif
 835     format(' DATADIR             : ',a80)
c
 825     continue
c
c ***** Prediction *****
c
         if (Lpred) then
c
            write(6,826) prtxt(iprcmp)
 826        format(' Prediction component  = ',a80)
c
            iy   = ipsymd/10000
            im   = (ipsymd - iy*10000)/100
            id   = (ipsymd - iy*10000 - im*100)
            ih   = ipshms/10000
            imin = (ipshms - ih*10000)/100
            write(6,827) iy,im,id,ih,imin,prsmjd
 827        format(' Prediction start time = ',i4,'/',i2,'/',i2,1x,
     +             i2,':',i2,', MJD = ',f12.5)
c
            iy   = ipeymd/10000
            im   = (ipeymd - iy*10000)/100
            id   = (ipeymd - iy*10000 - im*100)
            ih   = ipehms/10000
            imin = (ipehms - ih*10000)/100
            write(6,828) iy,im,id,ih,imin,premjd
 828        format(' Prediction end   time = ',i4,'/',i2,'/',i2,1x,
     +             i2,':',i2,', MJD = ',f12.5)
c
            write(6,829) iprdt
 829        format(' Prediction time step  =',i5,' (min)')
c
         endif
c
c ***** Prediction output format *****
c
         if (Lpred) then
c
            write(6,830) pftxt1(iprfm1)
 830        format(' Prediction output time unit  = ',a80)
c
            write(6,831) pftxt2(ikind(1),(iprfm2+1)/2)
            itmp = mod(iprfm2,2)
            if (itmp.eq.0) itmp = 2
            write(6,832) pftxt3(ikind(1),itmp)
 831        format(' Prediction output sign       = ',a80)
 832        format(' Prediction output unit       = ',a80)
c
         endif
c
c ***** UNIT20 or PREOUT *****
c
         if (Lpred .and. Lftn20 .and. (ftn20.ne.' ') ) then
            write(6,837) ftn20
 837        format(' Prediction output file       = ',a80)
            open(20,file=ftn20)
         endif
c
c ***** External file for prediction *****
c
         if (Lprein) then
c
            write(6,833) prein
 833        format(' External file for prediction = ',a80)
c
         endif
c
c ***** END *****
c
         write(6,899)
 899     format(' -----------------------------',
     +          '--------------------------')
         write(6,*)
         write(6,*)
c
      endif ! Verbous mode or not
c
      return
      end
c
