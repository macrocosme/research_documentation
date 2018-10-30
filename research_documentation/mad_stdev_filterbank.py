import numpy as np

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

N = np.array([1, 5, 10, 50, 100, 250, 500, 1000, 2500])

S1, S2, S3, S4 = [],[],[],[]

# median + stdev
for nn in N:
    d = []
    for ii in xrange(1000):
        x = np.random.normal(0, 1, 25000)
        k = len(x)
        x = x[:k//nn*nn].reshape(-1, nn).mean(-1)
        snr = (x.max() - np.median(x))/(np.std(x))
        d.append(snr)
    d = np.array(d)
    S1.append(d.max())
    print(len(x), nn)

# MoM + 1.48*MAD with MoM (amber)
for nn in N:
    d = []
    for ii in xrange(1000):
        x = np.random.normal(0, 1, 25000)
        k = len(x)
        x = x[:k//nn*nn].reshape(-1, nn).mean(-1)
        med = compute_mom(x)
        snr = (x.max() - med)/(1.48*compute_mad(x, med))
        d.append(snr)
    d = np.array(d)
    S2.append(d.max())

# median + 1.48*MAD
for nn in N:
    d = []
    for ii in xrange(1000):
        x = np.random.normal(0, 1, 25000)
        k = len(x)
        x = x[:k//nn*nn].reshape(-1, nn).mean(-1)
        med = np.median(x)
        snr = (x.max() - med)/(1.48*compute_mad(x, med))
        d.append(snr)
    d = np.array(d)
    S3.append(d.max())

# MoM + stdev
for nn in N:
    d = []
    for ii in xrange(1000):
        x = np.random.normal(0, 1, 25000)
        k = len(x)
        x = x[:k//nn*nn].reshape(-1, nn).mean(-1)
        snr = (x.max() - compute_mom(x))/(np.std(x))
        d.append(snr)
    d = np.array(d)
    S4.append(d.max())


plot(25000./N, S1)
plot(25000./N, S2)
plot(25000./N, S3)
plot(25000./N, S4)

legend(['median, stdev','MoM, MAD','median, MAD', 'MoM, stdev'], fontsize=20)

ylabel('S/N Max samples', fontsize=20)
xlabel('N', fontsize=20)

semilogx()