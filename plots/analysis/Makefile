FC	= gfortran
FFLAGS	=  -g 

cluster2000x.out:   cluster2000x.o
	$(FC) $(FFLAGS) -o $@ $^

clean:
	-rm cluster.* 2> /dev/null
	-rm *~ *.pyc *.o *.out 2> /dev/null


