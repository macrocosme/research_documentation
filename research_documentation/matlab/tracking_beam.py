'''
Construction of tracking beams (TBs)

 This script demonstrates how synthesised beams (SBs) need to be combined
 over time to form a tracking beam at a specific point within the
 field-of-view of the compound beam (CB)

 DV, 15 November 2018

 based on matlab code by (SJW, 12 December 2017)
'''

from math import pi
import numpy as np
from matplotlib import pyplot as plt

# def kr(U, varargin):
#     U = [U, varargin]
#     K = size(U{1},2);
#     if any(cellfun('size',U,2)-K)
#         error('kr:ColumnMismatch', ...
#               'Input matrices must have the same number of columns.');
#     end
#     J = size(U{end},1);
#     X = reshape(U{end},[J 1 K]);
#     for n = length(U)-1:-1:1
#         I = size(U{n},1);
#         A = reshape(U{n},[1 I K]);
#         X = reshape(bsxfun(@times,A,X),[I*J 1 K]);
#         J = I*J;
#     end
#     X = reshape(X,[size(X,1) K]);


# Taken from https://github.com/mrdmnd/scikit-tensor/blob/master/src/tensor_tools.py
def khatri_rao(matrices, reverse=False):
    # Compute the Khatri-Rao product of all matrices in list "matrices".
    # If reverse is true, does the product in reverse order.
    matorder = range(len(matrices)) if not reverse else list(reversed(range(len(matrices))))

    # Error checking on matrices; compute number of rows in result.
    # N = number of columns (must be same for each input)
    N = matrices[0].shape[1]
    # Compute number of rows in resulting matrix
    # After the loop, M = number of rows in result.
    M = 1
    for i in matorder:
        if matrices[i].ndim != 2:
            raise ValueError("Each argument must be a matrix.")
        if N != (matrices[i].shape)[1]:
            raise ValueError("All matrices must have the same number of columns.")
        M *= (matrices[i].shape)[0]

    # Computation
    # Preallocate result.
    P = np.zeros((M, N), dtype=np.complex_)

    # n loops over all column indices
    for n in range(N):
        # ab = nth col of first matrix to consider
        ab = matrices[matorder[0]][:, n]
        # loop through matrices
        for i in matorder[1:]:
            # Compute outer product of nth columns
            ab = np.outer(matrices[i][:, n], ab[:])
        # Fill nth column of P with flattened result
        P[:, n] = ab.flatten()
    return P

def xy_to_lm(x, y, gain, l, m, _lambda, l0, m0):
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
    if np.array_equal(l, l0) and np.array_equal(m, m0):
        l0grid, m0grid = np.meshgrid(l0, m0)
        signal = np.zeros(len(l0grid))

        for idx in range(1, len(l0grid)):
            print ('working on %d of %d' % (idx, len(l0grid)))
            xsrcdelay = -x * l0grid[idx]
            ysrcdelay = -y * m0grid[idx]
            arrayvec0 = np.exp(-2 * np.pi * idx * (xsrcdelay + ysrcdelay) / _lambda)
            arrayvec = gain * arrayvec0
            norm = np.sqrt(np.sum(np.asarray(np.abs(arrayvec))**2))
            signal[idx] = np.transpose(arrayvec0) * arrayvec / norm

        signal = signal.reshape([len(l0), len(m0)])
    else:
        xsrcdelay = -x * np.transpose(l0)
        ysrcdelay = -y * np.transpose(m0)
        arrayvec = gain * np.exp(-2 * np.pi * 1j * (xsrcdelay + ysrcdelay) / _lambda)
        norm = np.sqrt(np.sum(np.asarray(np.abs(arrayvec))**2))
        Wx = np.exp(-2 * np.pi * 1j * np.mat(l).transpose() * x.transpose() / _lambda)
        Wy = np.exp(-2 * np.pi * 1j * np.mat(m).transpose() * y.transpose() / _lambda)
        W = khatri_rao([Wx, Wy])
        signal = W * arrayvec * 1/norm #np.diag(1./norm)
        signal = signal.reshape([l.shape[0], m.shape[0], 1])

    return signal

def tracking_beam():
    # x-positions of the WSRT dishes in m
    xpos = np.asarray([x for x in range(10)]) * 144
    # y-positions of the WSRT dishes in m
    ypos = np.zeros(10)

    # Assumed observing wavelength in m
    _lambda = 0.21
    # Maximum frequency in Hz (== 1500 MHz)
    fmax = 1.5e9
    # Conversion from arcmin to radian
    arc_min_to_rad = (np.pi / 180) / 60
    # Maximum distance from CB center in rad
    theta_max = 15 * arc_min_to_rad
    # Speed of light in m/s
    c = 2.99792e8
    # Maximum baseline
    B_max = xpos[-1] - xpos[0]
    # Common quotient baseline in m
    Bcq = 144

    # resolution of (l, m)-grid in m
    dl = 5e-5
    # duration of observation in s
    T_obs = 12 * 3600
    # time resolution in simulation in s
    t_step = 200
    # distance of source from field center measured in SB separation
    theta_source = 6
    # azimuthal angle of source in rad
    phi_source = np.pi/3
    # angular velocity of Earth in rad/s
    omega_Earth = 2 * pi / (24 * 3600)

    """Construct grid of Synthesised Beams"""
    # wavelength at fmax
    lambda_max = c / fmax
    # distance to grating response at fmax
    theta_grating_response = lambda_max / Bcq
    # number of TABs, design parameter
    n_TABs = 12
    # TAB separation at fmax
    theta_sep_sb = theta_grating_response / n_TABs
    Nsynth = int(2 * np.floor(theta_max / theta_sep_sb) + 1)
    SBidx = -(Nsynth - 1) / np.arange(1, (Nsynth - 1)/2)

    ## define grid for calculation of beam patterns
    l = np.arange(0, theta_max, dl)
    l = np.concatenate((np.flip(-l[1:]), l), axis=0)
    m = l
    lm_distance = np.sqrt(np.asarray(np.meshgrid(l))**2 +
                        np.transpose(np.asarray(np.meshgrid(m)))**2)
    mask = np.ones(lm_distance.shape)
    mask[lm_distance > theta_max] = None

    ## example 1 of combining TABs over a 12-hour observation
    pbeam1 = np.zeros(lm_distance.shape)
    for tidx in range(int(np.floor(T_obs/t_step))):
        cur_SB_idx = np.round(theta_source * np.cos(omega_Earth * tidx * t_step + phi_source))
        rotangle = ((tidx * t_step) / (24 * 3600)) * 2 * pi
        rotmat = np.asarray([[np.cos(rotangle), -np.sin(rotangle)], [np.sin(rotangle), np.cos(rotangle)]])
        pos = np.matmul(np.mat((xpos, ypos)).transpose(), np.mat(rotmat).transpose())
        lm = np.matmul(rotmat, [cur_SB_idx * theta_sep_sb, 0])
        vbeam = xy_to_lm(pos[:, 0], pos[:, 1], np.eye(10), l, m, _lambda, lm[0], lm[1])
        pbeam1 = pbeam1 + abs(vbeam)**2 * mask

    plt.imshow(pbeam1)


if __name__ == '__main__':
  tracking_beam()
