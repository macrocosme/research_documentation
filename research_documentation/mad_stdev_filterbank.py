import numpy as np
import argparse

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

def main():
    from arts_analysis import reader
    import copy

    # THE MAIN EVENT IS HAPPENING HERE.
    N = np.array([1, 5, 10, 50, 100, 250, 500, 1000, 2500])
    data = reader.read_fil_data('/data2/output/20181020_2018-10-20-09:59:59.FRB171004_filterbank/CB17.fil', start=0, stop=250000)[0]

    S1, S2, S3, S4 = [],[],[],[]

    SS1, SS2, SS3, SS4 = {},{},{},{}

    # Initialise dicts
    for ss in [SS1, SS2, SS3, SS4]:
        for nn in N:
            ss[nn] = -999999

    for ii in range(1,1001, 10):
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

def make_plot(S1, S2, S3, S4, N, fn="filterbank.png"):
    from matplotlib import pyplot as plt
    plt.plot(25000./N, S1)
    plt.plot(25000./N, S2)
    plt.plot(25000./N, S3)
    plt.plot(25000./N, S4)

    plt.legend(['median, stdev','MoM, MAD','median, MAD', 'MoM, stdev'], fontsize=20)
    plt.ylabel('S/N Max (100 DMs)', fontsize=20)
    plt.xlabel('N', fontsize=20)

    # plt.yscale = 'log'
    # plt.xscale = 'linear'
    plt.semilogx()

    plt.tight_layout()
    plt.show()
    plt.savefig(fn)

if __name__ == "__main__":
    S1, S2, S3, S4, N = main()
    make_plot(S1, S2, S3, S4, N)
