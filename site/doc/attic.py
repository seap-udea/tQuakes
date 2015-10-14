        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # DEBUGGING DATA
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # RECONSTRUCTING ALL SIGNAL
        # stall=numpy.array([all_signal_teo(tval,ft,T,N,1,Nh+1) for tval in t])
        # numpy.savetxt("%s/data-all.dat"%quakedir,numpy.column_stack((t,stall)))

        # MEAN AND AMPLITUDE
        smean=s.mean()
        smax=numpy.abs(s-smean).max()

        # THEORETICAL DATA
        omega=2*PI/period
        k=omega2k(omega,T,N)
        st=numpy.array([signal_teo(tval,ft,T,N,k) for tval in t])

        # ADJUSTING THEORETICAL DATA
        stmean=st.mean()
        stmax=numpy.abs(st-stmean).max()
        st=(st-stmean)*smax/stmax+smean

        # STORING RESULT
        numpy.savetxt("%s/data.dat"%quakedir,numpy.column_stack((t,s)))
        numpy.savetxt("%s/data-theo.dat"%quakedir,numpy.column_stack((t,st)))
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        break
