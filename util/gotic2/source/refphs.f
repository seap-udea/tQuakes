c$refphs
c----------------------------------------------------------------
      subroutine refphs(phase)
c----------------------------------------------------------------
c
      implicit double precision (a-h,o-z)
c
      Logical Lmapout, Lmesh1, Lmesh2, Lmesh3, Lmesh4, Lpoint, Lmascor
      Logical Latan2 , Lverbo, Lpred , Lprein
      Logical Lhavej , Loutj , Lfullm , Lmapln
c
      common /flag/   Lmapout, Lmesh1, Lmesh2, Lmesh3, Lmesh4, Lpoint,
     +                Lmascor, Latan2, Lverbo, Lpred , Lprein, Lhavej,
     +                Loutj  , Lmapln, Lfullm
c
      if (Latan2) then
c
         do while (phase .ge. 180.d0)
            phase = phase - 360.d0
         enddo
c
         do while (phase .lt. -180.d0)
            phase = phase + 360.d0
         enddo
c     
      else
c     
         do while (phase .ge. 360.d0)
            phase = phase - 360.d0
         enddo
c
         do while (phase .lt. 0.d0)
            phase = phase + 360.d0
         enddo
c
      endif
c
      return
      end
c
