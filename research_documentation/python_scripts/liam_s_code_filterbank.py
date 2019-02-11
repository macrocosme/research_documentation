import numpy as np
import matplotlib.pylab as plt
def compute_mad(array, med):
    series_mad = np.abs(array - med)
    return np.median(series_mad)
def compute_mom(L):
    if len(L) < 10:
        L.sort()
        return L[int(len(L) / 2)]
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
def calc_snr(data):
    """ Calculate S/N of 1D input array (data)
    after excluding 0.05 at tails
    """
    std_chunk = data.copy()
    std_chunk.sort()
    ntime_r = len(std_chunk)
    stds = 1.148*np.sqrt((std_chunk[ntime_r//40:-ntime_r//40]**2.0).sum() /
                          (0.95*ntime_r))
    snr_ = std_chunk[-1] / stds
    return snr_
N = np.array([1, 5, 10, 25, 50, 75, 100, 250, 500, 750, 1000, 1750, 2500])
S1, S2, S3, S4, S5 = [],[],[],[], []
dinput = 'gaussian'
if dinput != 'gaussian':
    dd = data.data.mean(0)[:-50000]
print("\nBeginning median with stdev")
print("---------------------------")
for nn in N:
    d = []
    for ii in xrange(1000):
        if dinput is 'gaussian':
            x = np.random.normal(0, 1, 25000)
        else:
            ind0 = min(int(np.random.uniform()*len(dd)), len(dd)-25000)
            x = dd[ind0:ind0+25000]
        k = len(x)
        x = x[:k//nn*nn].reshape(-1, nn).mean(-1)
        snr = (x.max() - np.median(x))/(np.std(x))
        d.append(snr)
    d = np.array(d)
    S1.append(d.max())
    print("arr length, downsample factor", len(x), nn)
print("\nBeginning MoM with 1.48 MAD")
print("---------------------------")
for nn in N:
    d = []
    for ii in xrange(1000):
        print(ii)
        if dinput is 'gaussian':
            x = np.random.normal(0, 1, 25000)
        else:
            ind0 = min(int(np.random.uniform()*len(dd)), len(dd)-25000)
            x = dd[ind0:ind0+25000]
        k = len(x)
        x = x[:k//nn*nn].reshape(-1, nn).mean(-1)
        med = compute_mom(x)
        snr = (x.max() - med)/(1.48*compute_mad(x, med))
        d.append(snr)
    d = np.array(d)
    S2.append(d.max())
    print("arr length, downsample factor", len(x), nn)
print("\nBeginning median with 1.48 MAD")
print("---------------------------")
for nn in N:
    d = []
    for ii in xrange(1000):
        if dinput is 'gaussian':
            x = np.random.normal(0, 1, 25000)
        else:
            ind0 = min(int(np.random.uniform()*len(dd)), len(dd)-25000)
            x = dd[ind0:ind0+25000]
        k = len(x)
        x = x[:k//nn*nn].reshape(-1, nn).mean(-1)
        med = np.median(x)
        snr = (x.max() - med)/(1.48*compute_mad(x, med))
        d.append(snr)
    d = np.array(d)
    S3.append(d.max())
    print("arr length, downsample factor", len(x), nn)
print("\nBeginning MoM with stdev")
print("---------------------------")
for nn in N:
    d = []
    for ii in xrange(1000):
        if dinput is 'gaussian':
            x = np.random.normal(0, 1, 25000)
        else:
            ind0 = min(int(np.random.uniform()*len(dd)), len(dd)-25000)
            x = dd[ind0:ind0+25000]
        k = len(x)
        x = x[:k//nn*nn].reshape(-1, nn).mean(-1)
        snr = (x.max() - compute_mom(x))/(np.std(x))
        d.append(snr)
    d = np.array(d)
    S4.append(d.max())
    print("arr length, downsample factor", len(x), nn)
print("\nBeginning PRESTO algo with clipped tails")
print("---------------------------")
for nn in N:
    d = []
    for ii in xrange(1000):
        if dinput is 'gaussian':
            x = np.random.normal(0, 1, 25000)
        else:
            ind0 = min(int(np.random.uniform()*len(dd)), len(dd)-25000)
            x = dd[ind0:ind0+25000]
        k = len(x)
        x = x[:k//nn*nn].reshape(-1, nn).mean(-1)
        stdev = np.std(x)
        med = np.mean(x)
        indi = np.where(np.abs(x-med)<3.5*stdev)
        med = x[indi].mean()
        stdev = np.std(x[indi])
        snr = (x.max() - med)/stdev
        d.append(snr)
    d = np.array(d)
    S5.append(d.max())
    print("arr length, downsample factor", len(x), nn)
fig = plt.figure(figsize=(10,5))
plt.plot(25000./N, S1)
plt.plot(25000./N, S2)
plt.plot(25000./N, S3)
plt.plot(25000./N, S4)
plt.plot(25000./N, S5)
plt.legend(['median, stdev','MoM, MAD','median, MAD', 'MoM, stdev', 'PRESTO'], fontsize=20)
plt.ylabel('S/N Max samples', fontsize=20)
plt.xlabel('N', fontsize=20)
plt.semilogx()
plt.show()
