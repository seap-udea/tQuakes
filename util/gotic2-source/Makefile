# Makefile for GOTIC2
#    by Koji Matsumoto 
#    2004.10.25

# -----< Fortran Compiler Configuration >-----

# General
FC      = gfortran
FFLAGS  = 

# Intel fortran compiler on Linux
#FC      = ifort
#FFLAGS  = -O3 -tpp7 -lsvml 

# Gnu comliler on Linux or cygwin
#FC      = g77
#FFLAGS  =

# IBM AIX4.3
#FC      = xlf
#FFLAGS  = -O3 -qstrict

# HP-UX
#FC      = f90
#FFLAGS  = +O3

# -----< /Fortran Compiler Configuration >-----

PACKAGE = gotic2-source

PROG    = gotic2

SRCS	= agravi.f  angld.f   astro.f   atilti.f  azmth.f   \
	  banner.f  chop.f    cintgl.f  convl1.f  convl2.f  \
	  convl3.f  convl4.f  csearc.f  dgravi.f  dtilti.f  \
	  dverti.f  earth.f   factl.f   fconf.f   gellip.f  \
	  getapj.f  getapw.f  glsph.f   gmodel.f  greenf.f  \
	  greenp.f  lpout.f   lpout2.f  main.f    minmax.f  \
	  mjdymd.f  omeshf.f  predic.f  quadr.f   rd1st.f   \
	  rd2nd.f   rd3rd.f   rd4th.f   rdcmp.f   rdhead.f  \
	  rdispi.f  rdprein.f readin.f  refphs.f  reslt2.f  \
	  result.f  setap.f   spharm.f  stide.f   strani.f  \
	  tdispi.f  tjulid.f  vset.f

OBJS    = $(SRCS:.f=.o)

FILES   = Makefile $(SRCS)

VER     = `date +%Y%m%d`

BINDIR  = ..

# etc
SHELL   = /bin/sh
RM      = rm -f
PROF    = gprof

### rules ###

.SUFFIXES:
.SUFFIXES: .o .f

all: $(PROG) install

$(PROG): $(OBJS)
	$(FC) -o $@ $(OBJS)

.f.o:
	$(FC) $(FFLAGS) -c $< 


### useful commands ###

.PHONY: clean
clean:
	$(RM) $(OBJS)
	$(RM) gotic2 core gmon.out *~ #*# 

tar:
	@echo $(PACKAGE)-$(VER) > .package
	@$(RM) -r `cat .package`
	@mkdir `cat .package`
	@ln $(FILES) `cat .package`
	tar cvf - `cat .package` | gzip -9 > `cat .package`.tar.gz
	@$(RM) -r `cat .package` .package

zip:
	zip -9 $(PACKAGE)-$(VER).zip $(FILES)

install:
	cp $(PROG) $(BINDIR)
#
