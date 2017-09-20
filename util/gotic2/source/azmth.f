c$azmth
c------------------------------------------------------------------
      subroutine azmth (alat  , alon  , blat  , blon  , angl  ,
     +                  azmt                                   )
c------------------------------------------------------------------
c
      implicit double precision (a-h, o-z)
c
      common /const/  rearth, earthm, gravct, pi , rad, deg,
     +                dens  , rls1  , rls2  , egv, elp
c
      dlat = dabs(pi*0.5d0 - alat)
      dlon = dabs(alon - blon)
      azmt = 0.0d0
c
      if (angl.le.1.0d-7) return
c
      if (dlat.le.1.0d-7) return
c
      if (dlon.le.1.0d-7) then
         if (alat.gt.blat) then
            azmt = pi
         endif
         return
      endif
c
      arg = (dsin(blat) - dsin(alat)*dcos(angl))
     *    / (dcos(alat)*dsin(angl))
c
      if (arg.ge.1.0d0) then
         azmt = 0.0d0
         return
      else if (arg.le.-1.0d0) then
         azmt = pi
         return
      endif
c
      azmt = dacos(arg)
c
      dlon = alon - blon
      if (dlon.lt.0.d0) dlon = dlon + 2.d0*pi
      if (dlon.lt.pi) then
         azmt = -azmt
      endif
c
      return
      end
c
