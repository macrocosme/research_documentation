import numpy as np
import argparse
import cPickle as pickle

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
    if kwargs['input_type'] == 'filterbank':
        data = reader.read_fil_data(kwargs['filterbank_filename'], start=0, stop=250000)[0]
    if kwargs['input_type'] == 'time_chunks':
        chunk_size = 25000
        index_start = 0

        #chunk_size

    S1, S2, S3, S4 = [],[],[],[]

    SS1, SS2, SS3, SS4 = {},{},{},{}

    # Initialise dicts
    for ss in [SS1, SS2, SS3, SS4]:
        for nn in N:
            ss[nn] = -999999

    for ii in range(kwargs['n_samples']):
        print (ii)

        print kwargs['input_type']

        if kwargs['input_type'] == 'filterbank':
            xx = copy.deepcopy(data)
            xx.dedisperse(ii)
            xx = np.mean(xx.data, axis=0)
        elif kwargs['input_type'] == 'gaussian_noise':
            xx = np.random.normal(0, 1, 25000)
        elif kwargs['input_type'] == 'time_chunks':
            xx = reader.read_fil_data(kwargs['filterbank_filename'], start=index_start, stop=index_start+kwargs['chunk_size'])[0]
            xx = np.mean(xx.data, axis=0)
            index_start += kwargs['chunk_size']

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

    plt.legend(['median, stdev','MoM, stdev', 'MoM, MAD','median, MAD'], fontsize=kwargs['fontsize'])
    plt.xlabel('N', fontsize=kwargs['fontsize'])
    if kwargs['input_type'] == 'time_chunks':
        plt.ylabel('S/N Max (%d samples, %d chunk size)' % (kwargs['n_samples'], kwargs['chunk_size']), fontsize=kwargs['fontsize'])
    else:
        plt.ylabel('S/N Max (%d samples)' % (kwargs['n_samples']), fontsize=kwargs['fontsize'])

    plt.xscale = kwargs['xscale']
    plt.yscale = kwargs['yscale']

    plt.tight_layout()
    plt.show()
    plt.savefig(kwargs['figure_filename'], dpi=300)

def check_defaults(**kwargs):
    if kwargs['xscale'] == None:
        kwargs['xscale'] = 'log'

    if kwargs['yscale'] == None:
        kwargs['yscale'] = 'linear'

    if kwargs['fontsize'] == None:
        kwargs['fontsize'] = 12

    if kwargs['n_samples'] == None:
        kwargs['n_samples'] = 1000
    elif kwargs['input_type'] is 'time_chunks':
        kwargs['n_samples'] = 200

    if kwargs['figure_filename'] == None:
        kwargs['figure_filename'] = 'filterbank_%d.png' % kwargs['n_samples']

    if kwargs['input_type'] in ('filterbank', 'time_chunks'):
        kwargs['gaussian_noise'] = False

    if kwargs['make_figure_only'] == None:
        kwargs['make_figure_only'] = False

    kwargs['filterbank_filename'] = '/data2/output/20181020_2018-10-20-09:59:59.FRB171004_filterbank/CB17.fil'

    return kwargs


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--pickle_filename', help="Pickle filename")
    parser.add_argument('--figure_filename', help="Figure filename", type=str)
    parser.add_argument('--input_type',
                        help="""Options:
                        {'filterbank': Filterbank file (.fil),
                        'gaussian_noise': Stochastic gaussian draw,
                        'time_chunks': Discrete time chunks of size [index_start, index_start+chunk_size]}
                             """,
                        type=str, choices=['filterbank', 'gaussian_noise', 'time_chunks'])
    parser.add_argument('--chunk_size', help="Chunk size (if input_type is 'time_chunks')", type=int)
    parser.add_argument('--fontsize', help="Figure's font size", type=int)
    parser.add_argument('--gaussian_noise', help="Use gaussian noise input (True/False)", type=bool)
    parser.add_argument('--n_samples', help="Number of trials (e.g. DMs, draws, chunks)", type=int)
    parser.add_argument('--xscale', help="Scaling for the x axis", type=str, choices=['linear', 'log'])
    parser.add_argument('--yscale', help="Scaling for the y axis", type=str, choices=['linear', 'log'])
    parser.add_argument('--make_figure_only', help="Make figure only (True/False) from pickle file", type=bool)

    args = parser.parse_args()

    kwargs = check_defaults(**vars(args))

    if not kwargs['make_figure_only']:
        S1, S2, S3, S4, N = main(**kwargs)

        if args.pickle_filename:
            with open(args.pickle_filename, 'wb') as f:
                pickle.dump([S1, S2, S3, S4, N], f)
    else:
        with open(args.pickle_filename, 'rb') as f:
            S1, S2, S3, S4, N = pickle.load(f)

    make_plot(S1, S2, S3, S4, N, **kwargs)
