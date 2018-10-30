import numpy as np
import matplotlib.pylab as plt

import combine_profiles 

def plot_spectra(data):
	import matplotlib.pylab as plt 

	fig = plt.figure()
	data -= np.median(data, axis=-1)[..., None]

	fig.add_subplot(211)
	plt.imshow(data, aspect='auto', interpolation='nearest', 
			extent=[0, p0, 0, 1])
	#plt.colorbar()

	fig.add_subplot(212)
	plt.plot(data.mean(0))

	plt.show()

def compare_dms(files, dm, p0):
	freq_ref = 1390.62 # MHz
	bw = 131.25 # MHz
	ftop = freq_ref + bw/2. # top freq
	fbot = freq_ref - bw/2. # bottom freq
	fig = plt.figure()

	# factor by which to rebin frequency
	frq_rb = 2

	data_dm0 = combine_profiles.dedisperse_manually(files, 0.0, p0)
	data = data_dm0.mean(0).mean(0)
	data = data[:len(data)//frq_rb*frq_rb].reshape(len(data)//frq_rb, frq_rb, -1).mean(1)
	nph = data.shape[-1]
	data = data.reshape(-1, nph/4, 4).mean(-1)
	data -= np.median(data, axis=-1)[..., None]
	prof_0dm = data.mean(0)

	ax1=fig.add_subplot(411)
	plt.imshow(data, aspect='auto', interpolation='nearest', 
		extent=[0, p0, ftop, fbot], cmap='Greys')
	plt.ylabel('freq [MHz]')

	data_dm = combine_profiles.dedisperse_manually(files, dm, p0)
	data = data_dm.mean(0).mean(0)
	data = data[:len(data)//frq_rb*frq_rb].reshape(len(data)//frq_rb, frq_rb, -1).mean(1)
	nph = data.shape[-1]
	data = data.reshape(-1, nph/4, 4).mean(-1)
	data -= np.median(data, axis=-1)[..., None]
	prof_dm = data.mean(0)

	ax2=fig.add_subplot(412)
	plt.imshow(data, aspect='auto', interpolation='nearest', 
		extent=[0, p0, ftop, fbot], cmap='Greys')
	plt.ylabel('freq [MHz]')
	plt.text(0.1, .75, 'DM=0', fontsize=14, color='red')

	data_2dm = combine_profiles.dedisperse_manually(files, 2*dm, p0)
	data = data_2dm.mean(0).mean(0)
	data = data[:len(data)//frq_rb*frq_rb].reshape(len(data)//frq_rb, frq_rb, -1).mean(1)
	nph = data.shape[-1]
	data = data.reshape(-1, nph/4, 4).mean(-1)
	data -= np.median(data, axis=-1)[..., None]
	prof_2dm = data.mean(0)

	ax3 = fig.add_subplot(413)
	plt.imshow(data, aspect='auto', interpolation='nearest', 
		extent=[0, p0, ftop, fbot], cmap='Greys')
	plt.ylabel('freq [MHz]')
	plt.text(0.1, .75, 'DM=0', fontsize=14, color='red')

	ax4 = fig.add_subplot(414)
	ph = np.linspace(0, p0, len(prof_2dm))
	plt.plot(ph, prof_0dm, color='steelblue', linewidth=3)
	plt.plot(ph, prof_dm, color='grey', linewidth=3)
	plt.plot(ph, prof_2dm, color='salmon', linewidth=3)
	plt.legend(["DM=0", 
				"DM=expected", 
				"DM=2*expected"],
				loc=2,
				fontsize=12)
	plt.xlim(0, p0)
	plt.xlabel('pulse phase [s]')

	plt.show()