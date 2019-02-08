import numpy as np
from khatri_rao import khatri_rao

def xy_tolm(x, y, gain, l, m, _lambda, l0, m0):
    """ Calculates voltage beam

    if l==l0 and m==m0
        signal has size 1 x 1 x length(l0) x length(m0) and
        contains the main beam sensitivity on these locations
    otherwise
        signal has size length(l)
        and contains complete beam patterns

    beam directions on the grid defined
        x length(m) * length(l0) * length(m0)
            on a grid defined by l and m for main by l0 and m0
    """
    if l == l0 and m == m0:
        l0grid, m0grid = np.meshgrid(l0, m0)
        signal = np.zeros(len(l0grid))

        for idx in np.arange(1, len(l0grid)):
            print ('working on %d of %d' % (idx, len(l0grid)))
            xsrcdelay = -x * l0grid[idx]
            ysrcdelay = -y * m0grid[idx]
            arrayvec0 = np.exp(-2 * np.pi * idx * (xsrcdelay + ysrcdelay) / _lambda)
            arrayvec = gain * arrayvec0
            norm = np.sqrt(np.sum(np.abs(arrayvec)**2))
            signal[idx] = np.transpose(arrayvec0) * arrayvec / norm

        signal = signal.reshape([len(l0), len(m0)])
    else:
        xsrcdelay = -x * np.transpose(l0)
        ysrcdelay = -y * np.transpose(m0)
        arrayvec = gain * np.exp(-2 * np.pi * 1j * (xsrcdelay + ysrcdelay) / _lambda)
        norm = np.sqrt(np.sum(np.abs(arrayvec)**2))
        Wx = np.exp(-2 * np.pi * 1j * l * np.transpose(x) / _lambda)
        Wy = np.exp(-2 * np.pi * 1j * m * np.transpose(y) / _lambda)
        W = khatri_rao(Wx, Wy)
        signal = W * arrayvec * np.diag(1/norm)
        signal = signal.reshape([len(l), len(m), len(l0)])

    return signal
