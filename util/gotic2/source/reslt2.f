c$reslt2
c------------------------------------------------------------------
      subroutine reslt2(is, iw ,k)
c------------------------------------------------------------------
c
c   FOR PHASE ANGLE OF LOADING TIDE, THE RESULT OF CONVOLUTION INTEGRAL
c   USING THE SCHWIDERSKI'S MODEL GIVES PHASE RELATIVE TO COS-ARGUMENT
c   OF OCEANIC TIDE, E.I. TO THAT OF TIDAL POTENTIAL. THIS PHASE IS
c   GIVEN AS 'PHSOA'. ON THE OTHER HAND, 'PHSOR' IS PHASE OF LOADING
c   TIDE RELATIVE TO THE EQUILIBRIUM TIDE. FOLLOWING TO CONVENTION IN
c   OCEAN TIDE STUDY, WE USE HERE PLUS SIGN TO REPRESENT LAG IN PHASE.
c   THUS, IF 'PHSOR-PHSOA' GIVES POSITIVE VALUE, IT MEANS LAGGING IN
c   EQUILIBRIUM TIDE TO TIDAL POTENTIAL.
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
      common /stat99/ slat(10,3), slon(10,3),
     +                altd(10), azmth(10), slt(10), sln(10)
      common /wavei/  ncnt(21), isp(21)
      common /waver/  xlambda(21)
      common /wavec/  wn(21)
c
      character*3 wn
c
      dimension camp(6), samp(6)
c
      data eps /1.d-40/
c
      ncmp = ncomp(k)
c
      call stide (is, k, ncnt(iw), camp, samp)
c
      do nc = 1,ncmp
c
c -----< Solid Earth tide >-----
c
         phser(k,nc,is,iw) = 0.0d0 ! by definition
         ampst(k,nc,is,iw) = dsqrt(camp(nc)*camp(nc)
     +                           + samp(nc)*samp(nc))
c
         if (ampst(k,nc,is,iw).lt.eps) then
            phsea(k,nc,is,iw) = 0.0d0
         else
            phsea(k,nc,is,iw) = datan2(samp(nc),camp(nc))*deg
         endif
c
         call refphs(phsea(k,nc,is,iw))
c
c -----< Ocean loading tide >-----
c
         ampot(k,nc,is,iw) = amps(5,k,nc,is,iw)
         phsoa(k,nc,is,iw) = phsl(5,k,nc,is,iw)
c
         phsor(k,nc,is,iw) = phsoa(k,nc,is,iw) - phsea(k,nc,is,iw)
         call refphs(phsor(k,nc,is,iw))
c
c -----< Total tides (solid + load) >-----
c
         pe = phsea(k,nc,is,iw)*rad
         ce = ampst(k,nc,is,iw)*dcos(pe)
         se = ampst(k,nc,is,iw)*dsin(pe)
         po = phsoa(k,nc,is,iw)*rad
         co = ampot(k,nc,is,iw)*dcos(po)
         so = ampot(k,nc,is,iw)*dsin(po)
         ct = ce + co
         st = se + so
c
         ampt(k,nc,is,iw) = dsqrt(ct*ct + st*st)
c
         if (ampt(k,nc,is,iw).lt.eps) then
            phsta(k,nc,is,iw) = 0.0d0
         else
            phsta(k,nc,is,iw) = datan2(st,ct)*deg
         endif
c     
         call refphs(phsta(k,nc,is,iw))
c     
         phstr(k,nc,is,iw) = phsta(k,nc,is,iw) - phsea(k,nc,is,iw)
         call refphs(phstr(k,nc,is,iw))
c     
      enddo                     ! nc
c
      return
      end
c
