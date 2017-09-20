c$predic
c----------------------------------------------------------------
      subroutine predic(iu, nstat, nwave, nkind, ikind)
c----------------------------------------------------------------
c
      implicit double precision (a-h,o-z)
c
      Logical Lpr186
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
      common /comp/   ncomp(6)
      common /const/  rearth, earthm, gravct, pi , rad, deg,
     +                dens  , rls1  , rls2  , egv, elp
      common /predr/  prsmjd, premjd, prdt, prein
      common /predi/  iprfm1, iprfm2, iprcmp, Lpr186
      common /stat99/ slat(10,3), slon(10,3),
     +                altd(10), azmth(10), slt(10), sln(10)
      common /wavei/  ncnt(21), isp(21)
      common /waver/  xlambda(21)
      common /wavec/  wn(21)
c
      character*80 prein
      character*3  wn
c
      dimension ikind(6)
      dimension arg(21), arg2(21), afac(21), tide(6)
      dimension tfac(4), ofac(6,4)
c
      data tfac /86400.d0, 3600.d0, 60.d0, 1.d0/ 
      data ofac / 1.d0 ,  1.d0 ,  1.d0 ,  1.d0 ,  1.d0 ,  1.d0 ,
     +            1.d+3,  1.d+3,  1.d+8,  1.d+9,  1.d+9,  1.d+9,
     +           -1.d0 , -1.d0 , -1.d0 , -1.d0 , -1.d0 , -1.d0 ,
     +           -1.d+3, -1.d+3, -1.d+8, -1.d+9, -1.d+9, -1.d+9/
      data afac /0.03711d0, 0.00224d0, 0.13567d0, 0.18866d0,
     +           0.03729d0, 0.01125d0, 0.29810d0, 0.18863d0,
     +           0.20067d0, 0.01983d0, 0.64057d0, 0.03733d0,
     +           0.03735d0, 0.03730d0, 0.03680d0, 0.00154d0,
     +           0.41452d0, 0.41461d0, 0.06563d0, 0.02473d0,
     +           0.00085d0/
c
      data eps /1.d-5/
c
c-----------------------------------------------------------------------
c
      if (nstat.ne.1) then
c
         print*,'### Warning : Number of station is ',nstat
         print*,'###           The result is output for the',
     +          ' first station only.'
c
      endif
c
      if (nkind.ne.1) then
c
         print*,'### Warning : Number of kind is ',nkind
         print*,'###           The result is output for the',
     +          ' first kind only.'
c
      endif
c
c -----< Local phase to Greenwich phase (in radian) >-----
c      
      k = ikind(1)
c
      do iwave = 1,nwave
c
         iw   = ncnt(iwave)
         phsc = sln(1)*xlambda(iw)
c
         do nc = 1,ncomp(k)
c
            phsea(k,nc,1,iw) = (phsea(k,nc,1,iw) - phsc)*rad
            phsoa(k,nc,1,iw) = (phsoa(k,nc,1,iw) - phsc)*rad
            phsta(k,nc,1,iw) = (phsta(k,nc,1,iw) - phsc)*rad
c
         enddo
c
      enddo
c
c -----< calculate tide >-----
c
      nstep = ( (premjd - prsmjd + eps)*1440.d0 )/prdt + 1
      time  = 0.d0
c
      do itime = 1,nstep
c
         xmjd = prsmjd + time/86400.d0
         call astro(arg, arg2, xmjd)
c
         do nc = 1,ncomp(k)
c
            tide(nc) = 0.d0
c
            do iwave = 1,nwave
c
               iw      = ncnt(iwave)
               past    = arg (iw)  ! in radian
               past186 = arg2(iw)  ! in radian
c     
               if (iprcmp.eq.1) then
c     
                  as = ampst(k,nc,1,iw)
                  ao = ampot(k,nc,1,iw)
                  ps = phsea(k,nc,1,iw)
                  po = phsoa(k,nc,1,iw)
c
                  tide(nc) = tide(nc) + as*dcos(past-ps)
                  tide(nc) = tide(nc) + ao*dcos(past-po)
                  if (Lpr186) then
                     tide(nc) = tide(nc) + as*afac(iw)*dcos(past186-ps)
                     tide(nc) = tide(nc) + ao*afac(iw)*dcos(past186-po)
                  endif
c     
               else if (iprcmp.eq.2) then
c     
                  as = ampst(k,nc,1,iw)
                  ps = phsea(k,nc,1,iw)
                  tide(nc) = tide(nc) + as*dcos(past-ps)
                  if (Lpr186) then
                     tide(nc) = tide(nc) + as*afac(iw)*dcos(past186-ps)
                  endif
c     
               else
c
                  ao = ampot(k,nc,1,iw)
                  po = phsoa(k,nc,1,iw)
                  tide(nc) = tide(nc) + ao*dcos(past-po)
                  if (Lpr186) then
                     tide(nc) = tide(nc) + ao*afac(iw)*dcos(past186-po)
                  endif
c     
               endif
c
            enddo               ! nc
c
         enddo                  ! iwave
c
         do nc = 1,ncomp(k)
            tide(nc) = tide(nc)*ofac(k,iprfm2)
         enddo
c
         if (iprfm1.lt.5) then
c
            otime = time/tfac(iprfm1)
c
            if (mod(iprfm2,2).eq.1) then
               write(iu,101) otime,(tide(nc),nc=1,ncomp(k))
 101           format(f18.5,6d12.4)
            else
               write(iu,102) otime,(tide(nc),nc=1,ncomp(k))
 102           format(f18.5,6f12.4)
            endif
c
         else
c
            call mjdymd(xmjd, iymd, ihms, 2)
c
            iy   = iymd/10000
            im   = (iymd - iy*10000)/100
            id   = (iymd - iy*10000 - im*100)
            ih   = ihms/10000
            imin = (ihms - ih*10000)/100
c
            if (mod(iprfm2,2).eq.1) then
               write(iu,103) iy,im,id,ih,imin,(tide(nc),nc=1,ncomp(k))
 103           format(2x,i4,'/',i2.2,'/',i2.2,1x,i2.2,':',i2.2,6d12.4)
            else
               write(iu,104) iy,im,id,ih,imin,(tide(nc),nc=1,ncomp(k))
 104           format(2x,i4,'/',i2.2,'/',i2.2,1x,i2.2,':',i2.2,6f12.4)
            endif
c
         endif
c
         time = time + prdt*60.d0 ! Note that w is in rad/sec
c                                 ! and prdt is in minute.
c     
      enddo                     ! itime
c
      return
      end

