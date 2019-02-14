c$setap
c----------------------------------------------------------------
      subroutine setap(iu, k, nc, is)
c----------------------------------------------------------------
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
      common /wavei/  ncnt(21), isp(21)
      common /waver/  xlambda(21)
      common /wavec/  wn(21)
c
      character*3     wn, cwave
      character*120   buf
c
c
c-----------------------------------------------------------------------
c
      write(6,605)
      write(6,601)
      write(6,602)
 605  format(' ')
 601  format('         Solid Earth Tide        Ocean Tide',
     +       '             Total')      
 602  format(' Wave   Amplitude  A-Phase   Amplitude  A-Phase',
     +       '   Amplitude  A-Phase')
c
      do jwave = 1,22
c
         read(iu,'(a120)') buf
c
         if (buf(2:4).ne.'   ') then
c
            if (buf(1:1).eq.' ') then
               read(buf,603) cwave, ast, pst, tmp,
     +                       aot, pot, tmp, att, ptt, tmp
 603           format(1x,a3,1x,3(3x,1pe13.4,2(0pf9.3)))
            else
               read(buf,604) cwave, ast, pst, tmp,
     +                       aot, pot, tmp, att, ptt, tmp
 604           format(a3,1x,3(3x,1pe13.4,2(0pf9.3))) ! For WINDOWS
            endif
c
            do iwave = 1,21
c
               iw = ncnt(iwave)
c
               if (cwave.eq.wn(iw)) then
c
                  ampst(k,nc,is,iw) = ast
                  phsea(k,nc,is,iw) = pst
                  ampot(k,nc,is,iw) = aot
                  phsoa(k,nc,is,iw) = pot
                  ampt (k,nc,is,iw) = att
                  phsta(k,nc,is,iw) = ptt
c
                  write(6,'(1x,a3,1x,3(1pe13.4,0pf8.3))')
     +                     wn(iw),ast,pst,aot,pot,att,ptt
c
               endif
c
            enddo
c     
         else
c
            return
c
         endif
c
      enddo
c
      return
      end
c


