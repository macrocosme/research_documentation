from matplotlib import pyplot as plt
# %matplotlib inline
#%config InlineBackend.figure_format='retina'
from matplotlib import rc
rc('font', size=12)
rc('axes', titlesize=14)
rc('axes', labelsize=14)

import numpy as np


# Variables
seriess = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: []}
lens = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: []}
maxima = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: []}
moms = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: []}
mads = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: []}
snrs = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: []}
downsample_factors = [250, 200, 150, 100, 50, 25, ]#10, 1,]
loop = 10000

# Median of medians
def mom(data_array):
    select(data_array)

def select(list, left, right, n):
    while True:
        if left = right
             return left
        pivotIndex := pivot(list, left, right)
        pivotIndex := partition(list, left, right, pivotIndex)
        if n = pivotIndex
            return n
        else if n < pivotIndex
            right := pivotIndex - 1
        else
            left := pivotIndex + 1

for i in range(loop):
    j = 0
    # Generate a few arrays of different length
    array = np.random.normal(0,1,2500)

    for downsampling in downsample_factors:
        series = array[::len(array)//(len(array)//downsampling)]
        # MAX
        maximum = np.nanmax(series)

        # MOM
        # Fix implementation

        # MAD
        series_mad = series - mom
        mad = np.median(series_mad)

        # Max Signal-to-Noise Ratio
        snr = (maximum-mom)/(mad*1.48)

        lens[j] = len(series)
        if snr >= 10:
            maxima[j].append(maximum)
            moms[j].append(mom)
            mads[j].append(mad)
            snrs[j].append(snr)

        j+=1

print ("Triggers:")
print ("=========")
for j in range(len(downsample_factors)):
    print ("Array of", lens[j])
#     print ("series:\t", seriess[j])
    print ("maximum\t\t", maxima[j])
    print ("mom\t\t", moms[j])
    print ("momad\t\t", mads[j])
    print ("max_snr\t", snrs[j])
    print ()


# Start of Figure
fig, ax = plt.subplots()
plt.scatter(lens[j], len(snrs[j]))
plt.xlabel = "#Samples"
plt.ylabel = "#Triggers"
plt.title = "#Total = {s}", str(loop)


for j in range(len(downsample_factors)):
    ax.set_title("#Total = " + str(loop))
    ax.scatter(lens[j], len(snrs[j]))
    ax.set_xlabel("#Samples")
    ax.set_ylabel("#Triggers")

plt.show()

plt.savefig("10000windows.pdf")
