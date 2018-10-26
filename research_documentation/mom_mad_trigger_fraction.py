#!/bin/python3
import numpy as np

from matplotlib import pyplot as plt
from matplotlib import rc

rc('font', size=12)
rc('axes', titlesize=14)
rc('axes', labelsize=14)

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

def downsample(array, downsampling):
    if downsampling == 0:
        return array

    series = []
    for i in range(0, len(array), downsampling):
        series.append(np.mean(array[i:i+downsampling]))
    return np.asarray(series)


def draw(n_samples=2500):
    return np.random.normal(0, 1, n_samples)


def snr_median_mad(n_trials=1000, downsampling_levels=250, n_samples=2500):
    SNRs = np.zeros([downsampling_levels, n_trials])

    for trial in range(n_trials):
        distribution = draw(n_samples)
        for level in range(downsampling_levels):
            distribution = downsample(distribution, level)
            med = np.median(distribution)
            SNRs[level, trial] = (np.max(distribution) - med) / (compute_mad(distribution, med) * 1.48)
    return SNRs


def snr_mom_mad(n_trials=1000, downsampling_levels=250, n_samples=2500):
    SNRs = np.zeros([downsampling_levels, n_trials])

    for trial in range(n_trials):
        distribution = draw(n_samples)
        for level in range(downsampling_levels):
            distribution = downsample(distribution, level)
            mom = compute_mom(distribution)
            SNRs[level, trial] = (np.max(distribution) - mom) / (compute_mad(distribution, mom) * 1.48)

    return SNRs


def plot_trigger_ratio(SNRs, threshold=10, figure_name="trigger_ratio_median"):
    fig, ax = plt.subplots()

    for level in range(SNRs.shape[0]):
        if level != 0:
            ax.scatter(n_samples / level,
                       len(SNRs[level][np.where(SNRs[level] > threshold)]) / n_trials,
                       color='black')
        else:
            ax.scatter(n_samples,
                       len(SNRs[level][np.where(SNRs[level] > threshold)]) / n_trials,
                       color='black')

        ax.set_xlabel("N")
        ax.set_ylabel("Trigger fraction (SNR>" + str(threshold) + ")")

        plt.savefig(figure_name + "_threshold_" + str(threshold) + ".pdf")


def plot_max_snr_per_downsampling_level(SNRs, figure_name="max_snr_per_downsampling_median"):
    fig, ax = plt.subplots()

    for level in range(SNRs.shape[0]):
        if level != 0:
            ax.scatter(n_samples / level,
                       np.max(SNRs[level]),
                       color='black')
        else:
            ax.scatter(n_samples,
                       np.max(SNRs[level]),
                       color='black')

        ax.set_xlabel("N")
        ax.set_ylabel("Max(SNR)")

    plt.savefig(figure_name + ".pdf")

if __name__ == "__main__":
    n_trials = 1000
    downsampling_levels = 250
    n_samples = 2500

    SNR_median = snr_median_mad(n_trials, downsampling_levels, n_samples)
    SNR_mom = snr_mom_mad(n_trials, downsampling_levels, n_samples)

    plot_trigger_ratio(SNR_median, 6)
    plot_trigger_ratio(SNR_mom, 6, figure_name="trigger_ratio_median")

    plot_max_snr_per_downsampling_level(SNR_median)
    plot_max_snr_per_downsampling_level(SNR_mom, figure_name="max_snr_per_downsampling_mom")

