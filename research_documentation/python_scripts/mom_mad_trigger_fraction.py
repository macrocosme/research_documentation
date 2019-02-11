import numpy as np
import argparse
import cPickle as pickle

# Ripped from presto's filterbank.py
# (https://github.com/scottransom/presto/blob/master/lib/python/filterbank.py)
def read_header(filename, verbose=False):
    """Read the header of a filterbank file, and return
        a dictionary of header paramters and the header's
        size in bytes.
        Inputs:
            filename: Name of the filterbank file.
            verbose: If True, be verbose. (Default: be quiet)
        Outputs:
            header: A dictionary of header paramters.
            header_size: The size of the header in bytes.
    """
    header = {}
    filfile = open(filename, 'rb')
    filfile.seek(0)
    paramname = ""
    while (paramname != 'HEADER_END'):
        if verbose:
            print "File location: %d" % filfile.tell()
        paramname, val = sigproc.read_hdr_val(filfile, stdout=verbose)
        if verbose:
            print "Read param %s (value: %s)" % (paramname, val)
        if paramname not in ["HEADER_START", "HEADER_END"]:
            header[paramname] = val
    header_size = filfile.tell()
    filfile.close()
    return header, header_size

def compute_mad(array, med):
    series_mad = np.abs(array - med)
    return np.median(series_mad)

def compute_mom(L):
    if len(L) < 10:
        L.sort()
        return np.median(L)
    S = []
    l_index = 0
    for l_index in range(0, len(L) - 1, 5):
        S.append(L[l_index:l_index + 5])
    S.append(L[l_index:])
    Meds = []
    for sub_list in S:
        Meds.append(compute_mom(sub_list))
    L2 = compute_mom(Meds)
    L1 = L3 = []
    for i in L:
        if i < L2:
            L1.append(i)
        if i > L2:
            L3.append(i)
    if len(L) < len(L1):
        return compute_mom(L1)
    elif len(L) > len(L1) + 1:
        return compute_mom(L3)
    else:
        return L2

def main(**kwargs):
    from arts_analysis import reader
    import copy

    N = np.array([1, 5, 10, 50, 100, 250, 500, 1000, 2500])
    if kwargs['input_type'] is 'filterbank':
        data = reader.read_fil_data('/data2/output/20181020_2018-10-20-09:59:59.FRB171004_filterbank/CB17.fil', start=0, stop=250000)[0]
    if kwargs['input_type'] is 'time_chunks':
        chunk_size = 25000
        index_start = 0

        #chunk_size

    S1, S2, S3, S4 = [],[],[],[]

    SS1, SS2, SS3, SS4 = {},{},{},{}

    # Initialise dicts
    for ss in [SS1, SS2, SS3, SS4]:
        for nn in N:
            ss[nn] = -999999

    for ii in range(kwargs['N_SAMPLES']):
        print (ii)

        if kwargs['input_type'] is 'filterbank':
            xx = copy.deepcopy(data)
            xx.dedisperse(ii)
            xx = np.mean(xx.data, axis=0)
        elif kwargs['input_type'] is 'gaussian_noise':
            xx = np.random.normal(0, 1, 25000)
        elif kwargs['input_type'] is 'time_chunks':
            xx = reader.read_fil_data('/data2/output/20181020_2018-10-20-09:59:59.FRB171004_filterbank/CB17.fil', start=index_start, stop=index_start+args['chunk_size'])[0]
            index_start += args['chunk_size']

        for nn in N:
            print ("\t%d" % nn)

            k = len(xx)
            x = xx[:k//nn*nn].reshape(-1, nn).mean(-1)

            print ("\t\tCompute median/stdev")
            snr = (x.max() - np.median(x))/(np.std(x))
            if snr > SS1[nn]:
                SS1[nn] = snr

            print ("\t\tCompute mom/stdev")
            snr = (x.max() - compute_mom(x))/(np.std(x))
            if snr > SS2[nn]:
                SS2[nn] = snr

            print ("\t\tCompute mom/mad")
            med = compute_mom(x)
            snr = (x.max() - med)/(1.48*compute_mad(x, med))
            if snr > SS3[nn]:
                SS3[nn] = snr

            print ("\t\tCompute median/mad")
            med = np.median(x)
            snr = (x.max() - med)/(1.48*compute_mad(x, med))
            if snr > SS4[nn]:
                SS4[nn] = snr



            print ("")

    print ("printing order of append")
    for nn in N:
        print (nn)
        S1.append(SS1[nn])
        S2.append(SS2[nn])
        S3.append(SS3[nn])
        S4.append(SS4[nn])

    return S1, S2, S3, S4, N

def make_plot(S1, S2, S3, S4, N, **kwargs):
    from matplotlib import pyplot as plt
    plt.plot(25000./N, S1)
    plt.plot(25000./N, S2)
    plt.plot(25000./N, S3)
    plt.plot(25000./N, S4)

    plt.legend(['median, stdev','MoM, MAD','median, MAD', 'MoM, stdev'], fontsize=kwargs['fontsize'])
    plt.ylabel('S/N Max (1000 DMs)', fontsize=kwargs['fontsize'])
    plt.xlabel('N', fontsize=kwargs['fontsize'])

    plt.xscale = kwargs['xscale']
    plt.yscale = kwargs['yscale']

    plt.tight_layout()
    plt.show()
    plt.savefig(kwargs['figure_filename'])

def check_defaults(**kwargs):
    if kwargs['xscale'] == None:
        kwargs['xscale'] = 'log'

    if kwargs['yscale'] == None:
        kwargs['yscale'] = 'linear'

    if kwargs['fontsize'] == None:
        kwargs['fontsize'] = 12

    if kwargs['N_SAMPLES'] == None:
        kwargs['N_SAMPLES'] = 1000

    if kwargs['filerbank_header']:
        kwargs['filerbank_header'] = read_header

    if kwargs['figure_filename'] == None:
        kwargs['figure_filename'] = 'filterbank_%d.png' % kwargs['N_SAMPLES']

    if kwargs['input_type'] in ('filterbank', 'time_chunks'):
        kwargs['gaussian_noise'] = False

    return kwargs


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--pickle_filename', help="Pickle filename")
    parser.add_argument('--figure_filename', help="Figure filename", type=int)
    parser.add_argument('--input_type',
                        help="""Input type

                                Options:
                                    'filterbank': Filterbank file (.fil)
                                    'gaussian_noise': Stochastic gaussian draw
                                    'time_chunks': Discrete time chunks of size [index_start, index_start+chunk_size]
                             """,
                        type=str, choices=['filterbank', 'gaussian_noise', 'time_chunks'])
    parser.add_argument('--chunk_size', help="Chunk size (if input_type is 'time_chunks')", type=int)
    parser.add_argument('--fontsize', help="Figure's font size", type=str)
    parser.add_argument('--gaussian_noise', help="Use gaussian noise input (True/False)", type=bool)
    parser.add_argument('--N_SAMPLES', help="Number of trials (e.g. DMs, draws, chunks)", type=int)
    parser.add_argument('--xscale', help="Scaling for the x axis", type=str)
    parser.add_argument('--yscale', help="Scaling for the y axis", type=str)
    args = parser.parse_args()

    kwargs = check_defaults(**vars(args))

    S1, S2, S3, S4, N = main(**kwargs)

    if args.pickle_filename:
        with open(args.pickle_filename, 'wb') as f:
            pickle.dump([S1, S2, S3, S4, N], f)

    make_plot(S1, S2, S3, S4, N, **kwargs)
