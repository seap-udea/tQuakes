c$result
c------------------------------------------------------------------
      subroutine result(is, iw, k)
c------------------------------------------------------------------
c
      implicit double precision (a-h,o-z)
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
      common /wavei/  ncnt(21), isp(21)
      common /waver/  xlambda(21)
      common /wavec/  wn(21)
      common /stat99/ slat(10,3), slon(10,3),
     +                altd(10), azmth(10), slt(10), sln(10)
      common /sums/   sum(5,2,6), suma(5,2), sume(5,2)
c
      character*3 wn
c
      data eps /1.d-40/
c
c-----------------------------------------------------------------------
c
      ncmp = ncomp(k)
      phsc = sln(is)*xlambda(ncnt(iw))
c
c -----< Attraction >-----
c
      if (k.eq.3) then
c
         do m = 1,4             ! m stands for m-th order mesh.
c
            ampa(m,is,iw) = suma(m,1)*suma(m,1) + suma(m,2)*suma(m,2)
            ampa(m,is,iw) = dsqrt(ampa(m,is,iw))
c     
            if (ampa(m,is,iw).lt.eps) then
               phsa(m,is,iw) = 0.d0
            else
               phsa(m,is,iw) = datan2(suma(m,2),suma(m,1))*deg
            endif
c     
            call refphs(phsa(m,is,iw))
c
c -----< Loading >-----
c     
            ampe(m,is,iw) = sume(m,1)*sume(m,1) + sume(m,2)*sume(m,2)
            ampe(m,is,iw) = dsqrt(ampe(m,is,iw))
c     
            if (ampe(m,is,iw).lt.eps) then
               phse(m,is,iw) = 0.d0
            else
               phse(m,is,iw) = datan2(sume(m,2),sume(m,1))*deg
            endif
c     
            call refphs(phse(m,is,iw))
c     
         enddo                  ! m
c     
c -----< Attraction for total meshes >-----
c     
         suma(5,1) = suma(1,1) + suma(2,1) + suma(3,1) + suma(4,1)
         suma(5,2) = suma(1,2) + suma(2,2) + suma(3,2) + suma(4,2)
         ampa(5,is,iw) = suma(5,1)*suma(5,1) + suma(5,2)*suma(5,2)
         ampa(5,is,iw) = dsqrt(ampa(5,is,iw))
c     
         if (ampa(5,is,iw).lt.eps) then
            phsa(5,is,iw) = 0.d0
         else
            phsa(5,is,iw) = datan2(suma(5,2),suma(5,1))*deg
         endif
c
         call refphs(phsa(5,is,iw))
c
c -----< Loading for total meshe >-----
c
         sume(5,1) = sume(1,1) + sume(2,1) + sume(3,1) + sume(4,1)
         sume(5,2) = sume(1,2) + sume(2,2) + sume(3,2) + sume(4,2)
         ampe(5,is,iw) = sume(5,1)*sume(5,1) + sume(5,2)*sume(5,2)
         ampe(5,is,iw) = dsqrt(ampe(5,is,iw))
c     
         if (ampe(5,is,iw).lt.eps) then
            phse(5,is,iw) = 0.d0
         else
            phse(5,is,iw) = datan2(sume(5,2),sume(5,1))*deg
         endif
c     
         call refphs(phse(5,is,iw))
c
      endif ! Currently only for gravity
c
c -----< Amplitude and Phase for each order mesh >-----
c
      do nc = 1,ncmp
c
         do m = 1,4             ! m stands for m-th order mesh.
            
            amps(m,k,nc,is,iw) = dsqrt(sum(m,1,nc)*sum(m,1,nc)
     +                               + sum(m,2,nc)*sum(m,2,nc))
c
            if (amps(m,k,nc,is,iw).lt.eps) then
               phsg(m,k,nc,is,iw) = 0.0d0
            else
               phsg(m,k,nc,is,iw) = datan2(sum(m,2,nc),sum(m,1,nc))*deg
            endif
c
            call refphs(phsg(m,k,nc,is,iw))
c
         enddo                  ! m
c
c -----< Amplitude and Phase for total meshes >-----
c
         sum(5,1,nc) = sum(1,1,nc) + sum(2,1,nc)
     +               + sum(3,1,nc) + sum(4,1,nc)
         sum(5,2,nc) = sum(1,2,nc) + sum(2,2,nc)
     +               + sum(3,2,nc) + sum(4,2,nc)
         amps(5,k,nc,is,iw) = dsqrt(sum(5,1,nc)*sum(5,1,nc)
     +                            + sum(5,2,nc)*sum(5,2,nc))
c     
         if (amps(5,k,nc,is,iw).lt.eps) then
            phsg(5,k,nc,is,iw) = 0.0d0
         else
            phsg(5,k,nc,is,iw) = datan2(sum(5,2,nc),sum(5,1,nc))*deg
         endif
c     
         call refphs(phsg(5,k,nc,is,iw))
c
c -----< Convert Greenwich phase to local phase >-----
c
         do m = 1,5             ! m stands for m-th order mesh (5=total).
c     
            phsl(m,k,nc,is,iw) = phsg(m,k,nc,is,iw) + phsc
            call refphs(phsl(m,k,nc,is,iw))
c
         enddo                  ! m
c     
      enddo                     ! nc
c
      return
      end
c
