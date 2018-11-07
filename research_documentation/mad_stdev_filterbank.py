import numpy as np
import argparse
import cPickle as pickle

def read_fil_data(fn):
    x = reader.read_fil_data(fn, start=0, stop=250000)[0]
    return x

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
    data = reader.read_fil_data('/data2/output/20181020_2018-10-20-09:59:59.FRB171004_filterbank/CB17.fil', start=0, stop=250000)[0]

    S1, S2, S3, S4 = [],[],[],[]

    SS1, SS2, SS3, SS4 = {},{},{},{}

    # Initialise dicts
    for ss in [SS1, SS2, SS3, SS4]:
        for nn in N:
            ss[nn] = -999999

    for ii in range(kwargs['N_DM']):
        print (ii)
        xx = copy.deepcopy(data)
        xx.dedisperse(ii)
        xx = np.mean(xx.data, axis=0)

        for nn in N:
            print ("\t%d" % nn)

            k = len(xx)
            x = xx[:k//nn*nn].reshape(-1, nn).mean(-1)

            print ("\t\t...Step 1")
            snr = (x.max() - np.median(x))/(np.std(x))
            if snr > SS1[nn]:
                SS1[nn] = snr

            print ("\t\t...Step 2")
            med = compute_mom(x)
            snr = (x.max() - med)/(1.48*compute_mad(x, med))
            if snr > SS2[nn]:
                SS2[nn] = snr

            print ("\t\t...Step 3")
            med = np.median(x)
            snr = (x.max() - med)/(1.48*compute_mad(x, med))
            if snr > SS3[nn]:
                SS3[nn] = snr

            print ("\t\t...Step 4")
            snr = (x.max() - compute_mom(x))/(np.std(x))
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

    plt.legend(['median, stdev','MoM, MAD','median, MAD', 'MoM, stdev'], fontsize=20)
    plt.ylabel('S/N Max (1000 DMs)', fontsize=15)
    plt.xlabel('N', fontsize=20)

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

    if kwargs['N_DM'] == None:
        kwargs['N_DM'] = 1000

    if kwargs['figure_filename'] == None:
        kwargs['figure_filename'] = 'filterbank_%d.png' % kwargs['N_DM']

    return kwargs


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--pickle_filename', help="Pickle filename")
    parser.add_argument('--figure_filename', help="Figure filename", type=str)
    parser.add_argument('--N_DM', help="Number of DM trials", type=int)
    parser.add_argument('--xscale', help="Scaling for the x axis", type=str)
    parser.add_argument('--yscale', help="Scaling for the y axis", type=str)
    args = parser.parse_args()

    kwargs = check_defaults(**vars(args))

    S1, S2, S3, S4, N = main(**kwargs)

    if args.pickle_filename:
        with open(args.pickle_filename, 'wb') as f:
            pickle.dump([S1, S2, S3, S4, N], f)

    make_plot(S1, S2, S3, S4, N, **kwargs)
