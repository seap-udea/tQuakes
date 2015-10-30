c
C -- PROGRAM CLUSTER2000X 
C -- MODIFIED BY JORGE I. ZULUAGA, OCTOBER 29, 2015
C
C    RECOGNIZE CLUSTERS IN SPACE-TIME IN AN EARTHQUAKE CATALOG
C
C    VERSION CLUSTER2000 IS A MODIFICATION OF CLUSTER5, INCORPORATING
C    YEAR-2000 FORMAT COMPATIBILITY FOR INPUT FILES.
C
C    This code is a pre-release of a Y2K-version, developed for Rob Wesson.
C    It does not implement full Y2K compatibility. For example, the time calculations
C    are NOT Y2K-compatible because the century is ignored, so this code will NOT WORK
C    if the catalog bridges a century change. A real Y2K version is coming, which 
c    will accept catalogs that bridge century change.
C
C    Original version of this code is available at:
C       http://earthquake.usgs.gov/research/software/#CLUSTER
C
C    DESCRIPTION OF VARIABLES:
c
c          list     pointer from event to cluster number
c          nc       number of events in cluster
c          nclust   number of clusters
c          n        index for new cluster number
c          ctim0    time of first event in cluster
c          ctim1    time of largest event in custer
c          ctim2    time of second largest event in cluster
c          clat,clon,cdep   position of 'equivalent event' corresponding
c                   to cluster
c          cmag1    magnitude of largest event in cluster
c          cmag2    magnitude of second largest event in cluster
c          ibigst   event index pointing to biggest event in cluster
c          cdur     duration (first event to last) of cluster
c          cmoment  summed moment of events in cluster
c
c          tau      look-ahead time (minutes) for building cluster.
c          taumin   value for tau when event1 is not clustered
c          rtest    look-around (radial) distance (km) for building cluster
c          r1       circular crack radius for event1
c          rmain    circular crack radius for largest event in current cluster
c
c          xmeff    "effective" lower magnitude cutoff for catalog.
c                   xmeff is raised above its base value 
c                   by the factor xk*cmag1(list(i)) during clusters.
c
c          rfact    number of crack radii (see Kanamori and Anderson,
c                   1975) surrounding each earthquake within which to
c                   consider linking a new event into cluster.
c
c	   mpref    array of 4 integers specifying preferences for 
c		    selection of magnitude from hypoinverse record.
c			mpref(1) is the most prefered value, if it exists.
c			mpref(2) is the next-most prefered,  if it exists.
c			mpref(3) is the third-most prefered, if it exists.
c			mpref(4) is the least-prefered.
c
c	   	    where  1=fmag; 2=amag; 3=BKY-Mag (B); 4=Recalculated ML (L)
c
c		   for example, mpref=(3,1,2,4) means
c		        first use BKY (B) mag.
c			if it doesnt exist, next use fmag 
c			if it doesnt exist, next use amag 
c			if it doesnt exist, use Recalculated ML (L).
c
ccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc
c      input/output units:
c          unit 1       scratch file on scr:
c          unit 2       output - cluster summary
c          unit 3       input  - earthquake catalog to read
c          unit 7       output - original catalog, annotated to show 
c                                cluster membership
c          unit 8       output - declustered catalog: original catalog with
c                                clusters removed and replaced by their 
c                                equivalent events.
c          unit 9       output - cluster catalog: all events that belong to 
c                                a cluster (in chronological order, not  
c                                sorted by cluster)
c          
      dimension clat(9000),clon(9000),cdep(9000)
      dimension cmag1(9000),cmag2(9000),cdur(9000),cmoment(9000)
      dimension mpref(4), zmag(4)
      integer*2 ctim0(5,9000),ctim1(5,9000),ctim2(5,9000)
      integer*2 list(250000),nc(9000)
      integer*2 jcent, icent
      integer*2 itime(5),jtime(5),ltime(5),ytim1(5),ytim2(5)
      integer   fore, ibigst(9000), ibigx, inicent
      character*1 q1,q2,ichr,ins,iew,insx,iewx,fflag,aflag,cm1,cm2
      character*2 rmk2
      character*5 dum5
      character*3 eid1, eid2
      double precision dif
      character*40 catalog
      character*132 stamp
      logical cluster
      common/a/ rfact,tau
      
      data zero /0/
      data  nmag, mpref /4, 3,1,2,4/
      data list,cmag1/250000*0,9000*0./
      data tau0,taumin,taumax,p1,xk /2880., 2880., 14400., 0.99, .5/
      data xmeff,rfact,ierradj /1.5, 10.0, 1/
      data q1,q2,ins,iew,fflag,aflag /' ',' ',' ',' ',' ',' '/
      nmagrej = 0
      ntimrej = 0
      nquarej = 0
      ifile = 1

C-- OPEN A DIRECT ACCESS SCRATCH FILE FOR CATALOG
      open (1, status='scratch',
     1      access='direct', recl=109)

C-- JIZ: READ CONFIGURATION FILE
      open (666,file="cluster.conf",status="old")
      read (666,*) icent,inicent,IY1,IY2,xmagcut,rfact,ierradj

C-- SPECIFY THE SOURCE OF THE DATA
   20 catalog='catalogue.dat'

C-- READ DATA FROM THE NAMED CATALOG
        write (6,29) catalog
   29   format (' OPENING USER FILE ', a)
        open (3,file=catalog,status='old',err=20)
        irec = 1
        iorec = 1

C-- JIZ: THIS VERSION USES FREE FORMAT INPUT
   31   infmt=5

C-- FREE FORMAT - INPUT
C-- JIZ: COLUMNS: year, month, day, hour, minute, lat, lon, dep, Ml
  105 read (3, *, err= 900, END=35) jyr, itime(2), itime(3),
     1     itime(4), itime(5), xjlat, xjlon, dep1, xmag1
      itime(1)=jyr-inicent
      lat1=xjlat
      xlat1=(xjlat-lat1)*60.0
      lon1= -xjlon
      xlon1=(-xjlon-lon1)*60.0
      erh1=0.
      erz1=0.
      q1=' '
      iew=' '
      ins=' '
      goto 108

108   irec = irec + 1
      
C-- ACCEPT ONLY EVENTS PASSING INPUT CRITERIA...

C-- APPLY MAGNITUDE CUT:
        if (xmag1 .lt. xmagcut) then
          nmagrej = nmagrej + 1 
          goto 31
        end if
C-- REMOVE QUARRY SHOTS:
       if (rmk2(1:1) .eq. 'Q' .or. rmk2(1:1) .eq. 'q' .or.
     1     rmk2(2:2) .eq. 'Q' .or. rmk2(2:2) .EQ. 'q') then
         nquarej = nquarej + 1
         goto 31
       end if
C-- APPLY TIME LIMITS:
        if (itime(1) .lt. iy1 .or. itime(1) .gt. iy2) then
          ntimrej = ntimrej + 1
          goto 31
        end if

C-- AND WRITE AN UNFORMATTED RECORD TO A SCRATCH DIRECT-ACCESS FILE

        write(1,rec=iorec)icent,itime,lat1,ins,xlat1,lon1,iew,xlon1,
     1             dep1, xmag1,erh1,erz1,q1,dlat1, dlon1, ddep1, rms, 
     2             nst, amag1, aflag, fmag1, fflag, dum5,
     2             e1az,e1dip,e1, e2az,e2dip,e2, eid1

        iorec = iorec + 1
        goto 31

        stop 

   35   neq = iorec - 1
        inrec = irec - 1
        close (unit=3,status='keep')

      write (6,39) iy1, iy2, xmagcut, inrec, neq, ntimrej, 
     1             nmagrej, nquarej
   39 format ('   RANGE OF YEARS TO ACCEPT: ', I2, ' TO ', I2, /
     1        ' ...USING MINIMUM MAGNITUDE CUTOFF = ', F5.2 /
     1        i12, '   EVENTS READ', / 
     2        i12, '   EVENTS ACCEPTED' / 
     3        i12, '   EVENTS WERE OUTSIDE TIME WINDOW' /
     4        i12, '   EVENTS WERE REJECTED FOR MAGNITUDE' /
     5        i12, '   EVENTS WERE REJECTED AS QUARRY BLASTS')

      if (ierradj .eq. 1) write (6, 37) 
   37 format ('   LOCATION ERRORS IGNORED in distance calculations')
      if (ierradj .eq. 2) write (6, 38)
   38 format ('   LOCATION ERRORS SUBTRACTED in distance calculations')

C-- GET TO WORK
      i=0
      n=0
      nclust=0
      open (2,file='cluster.out',status='new')
      open (7,file='cluster.ano',status='new')
      open (8,file='cluster.dec',status='new')
      open (9,file='cluster.clu',status='new')

C-- PROCESS ONE EVENT AT A TIME

C-- GET THE ITH EVENT
  100 i=i+1
      read(1,rec=i,err=500)icent,itime,lat1,ins,xlat1,lon1,iew,xlon1,
     1             dep1, xmag1,erh1,erz1,q1,dlat1, dlon1, ddep1, rms, 
     2             nst, amag1, aflag, fmag1, fflag, dum5,
     2             e1az,e1dip,e1, e2az,e2dip,e2, eid1

      if (mod(i,1000) .ne. 0) goto 115
      call fdate (stamp)
      write (6,110) stamp(11:20), icent,itime, i, nclust
  110 format (2x, a, '  (',4i2,1x,2i2, ')', i10, 
     1       ' events read',i6,' clusters found')
      
  115 continue

C-- calculate tau (days), the look-ahead time for event 1.  When event1
C-- C belongs to a cluster, tau is a function of the magnitude of and
C-- the C time since the largest event in the cluster.  When event1 is
C-- not C (yet) clustered, tau = TAU0 set look-ahead time (in minutes)
C-- if C event1 is not yet clustered
      if (list(i) .ne. 0) goto 32
   30 tau = TAU0
      goto 40

C-- Calculate look-ahead time for events belonging to a cluster
   32 do 33 it=1,5
   33 jtime(it) = ctim1(it,list(i))
      call tdif(jtime,itime,dif)

      t=dif
      if (t .le. 0.) goto 30

      deltam = (1.-xk)*cmag1(list(i)) - xmeff
      denom = 10.**((deltam-1.)*2./3.)
      top = -alog(1.-p1)*t
      tau = top/denom

C-- Truncate tau to not exceed taumax, OR DROP BELOW TAUMIN
      if (tau .gt. taumax) tau = taumax
      IF (TAU .LT. TAUMIN) TAU = TAUMIN

   40 continue

C-- Keep getting jth events until dif > tau
      j=i
  200 j=j+1

C-- Skip the jth event if it is already identified as being part of c
C-- the cluster associated with the ith event
      if (list(j) .eq. list(i) .and. list(j) .ne. 0) goto 200

      read(1,rec=j,err=400)jcent,jtime,lat2,ins,xlat2,lon2,iew,xlon2,
     1             dep2, xmag2,erh2,erz2,q2,dlat2, dlon2, ddep2, rms, 
     2             nst, amag2, aflag, fmag2, fflag, dum5,
     2             e1az2,e1dip2,e12, e2az2,e2dip2,e22, eid2

C-- Test for temporal clustering
  208 call tdif (itime, jtime, dif)

      if (dif .gt. tau) goto 400

C--- test for spatial clustering
      call ctest(itime,lat1,xlat1,lon1,xlon1,dep1,xmag1,erh1,erz1,q1,
     1           jtime,lat2,xlat2,lon2,xlon2,dep2,xmag2,erh2,erz2,q2,
     2           cmag1(list(i)),cluster,ierradj)

      if (cluster .eqv. .false.) goto 200

C-- Cluster declared.  c if event i and event j are both already
C-- associated with c clusters, combine the clusters.
      if (list(i) .ne. 0 .and. list(j) .ne. 0) goto 375

C-- If event i is already associated with a cluster, add event j to it
      if (list(i) .ne. 0) goto 300

C-- If event j is already associated with a cluster, add event i to it
      if (list(j) .ne. 0) goto 280

C-- Initialize new cluster
      n=n+1
      nclust=nclust+1
      list(i)=n
      clat(n)=lat1+xlat1/60.
      clon(n)=lon1+xlon1/60.
      cdep(n)=dep1
      nc(n)=1
      ibigst(n) = i
      cmag1(n)=xmag1
      cmag2(n)=-2.
      cmoment(n)=10**(1.2*xmag1)
      do 250 it=1,5
      ctim1(it,n)=itime(it)
      ctim2(it,n)=0
  250 ctim0(it,n)=itime(it)
      goto 300

C-- prepare to add ith event to existing cluster
  280 l=i
      k=list(j)
      lat=lat1
      xlat=xlat1
      lon=lon1
      xlon=xlon1
      xmag=xmag1
      ibigx = i
      dep=dep1
      do 285 it=1,5
  285 ltime(it)=itime(it)
      goto 320

C-- prepare to add jth event to existing cluster
  300 l=j
      k=list(i)
      lat=lat2
      xlat=xlat2
      lon=lon2
      xlon=xlon2
      dep=dep2
      xmag=xmag2
      ibigx = j
      do 305 it=1,5
  305 ltime(it)=jtime(it)

C-- Add new event to cluster
  320 nc(k)=nc(k)+1
      w1=(nc(k)-1.)/nc(k)
      w2=  1.0/nc(k)
      list(l)=k

C-- Update cluster focal parameters
      clat(k)=clat(k)*w1 + (lat+xlat/60.)*w2
      clon(k)=clon(k)*w1 + (lon+xlon/60.)*w2
      cdep(k)=cdep(k)*w1 + dep*w2

C-- Update other cluster parameters
      cmoment(k)=cmoment(k) + 10**(1.2*xmag)
      if (xmag .gt. cmag1(k)) goto 350
      if (xmag .le. cmag2(k)) goto 200

C-- Current event is second largest event in cluster k
      cmag2(k)=xmag
      do 330 it=1,5
  330 ctim2(it,k)=ltime(it)
      goto 200

C-- Current event is largest in cluster k
  350 cmag2(k)=cmag1(k)
      cmag1(k)=xmag
      ibigst(k) = ibigx
      do 355 it=1,5
      ctim2(it,k)=ctim1(it,k)
  355 ctim1(it,k)=ltime(it)
      goto 200

C-- Combine existing clusters by merging into earlier cluster c and
C-- keeping earlier cluster's identity
  375 k=list(i)
      l=list(j)

      if (k. lt. l) goto 376
      k=list(j)
      l=list(i)
C-- Merge cluster l into cluster k
  376 w1=float(nc(k))/float((nc(k)+nc(l)))
      w2=float(nc(l))/float((nc(k)+nc(l)))
      clat(k)=clat(k)*w1 + clat(l)*w2
      clon(k)=clon(k)*w1 + clon(l)*w2
      cdep(k)=cdep(k)*w1 + cdep(l)*w2
      cmoment(k)=cmoment(k) + cmoment(l)
      do 380 ii=1,neq
  380 if (list(ii) .eq. l) list(ii)=k
      nc(k)=nc(k)+nc(l)
      nc(l)=0
      nclust=nclust-1

C-- Identify largest and second largest magnitude events in c merged
C-- cluster
      if (cmag1(k) .ge. cmag1(l)) then
            ymag1=cmag1(k)
            ibigx = ibigst(k)
            do 382 it=1,5
  382       ytim1(it)=ctim1(it,k)
            if (cmag1(l) .gt. cmag2(k)) then
                  ymag2=cmag1(l)
                  do 383 it=1,5
  383             ytim2(it)=ctim1(it,l)
            else
                  ymag2=cmag2(k)
                  do 384 it=1,5
  384             ytim2(it)=ctim2(it,k)
            end if
      else
            ymag1=cmag1(l)
            ibigx = ibigst(l)
            do 392 it=1,5
  392       ytim1(it)=ctim1(it,l)
            if (cmag1(k) .ge. cmag2(l)) then
                  ymag2=cmag1(k)
                  do 393 it=1,5
  393             ytim2(it)=ctim1(it,k)
            else
                  ymag2=cmag2(l)
                  do 394 it=1,5
  394             ytim2(it)=ctim2(it,l)
            end if
      end if

      cmag1(k)=ymag1
      cmag2(k)=ymag2
      ibigst(k) = ibigx
      do 395 it=1,5
      ctim1(it,k)=ytim1(it)
  395 ctim2(it,k)=ytim2(it)

C-- Update duration of merged event
      do 396 it=1,5
  396 jtime(it)=ctim0(it,k)
      call tdif(jtime,itime,dif)
      cdur(k)=dif/1440.

      goto 200

C-- Finish processing ith event
  400 if (list(i) .eq. 0) goto 100

C-- Update duration of cluster k for event i
      do 360 it=1,5
  360 jtime(it)=ctim0(it,list(i))
      call tdif(jtime,itime,dif)
      cdur(list(i))=dif/1440.
      goto 100

C-- entire catalog has been searched c output results
  500 neqcl = 0
      do 502 i=1,neq-1
  502 if (list(i) .ne. 0) neqcl=neqcl+1

      call fdate (stamp)

      do 680 i=1,neq

C-- MAIN OUTPUT LOOP
      read (1, rec=i) icent,itime,lat1,ins,xlat1,lon1,iew,xlon1,
     1                dep1,xmag1,erh1,erz1,q1,dlat1, dlon1,
     2   ddep1, rms, nst, amag1, aflag, fmag1, fflag, dum5,
     3   e1az,e1dip,e1, e2az,e2dip,e2, eid1

      icr = 43
      if (list(i).ne.0) icr = mod(list(i)-1,26)+65
      ichr = char(icr)

C-- OUTPUT FORMATS
C-- FREE
613   format (3i2.2,1x,2i2.2,2x,i3,a1,f10.2,1x,i3,a1,f10.2,
     1        2x,f10.2,3x,f4.2,18x,f4.1,1x,f4.1,1x,a1, 
     1        t82,i10,1x,a1)

CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
C-- DECLUSTERED CATALOG - ONLY UNCLUSTERED EVENTS
      if (list(i) .ne. 0) goto 630

600   goto 605

C-- FREE FORMAT
605    write (8, *) (itime(k), k=1,3), 
     1              lat1+xlat1/60, lon1+xlon1/60,dep1,xmag1
       goto 650

CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
C-- WRITE TO CLUSTERED EVENTS LIST 
630   goto 633

C-- FREE FORMAT
633   WRITE (9, 613) itime,lat1,ins,xlat1,
     1 lon1,iew,xlon1,dep1,xmag1,erh1,erz1,q1, list(i)
      goto 650

CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
C-- ANNOTATED CATALOG - ALL EVENTS
650   goto 653

C-- FREE FORMAT
653   WRITE (7, 613) itime,lat1,ins,xlat1,
     1 lon1,iew,xlon1,dep1,xmag1,erh1,erz1,q1, LIST(I),ICHR
      goto 680

680   continue
CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC

C-- write the output file summarizing the run and the listing the
C-- clusters
      write (2,503) catalog, inrec, neq, ntimrej, nquarej, 
     1     nmagrej, xmagcut, neq, nclust, neqcl, stamp,
     1     rfact, tau0, taumin, taumax, p1, xk, ierradj
  503 format (//8x,'Program: CLUSTER2000X (test version)', //
     1    '        SUMMARY OF CLUSTERS IN  ',A,//
     1    i8, ' EVENTS READ', i8, ' EVENTS ACCEPTED', 
     2    i8, ' EVENTS WERE OUTSIDE TIME RANGE SPECIFIED',/
     3    i8, ' EVENTS WERE REJECTED AS QUARRY BLASTS'/
     2    i8, ' EVENTS REJECTED FOR MAGNITUDE  (MINIMUM MAGNITUDE = ',
     2    f5.2, ')' //
     3    i10,' earthquakes tested;  ',i6,' clusters identified',5x,
     4    i6,' clustered events',5x,a, /
     5    '   rfact=',f6.3,'   tau0=',f8.3,'   taumin=',f10.2,
     6    '   taumax=',f10.2,'   p1=',f6.3,'   xk=',f5.2,
     6    '   ierradj=',i2,///
     7    '    N  -1ST EVENT-   DUR(DAYS)   NC  ------------EQUIVALENT',
     8    ' EVENT-----------  --LARGEST EVENT--   2ND LARGEST EVENT',
     9    '         PCT(F)         DT    DM  '/,'***###***')

C-- Loop through clusters, k=1,n
      do 700 k=1,n
      if (nc(k) .eq. 0) goto 700
      lat=clat(k)
      xlat=(clat(k)-lat)*60.
      lon=clon(k)
      xlon=(clon(k)-lon)*60.
      xmag=(alog10(cmoment(k)))/1.2

C-- Calculate percentage of cluster duration taken by foreshocks
      do 504 it=1,5
      itime(it)=ctim0(it,k)
  504 jtime(it)=ctim1(it,k)
      call tdif(itime,jtime,dif)
      if (cdur(k) .lt. 0.001) cdur(k)=.001
      fore =  (dif/14.40) / cdur(k) + .5

C-- Calculate time (days) from largest event to 2nd-largest event.
C-- (positive = aftershock-like, negative = foreshock-like).
      do 505 it=1,5
      itime(it)=ctim1(it,k)
  505 jtime(it)=ctim2(it,k)
      call tdif(itime,jtime,dif)
      t12dif=dif/1440.
      xmdif=cmag1(k)-cmag2(k)

C-- Calculate DT, the absolute time difference between largest and
C-- 2nd-largest events, and DM, the magnitude of the second of these
C-- events minus the magnitude of the first.
      if (t12dif .lt. 0.0) then
         dm =   xmdif
         dt = - t12dif
      else
         dm = - xmdif
         dt =   t12dif
      end if

C-- Write out cluster summary to "output" file
      ichr = char(mod(k-1,26)+65)
  510 write (2,511) ichr,k,(ctim0(it,k),it=1,5),cdur(k),nc(k),lat,xlat,
     1       lon,xlon,cdep(k),xmag,(ctim1(it,k),it=1,5),cmag1(k),
     2       (ctim2(it,k),it=1,5),cmag2(k),fore,DT,DM
  511 format (1x,a1,i4,1x,3i2.2,1x,2i2.2,2x,f8.3,2x,i5,
     1        2(i4,f8.2),2f8.2,2(3x,5i2.2,1x,f6.2),i15,1x,f10.3,f6.2)

C-- Write out (append) the "equivalent events" to declustered catalog
C-- Use error parameters from largest event in cluster
        read(1,rec=ibigst(k),err=903) icent,itime,lat1,insx,xlat1,
     2        lon1,iewx,xlon1,
     3        dep1, xmag1,erh1,erz1,q1,dlat1, dlon1, ddep1, rms, 
     4        nst, amag1, aflag, fmag1, fflag, dum5,
     5        e1az,e1dip,e1, e2az,e2dip,e2, eid1

      goto 695

C-- FREE FORMAT
695    write (8, *)  (ctim1(it,k),it=1,3), lat+xlat/60.,
     1                 lon+xlon/60., xmag
      goto 700

  700 continue
      close (unit=1,status='delete')
      close (unit=2,status='keep')
      close (unit=3,status='keep')
      close (unit=4,status='keep')
      stop
  900 WRITE (2, 902) IREC
  902 FORMAT (' ***** READ ERROR ON INPUT FILE, LINE ', I8)
      stop
  903 WRITE (2, 904) ibigst(k)
  904 FORMAT (' ***** READ ERROR ON DIRECT ACCESS FILE, LINE ', I8)
      stop
      end

C**********************************************************************
C ROUTINES
C**********************************************************************

C============================================================
C ctest: Determine whether event1 and event2 are 'clustered'
C============================================================

      subroutine ctest (itime,lat1,xlat1,lon1,xlon1,dep1,xmag1,erh1,
     1                  erz1,q1,jtime,lat2,xlat2,lon2,xlon2,dep2,xmag2,
     2                  erh2,erz2,q2,cmag1,cluster,ierradj)

c      Determine whether event1 and event2 are 'clustered'
c      according to the radial distance criterion:

c            reduced hypocentral distance .le. rtest 
c
c	Hypocentral distance r may be reduced by the hypocentral
c	uncertainty, or ignored, depending on an option set in the
c	beginning of the main program.
c	To reduce distance by location error, set ierradj = 2.
c	Or, to ignore the hypocentral errors, set ierradj = 1. 

      logical cluster
      character*1 q1,q2,qual(4)
      integer*2 itime(5),jtime(5)
      dimension erhqual(4), erhearly(4),erzqual(4), erzearly(4) 
      common/a/ rfact,tau

      data erhqual/.5,1.,2.5,5./              
      data erhearly/1.,3.,7.,10./            
      data erzqual/1.,2.,5.,10./            
      data erzearly/5.,10.,10.,10./        
      data qual/'A','B','C','D'/          

      cluster=.false.

C  The interaction distance about an event is defined as
   
C         r  =  rfact * a(M, dsigma)

C  where a(M, dsigma) is the radius of a circular crack (Kanamori and
C  Anderson, 1975) corresponding to an earthquake of magnitude M and
C  stress drop dsigma.  The value dsigma = 30 bars is adopted implicitly
C  in the calculation.

C     log a  =  0.4*M - (log(dsigma))/3 - 1.45

C  The term (log(dsigma)/3 - 1.45) evaluates to the factor 0.011 in
C  calculation below, when dsigma=30 bars. a is in kilometers.

c---- determine hypocentral distance between events
      alat=lat1+xlat1/60.
      alon=lon1+xlon1/60.
      blat=lat2+xlat2/60.
      blon=lon2+xlon2/60.
      call delaz(alat,alon,blat,blon,r,azr)
      z=abs(dep1-dep2)
      r=sqrt(z**2 + r**2)
      if (z .lt. 0.01 .and. r .lt. 0.01) goto 30

c---- assign hypocentral errors if a quality code was given
	if (q1. ne. ' ') then
	DO 4 I=1,4
4	IF (Q1 .EQ. QUAL(I)) GOTO 5
	I=4
5	IF (Itime(1) .LT. 70) THEN
		ERH1 = ERHEARLY(I)
		ERZ1 = ERZEARLY(I)
	ELSE
		ERH1 = ERHQUAL(I)
		ERZ1 = ERZQUAL(I)
	ENDIF
	DO 14 I=1,4
14	IF (Q2 .EQ. QUAL(I)) GOTO 15
	I=4
15	IF (Itime(1) .LT. 70) THEN
		ERH2 = ERHEARLY(I)
		ERZ2 = ERZEARLY(I)
	ELSE
		ERH2 = ERHQUAL(I)
		ERZ2 = ERZQUAL(I)
	ENDIF
	endif
	
c---- reduce hypocentral distance by location uncertainty of both events
c     Note that r can be negative when location uncertainties exceed
c     hypocentral distance
      if (ierradj .eq. 2) then
	alpha = atan2(z,r)
	ca = cos(alpha)
	sa = sin(alpha)
	e1 = sqrt(erh1*erh1 * ca*ca + erz1*erz1 * sa*sa)
	e2 = sqrt(erh2*erh2 * ca*ca + erz2*erz2 * sa*sa)
	r = r - e1 - e2
      endif

c     calculate interaction radius the first event of the pair
c     and for the largest event in the cluster associated with
c     the first event
   30 r1 = rfact * 0.011 * 10.**(0.4*xmag1)
      rmain =      0.011 * 10.**(0.4*cmag1)
      rtest = r1 + rmain
c     limit interaction distance to one crustal thickness
      if (rtest .gt. 30.) rtest=30.

c---- test distance criterion
      if (r .le. rtest) cluster=.true.
      return
      end

C============================================================
C tdif: Calculates the time difference (jtime - itime)
C============================================================

       subroutine tdif (itime,jtime,dif)
c      Calculates the time difference (jtime - itime)
c      where the elements of itime of jtime represent year,
c      month, day, hour and minute.  Leap years are accounted for.
c      The time difference, in minutes, is returned in the
c      double precision variable dif.

c      dif = (jtime - itime)

      integer*2 days(12),itime(5),jtime(5)
      double precision t1,t2,t1a,t2a,t1b,t2b,dif
      data days/0,31,59,90,120,151,181,212,243,273,304,334/

c---- t1a is number of minutes from 00:00 1/1/itime(1) to itime
      t1a = ( (days(itime(2)) + itime(3)-1)*24. + itime(4))*60. 
     1      + itime(5)
      if (mod(itime(1),4).eq.0 .and. itime(2).gt.2) t1a = t1a + 1440.

c---- t1b is number of days from 00:00 1/1/69 to 00:00 1/1/itime(1)
      t1b = (itime(1)-69)*365 + int((itime(1)-69.)/4.)

      t1 = t1a + t1b *1440.

c---- t2a is number of minutes from 00:00 1/1/jtime(1) to jtime
      t2a = ( (days(jtime(2)) + jtime(3)-1)*24. + jtime(4))*60. 
     1        + jtime(5)
      if (mod(jtime(1),4).eq.0 .and. jtime(2).gt.2) t2a = t2a + 1440.

c---- t2b is number of days from 00:00 1/1/69 to 00:00 1/1/jtime(1)
      t2b = (jtime(1)-69)*365 + int((jtime(1)-69.)/4.)

      t2 = t2a + t2b *1440.

      dif = t2 - t1
      return
      end

C============================================================
C delaz: computes cartesian distance from a to b
C============================================================
      subroutine delaz(alat,alon,blat,blon,dist,azr)
c        computes cartesian distance from a to b
c        a and b are in decimal degrees and n-e coordinates
c        del -- delta in degrees
c        dist -- distance in km
c        az -- azimuth from a to b clockwise from north in degrees
c
      real*8 pi2,rad,flat,alatr,alonr,blatr,blonr,geoa,geob,
     1       tana,tanb,acol,bcol,diflon,cosdel,delr,top,den,
     2       colat,radius
c
      data pi2/1.570796e0/
      data rad/1.745329e-02/
      data flat/.993231e0/
      if (alat.eq.blat.and.alon.eq.blon) goto 10
c-----convert to radians
      alatr=alat*rad
      alonr=alon*rad
      blatr=blat*rad
      blonr=blon*rad
      tana=flat*dtan(alatr)
      geoa=datan(tana)
      acol=pi2-geoa
      tanb=flat*dtan(blatr)
      geob=datan(tanb)
      bcol=pi2-geob
c-----calcuate delta
      diflon=blonr-alonr
      cosdel=dsin(acol)*dsin(bcol)*dcos(diflon)+dcos(acol)*dcos(bcol)
      delr=dacos(cosdel)
c-----calcuate azimuth from a to b
      top=dsin(diflon)
      den=dsin(acol)/dtan(bcol)-dcos(acol)*dcos(diflon)
      azr=datan2(top,den)
c-----compute distance in kilometers
      colat=pi2-(alatr+blatr)/2.
      radius=6371.227*(1.0+3.37853d-3*(1./3.-((dcos(colat))**2)))
      dist=delr*radius
      return
   10 dist=0.0
      azr=0.0
      return
      end
