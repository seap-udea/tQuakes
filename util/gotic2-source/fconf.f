c$fconf
c---------------------------------------------------------------
      subroutine fconf(tmapw  , tmapj , grn1  , grn2  , grn3  ,
     +                 grn4   , grn5  , fmap1 , datdir, omodel )
c---------------------------------------------------------------
c
      Logical       Lw2
      character*2   wn2
      character*3   wnl, wn3
      character*80  tmapw(21), tmapj(21)
      character*80  grn1, grn2, grn3, grn4, grn5, fmap1, datdir, omodel
c
      dimension wnl(21)
c
      data wnl    /'m2 ','s2 ','k1 ','o1 ','n2 ','p1 ','k2 ','q1 ',
     +             'm1 ','j1 ','oo1','2n2','mu2','nu2','l2 ','t2 ',
     +             'mtm','mf ','mm ','ssa','sa '                  /
c
      call chop(datdir, ic)
      if (datdir(ic:ic).ne.'/') then
         ic = ic + 1
         datdir(ic:ic) = '/'
      endif
c
      call chop(omodel,ic3)
      do ic2 = 1,ic3
         if (omodel(ic2:ic2).ne.' ') goto 19
      enddo
 19   continue
c
      do iw = 1,21
c
         wn3 = wnl(iw)
c
         if (wn3(3:3).eq.' ') then
            Lw2 = .true.
            wn2  = wn3(1:2)
         else
            Lw2 = .false.
         endif
c
         if (Lw2) then
            tmapw(iw) = datdir(1:ic)//'omap/'
     +                  //wn2//'.'//omodel(ic2:ic3)
            if ( (omodel(ic2:ic3).eq.'nao').and.(iw.le.16) ) then
               tmapj(iw) = datdir(1:ic)//'omap/'
     +                     //wn2//'_j.'//omodel(ic2:ic3)
            else
               tmapj(iw) = ' '
            endif
         else
            tmapw(iw) = datdir(1:ic)//'omap/'
     +                  //wn3//'.'//omodel(ic2:ic3)
            if ( (omodel(ic2:ic3).eq.'nao').and.(iw.le.16) ) then
               tmapj(iw) = datdir(1:ic)//'omap/'
     +                     //wn3//'_j.'//omodel(ic2:ic3)
            else
               tmapj(iw) = ' '
            endif
         endif
c
      enddo                     !iw
c
      grn1   = datdir(1:ic)//'grn1.data'
      grn2   = datdir(1:ic)//'grn2.data'
      grn3   = datdir(1:ic)//'grn3.data'
      grn4   = datdir(1:ic)//'grn4.data'
      grn5   = datdir(1:ic)//'grn5.data'
c
      fmap1  = datdir(1:ic)//'mesh/1stmesh.data'
c
      return
      end
c
