c$getapj
c------------------------------------------------------------------
      subroutine getapj(xc    , yc    , ampj  , phsj  , mgmax ,
     +                  ngmax , hight , phase                  )
c------------------------------------------------------------------
c
      implicit double precision (a-h,o-z)
c
      common /const/  rearth, earthm, gravct, pi , rad, deg,
     +                dens  , rls1  , rls2  , egv, elp
      common /jmap/   xminj, xmaxj, yminj, ymaxj, gsizej, mendj, nendj
c
      dimension ampj(mgmax,ngmax)  , phsj(mgmax,ngmax)
      dimension wf(2,2),ag(2,2),pg(2,2)
c
      bia = 0.d0
      bip = 0.d0
      w0  = 0.d0
      dx  = gsizej
      dy  = gsizej
c
      m = int( (xc - xminj)/dx ) + 1.d0
      n = int( (ymaxj - yc)/dy ) + 1.d0
c
      ag(1,1) = ampj(m  ,n  )
      ag(2,1) = ampj(m+1,n  )
      ag(1,2) = ampj(m  ,n+1)
      ag(2,2) = ampj(m+1,n+1)
      pg(1,1) = phsj(m  ,n  )
      pg(2,1) = phsj(m+1,n  )
      pg(1,2) = phsj(m  ,n+1)
      pg(2,2) = phsj(m+1,n+1)
c
c -----< Fill ocean tide information if not defined >-----
c
      if ((ag(1,1).gt.9.998d0).and.(ag(2,1).gt.9.998d0).and.
     +    (ag(1,2).gt.9.998d0).and.(ag(2,2).gt.9.998d0)     ) then
c
         do iy = 0,-2,-1
            nn = n + iy
            if (nn.lt.1) nn = 1
            do ix = 0,-2,-1
               mm = m + ix
               if (mm.lt.1) mm = 1
               if (ampj(mm,nn).lt.9.998d0) then
                  ag(1,1) = ampj(mm,nn)
                  pg(1,1) = phsj(mm,nn)
                  goto 19
               endif
            enddo
         enddo
c
 19      do iy = 0,-2,-1
            nn = n + iy
            if (nn.lt.1) nn = 1
            do ix = 0,2
               mm = m + ix
               if (mm.gt.mgmax) mm = mgmax
               if (ampj(mm,nn).lt.9.998d0) then
                  ag(2,1) = ampj(mm,nn)
                  pg(2,1) = phsj(mm,nn)
                  goto 29
               endif
            enddo
         enddo
c
 29      do iy = 0,2
            nn = n + iy
            if (nn.gt.ngmax) nn = ngmax
            do ix = 0,-2,-1
               mm = m + ix
               if (mm.lt.1) mm = 1
               if (ampj(mm,nn).lt.9.998d0) then
                  ag(1,2) = ampj(mm,nn)
                  pg(1,2) = phsj(mm,nn)
                  goto 39
               endif
            enddo
         enddo
c
 39      do iy = 0,2
            nn = n + iy
            if (nn.gt.ngmax) nn = ngmax
            do ix = 0,2
               mm = m + ix
               if (mm.gt.mgmax) mm = mgmax
               if (ampj(mm,nn).lt.9.998d0) then
                  ag(2,2) = ampj(mm,nn)
                  pg(2,2) = phsj(mm,nn)
                  goto 49
               endif
            enddo
         enddo
c
 49      continue
c
      endif                     ! All of required 4 girds are defined or not 
c
      xm = xminj + (dfloat(m) - 1.d0)*dx
      ym = ymaxj - (dfloat(n) - 1.d0)*dy
c
      u1 = (xc - xm)/dx
      u2 = 1.d0 - u1
      v1 = (ym - yc)/dy
      v2 = 1.d0 - v1
c
      wf(1,1) = u2*v2
      wf(1,2) = u2*v1
      wf(2,1) = u1*v2
      wf(2,2) = u1*v1
c
      do iy = 1,2
         do ix = 1,2
c
            if (ag(ix,iy).lt.9.998d0) then
               cs  = ag(ix,iy)*dcos(pg(ix,iy)*rad)
               ss  = ag(ix,iy)*dsin(pg(ix,iy)*rad)
               bia = bia + cs*wf(ix,iy)
               bip = bip + ss*wf(ix,iy)
               w0 = w0 + wf(ix,iy)
            endif
c
         enddo   ! ix
      enddo      ! iy
c
      if (w0.gt.0.d0) then
c
         cp = bia/w0
         sp = bip/w0
         bia = dsqrt(cp*cp + sp*sp)
         if (dabs(cp).gt.0.d0) then
            bip = datan2(sp,cp)
         else if (sp.gt.0.d0) then
            bip = pi*0.5d0
         else
            bip = pi*1.5d0
         endif
         if (bip.lt.0.d0) bip = bip + 2.d0*pi
c
      else
c
         bia = 9.9999d0
         bip = 999.99d0
c
      endif
c
      hight = bia
      phase = bip
c
      return
      end
