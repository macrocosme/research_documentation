#!/usr/bin/env/ python

import time

import random
import numpy as np
import glob
import scipy
import optparse
import random

try:
    import matplotlib.pyplot as plt
except:
    plt = None
    pass

import simulate_frb
import reader
import tools
#import rfi_test

# width / downsample bug

def test_writer():
    fn_fil = '/data/03/Triggers/B0329+54/1_dish_B0329+54.fil'
    fn_out = '/data/03/Triggers/B0329+54/1_dish_B0329+54_output.fil'
    NFREQ = 1536
    chunksize = 5e4

    for ii in range(146):
        data_filobj, freq, delta_t, header = reader.read_fil_data(fn_fil,
                                 start=ii*chunksize, stop=chunksize)
        data = data_filobj.data

        if ii==0:
            fn_rfi_clean = reader.write_to_fil(np.zeros([NFREQ, 0]),
                                               header, fn_out)

        fil_obj = reader.filterbank.FilterbankFile(fn_out, mode='readwrite')
        fil_obj.append_spectra(data.transpose())

        print('wrote %d' % ii)


def inject_in_filterbank(fn_fil, fn_out_dir, N_FRB=1, 
                         NFREQ=1536, NTIME=2**15, rfi_clean=False,
                         dm=250.0, freq=(1550, 1250), dt=0.00004096,
                         chunksize=5e4, calc_snr=True, start=0, 
                         freq_ref=1400., subtract_zero=False, clipping=None):
    """ Inject an FRB in each chunk of data 
        at random times. Default params are for Apertif data.

    Parameters:
    -----------

    fn_fil : str
        name of filterbank file 
    fn_out_dir : str 
        directory for output files 
    N_FRB : int 
        number of FRBs to inject 
    NTIME : int 
        number of time samples per data chunk 
    rfi_clean : bool 
        apply rfi filters 
    dm : float / tuple 
        dispersion measure(s) to inject FRB with 
    freq : tuple 
        (freq_bottom, freq_top) 
    dt : float 
        time resolution 
    chunksize : int 
        size of data in samples to read in 
    calc_snr : bool 
        calculates S/N of injected pulse 
    start : int 
        start sample 
    freq_ref : float 
        reference frequency for injection code 
    subtract_zero : bool 
        subtract zero DM timestream from data 
    clipping : 
        zero out bright events in zero-DM timestream 

    Returns:
    --------
    None 
    """

    if type(dm) is not tuple:
        max_dm = dm
    else:
        max_dm = max(dm)

    t_delay_max = abs(4.14e3*max_dm*(freq[0]**-2 - freq[1]**-2))
    t_delay_max_pix = int(t_delay_max / dt)

    # ensure that dispersion sweep is not too large 
    # for chunksize
    f_edge = 0.3    

    while chunksize <= t_delay_max_pix/f_edge:
        chunksize *= 2
        NTIME *= 2
        print('Increasing to NTIME:%d, chunksize:%d' % (NTIME, chunksize))

    ii=0
    params_full_arr = []

    ttot = int(N_FRB*chunksize*dt)

    timestr = time.strftime("%Y%m%d-%H%M")
    fn_fil_out = '%s/dm%s_nfrb%d_%s_sec_%s.fil' % (fn_out_dir, dm, N_FRB, ttot, timestr)
    fn_params_out = fn_fil_out.strip('.fil') + '.txt'

    f_params_out = open(fn_params_out, 'w+')
    f_params_out.write('# DM      Sigma      Time (s)     Sample    Downfact\n')
    f_params_out.close()

    for ii in xrange(N_FRB):
        # drop FRB in random location in data chunk
        offset = random.randint(0.1*chunksize, (1-f_edge)*chunksize)
        data_filobj, freq_arr, delta_t, header = reader.read_fil_data(fn_fil, 
                                            start=start+chunksize*ii, stop=chunksize)

        if ii==0:
            fn_rfi_clean = reader.write_to_fil(np.zeros([NFREQ, 0]), 
                                            header, fn_fil_out)

        data = data_filobj.data
        # injected pulse time in seconds since start of file

        t0_ind = offset+NTIME//2+chunksize*ii
        t0_ind = start + chunksize*ii + offset   # hack because needs to agree with presto  
        t0 = t0_ind*delta_t 

        if len(data)==0:
            break             

        data_event = (data[:, offset:offset+NTIME]).astype(np.float)

        data_event, params = simulate_frb.gen_simulated_frb(NFREQ=NFREQ, 
                                               NTIME=NTIME, sim=True, 
#                                               fluence=3000*(1+0.1*ii),
                                               fluence=(150+10*ii, 500+10*ii),
                                               spec_ind=0, width=(delta_t, delta_t*100),#delta_t*512,#(delta_t, delta_t*100), 
                                               dm=dm+ii*10, scat_factor=(-4, -3.5), 
                                               background_noise=data_event, 
                                               delta_t=delta_t, plot_burst=False, 
                                               freq=(freq_arr[0], freq_arr[-1]), 
                                               FREQ_REF=freq_ref, scintillate=False)

        dm_ = params[0]
        params.append(offset)

        print("%d/%d Injecting with DM:%d width: %.2f offset: %d" % 
                                (ii, N_FRB, dm_, params[2], offset))
        
        data[:, offset:offset+NTIME] = data_event

        #params_full_arr.append(params)
        width = params[2]
        downsamp = max(1, int(width/delta_t))
        t_delay_mid = 4.15e3*dm_*(freq_ref**-2-freq_arr[0]**-2)
        # this is an empirical hack. I do not know why 
        # the PRESTO arrival times are different from t0 
        # by the dispersion delay between the reference and 
        # upper frequency
        t0 -= t_delay_mid #hack

        if rfi_clean is True:
            data = rfi_test.apply_rfi_filters(data.astype(np.float32), delta_t)

        if subtract_zero is True:
            print("Subtracting zero DM")
            data_ts_zerodm = data.mean(0)
            data -= data_ts_zerodm[None]

        if clipping is not None:
            # Find tsamples > 8sigma and replace them with median
            assert type(clipping) in (float, int), 'clipping must be int or float'

            data_ts_zerodm = data.mean(0)
            stds, med = sigma_from_mad(data_ts_zerodm)
            ind = np.where(np.absolute(data_ts_zerodm - med) > 8.0*stds)[0]
            data[:, ind] = np.median(data, axis=-1, keepdims=True)

        if ii<0:
            fn_rfi_clean = reader.write_to_fil(data.transpose(), header, fn_fil_out)
        elif ii>=0:
            fil_obj = reader.filterbank.FilterbankFile(fn_fil_out, mode='readwrite')
            fil_obj.append_spectra(data.transpose())

        if calc_snr is True:
            data_filobj.data = data
            data_filobj.dedisperse(dm_)
            print('t0, t0_ind, offset, np.argmax(data_filobj.data.mean(0))')
            print(t0, t0_ind, offset, np.argmax(data_filobj.data.mean(0)))
            end_t = abs(4.15e3*dm_*(freq[0]**-2 - freq[1]**-2))
            end_pix = int(end_t / dt)
            end_pix_ds = int(end_t / dt / downsamp)

            data_rb = (data_filobj.data).copy()
            data_rb = data_rb[:, :-end_pix].mean(0)
            data_rb -= np.median(data_rb)

            SNRTools = tools.SNR_Tools()
            print("calculating S/N")
            snr_max, width_max = SNRTools.calc_snr_widths(data_rb,
                                                          widths=2**np.arange(12))

#            snr_max2, width_max2 = tools.calc_snr_widths(data_rb,
#                                         )
            print("S/N: %.2f width_used: %.3f width_tru: %.3f DM: %.1f" % (snr_max, width_max, width/delta_t, dm_))
            t0_ind = np.argmax(data_filobj.data.mean(0)) + chunksize*ii
            t0 = t0_ind*delta_t #huge hack
        else:
            snr_max = 10.0
            width_max = int(width/dt)

        f_params_out = open(fn_params_out, 'a+')
        f_params_out.write('%2f   %2f   %5f   %7d   %d\n' % 
                           (params[0], snr_max, t0, t0_ind, width_max))

        f_params_out.close()
        del data, data_event

    params_full_arr = np.array(params_full_arr)

if __name__=='__main__':

    def foo_callback(option, opt, value, parser):
        setattr(parser.values, option.dest, value.split(','))

    parser = optparse.OptionParser(prog="inject_frb.py", \
                        version="", \
                        usage="%prog FN_FILTERBANK FN_FILTERBANK_OUT [OPTIONS]", \
                        description="Create diagnostic plots for individual triggers")

    parser.add_option('--sig_thresh', dest='sig_thresh', type='float', \
                        help="Only process events above >sig_thresh S/N" \
                                "(Default: 8.0)", default=8.0)

    parser.add_option('--nfrb', dest='nfrb', type='int', \
                        help="Number of FRBs to inject(Default: 50).", \
                        default=10)

    parser.add_option('--rfi_clean', dest='rfi_clean', default=False,\
                        help="apply rfi filters")

    parser.add_option('--dm_low', dest='dm_low', default=None,\
                        help="min dm to use, either float or tuple", 
                      type='float')

    parser.add_option('--dm_high', dest='dm_high', default=None,\
                        help="max dms to use, either float or tuple", 
                      type='float')

    parser.add_option('--calc_snr', action='store_true',
                        help="calculate S/N of injected pulse", 
                      )
    
    parser.add_option('--dm_list', type='string', action='callback', callback=foo_callback)


    options, args = parser.parse_args()
    fn_fil = args[0]
    fn_fil_out = args[1]

    if options.dm_low is None:
        if options.dm_high is None:
            dm = 500.
        else:
            dm = options.dm_high
    elif options.dm_high is None:
        dm = options.dm_low
    else:
        dm = (options.dm_low, options.dm_high)

    if len(options.dm_list)==1:
        inject_in_filterbank(fn_fil, fn_fil_out, N_FRB=options.nfrb,
                                                        NTIME=2**15, rfi_clean=options.rfi_clean,
                                                        calc_snr=options.calc_snr, start=0,
                                                        dm=float(options.dm_list[0]))
        exit()

    import multiprocessing
    from joblib import Parallel, delayed

    ncpu = multiprocessing.cpu_count() - 1 
    Parallel(n_jobs=ncpu)(delayed(inject_in_filterbank)(fn_fil, fn_fil_out, N_FRB=options.nfrb,
                                                        NTIME=2**15, rfi_clean=options.rfi_clean,
                                                        calc_snr=options.calc_snr, start=0,
                                                        dm=float(x)) for x in options.dm_list)

#    params = inject_in_filterbank(fn_fil, fn_fil_out, N_FRBs=options.nfrb, 
#                                  NTIME=2**15, rfi_clean=options.rfi_clean, 
#                                  dm=dm, calc_snr=options.calc_snr, start=0)
    

#    params = inject_in_filterbank(fn_fil, fn_fil_out, N_FRBs=options.nfrb, 
#                                  NTIME=2**15, rfi_clean=options.rfi_clean, 
#                                  dm=dm, calc_snr=options.calc_snr, start=0)
 
