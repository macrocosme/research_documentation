"""
Distributed under the MIT License. See LICENSE.txt for more info.
"""

import astropy.units as u
import pickle
import os
import re
import numpy as np

from astropy.coordinates import SkyCoord
from bokeh.embed import components
from bokeh.models import ColumnDataSource
from bokeh.util.hex import hexbin
from bokeh.palettes import Spectral6
from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.transform import factor_cmap, linear_cmap
from django.conf import settings

from alert_web.models import (
    Galaxy, Response, QuestionResponse,
    QuestionDrawnResponse)
from alert_web.utility.constants import (
    display_plot_size_x, display_plot_size_y,
    sky_projection_plot_x, sky_projection_plot_y,
    scatterplot_x, scatterplot_y,
    ra_pickle_name, dec_pickle_name,
    fpeak_fint_pickle_name, log_snr_pickle_name
)

import matplotlib

# this must be used like the following, as there are some crashing issues in second request to the page
# setting up the matplotlib backend as 'Agg'
matplotlib.use('Agg')
# now importing the pyplot
import matplotlib.pyplot as plt


def generate_sky_projection(request):
    """Generate sky projection plot using matplotlib

    Parameters
    ----------
    request:
         Post request

    Returns
    -------
    image_url :
         Image location (settings.MEDIA_URL + image)
    """

    # getting pickle files location
    ra_pickle = settings.MEDIA_ROOT + ra_pickle_name
    dec_pickle = settings.MEDIA_ROOT + dec_pickle_name

    # checking pickle exists? if yes, loading from the file
    if os.path.isfile(ra_pickle) and os.path.isfile(dec_pickle):
        with open(ra_pickle, 'rb') as ra_pickle_in:
            ra_rad = pickle.load(ra_pickle_in)

        with open(dec_pickle, 'rb') as dec_pickle_in:
            dec_rad = pickle.load(dec_pickle_in)

    else:  # otherwise reading from database and saving in the pickle files
        # cleaning up pickle files if exists (can only happen if one is missing)
        if os.path.isfile(ra_pickle):
            os.remove(ra_pickle)

        if os.path.isfile(dec_pickle):
            os.remove(dec_pickle)

        galaxies = Galaxy.objects.all()

        ra = []
        dec = []

        for galaxy in galaxies:
            ra.append(galaxy.ra)
            dec.append(galaxy.dec)

        c = SkyCoord(ra=ra, dec=dec, frame='icrs', unit=(u.hourangle, u.degree))
        ra_rad = c.ra.wrap_at(180 * u.deg).radian
        dec_rad = c.dec.radian

        with open(ra_pickle, "wb") as ra_pickle_out:
            pickle.dump(ra_rad, ra_pickle_out)

        with open(dec_pickle, "wb") as dec_pickle_out:
            pickle.dump(dec_rad, dec_pickle_out)

    plt.figure(figsize=(8, 4.2))
    plt.subplot(111, projection="aitoff")
    # plt.title("Sky Projection")
    plt.grid(True)
    plt.plot(ra_rad, dec_rad, 'o', markersize=2, alpha=0.3)

    try:
        response = Response.objects.get(survey=request.session['survey_id'],
                                        user=request.user)
        question_responses = QuestionResponse.objects.filter(response=response)

        ra = []
        dec = []
        for response in question_responses:
            ra.append(response.survey_question.survey_element.galaxy.ra)
            dec.append(response.survey_question.survey_element.galaxy.dec)

        c = SkyCoord(ra=ra, dec=dec, frame='icrs', unit=(u.hourangle, u.degree))
        ra_rad2 = c.ra.wrap_at(180 * u.deg).radian
        dec_rad2 = c.dec.radian

        plt.plot(ra_rad2, dec_rad2, '*', markersize=7, alpha=1, color='red')
    except Response.DoesNotExist:  # No response yet
        pass

    # plt.plot(ra_rad, dec_rad, 'o', markersize=2, alpha=0.3)
    plt.subplots_adjust(top=0.95, bottom=0.0)
    image = 'sky_projection_{}.png'.format(request.user.username)
    plt.savefig(settings.MEDIA_ROOT + image)
    plt.close()
    return settings.MEDIA_URL + image


def get_global_fpeak_fint_over_log_snr():
    """Get global survey data for fpeak/fint vs log(snr) plot.

    This function computes bokeh.util.hex.hexbins for all galaxies in the catalog,
    where the x axis is galaxies.f_peak/galaxies.f_int, and the y axis is log10(snr),
    with snr=(galaxies.fpeak - 0.25)/galaxies.rms

    Returns
    -------
    hexbins:
        bins to be plotted by bokeh.
    """
    # getting pickle files location
    fpeak_fint_pickle = settings.MEDIA_ROOT + fpeak_fint_pickle_name
    log_snr_pickle = settings.MEDIA_ROOT + log_snr_pickle_name

    # checking pickle exists? if yes, loading from the file
    if os.path.isfile(fpeak_fint_pickle) and os.path.isfile(log_snr_pickle):
        with open(fpeak_fint_pickle, 'rb') as fpeak_fint_pickle_in:
            fpeak_fint = pickle.load(fpeak_fint_pickle_in)

        with open(log_snr_pickle, 'rb') as log_snr_pickle_in:
            log_snr = pickle.load(log_snr_pickle_in)

    else:  # otherwise reading from database and saving in the pickle files
        # cleaning up pickle files if exists (can only happen if one is missing)
        if os.path.isfile(fpeak_fint_pickle):
            os.remove(fpeak_fint_pickle)

        if os.path.isfile(log_snr_pickle):
            os.remove(log_snr_pickle)

        galaxies = Galaxy.objects.all()

        fpeak_fint = []
        log_snr = []

        for galaxy in galaxies:
            fpeak_fint.append(galaxy.fpeak / galaxy.fint)
            log_snr.append(np.log10((galaxy.fpeak - 0.25)/galaxy.rms))

        with open(fpeak_fint_pickle, "wb") as fpeak_fint_pickle_out:
            pickle.dump(fpeak_fint, fpeak_fint_pickle_out)

        with open(log_snr_pickle, "wb") as log_snr_pickle_out:
            pickle.dump(log_snr, log_snr_pickle_out)

    return hexbin(np.array(log_snr), np.array(fpeak_fint), 0.1)


def compute_request_fpeak_fint_over_log_snr(request):
    """Compute request f_peak/f_int vs log(snr).

    This function computes points for a scatter plot for currently labeled galaxies.
    The x axis is labeled_galaxies.f_peak/labeled_galaxies.f_int, and the y axis is
    log10(snr), with snr=(labeled_galaxies.fpeak - 0.25)/labeled_galaxies.rms

    Parameters
    ----------
    request:
        POST request

    Returns
    -------
    log_snr:
        numpy array used for the x axis of the scatter plot
    fpeak_fint:
        numpy array used for the y axis of the scatter plot
    """
    fpeak_fint = []
    log_snr = []

    try:
        response = Response.objects.get(survey=request.session['survey_id'],
                                        user=request.user)
        question_responses = QuestionResponse.objects.filter(response=response)

        for response in question_responses:
            galaxy = response.survey_question.survey_element.galaxy
            fpeak_fint.append(galaxy.fpeak / galaxy.fint)
            log_snr.append(np.log10((galaxy.fpeak - 0.25) / galaxy.rms))

    except Response.DoesNotExist:  # No response yet
        pass

    return log_snr, fpeak_fint


def compute_request_n_components_over_log_snr(request):
    """Compute request n-components vs log(snr).

    Similar to compute_request_fpeak_fint_over_log_snr, with the exception that the y axis is
    the number of components recorded by users during labelling.

    Parameters
    ----------
    request:
        POST request

    Returns
    -------
    x_axis:
        numpy array used for the x axis of the scatter plot
    y_axis:
        numpy array used for the y axis of the scatter plot
    """
    y_axis = []
    x_axis = []

    try:
        response = Response.objects.get(survey=request.session['survey_id'],
                                        user=request.user)

        question_responses = QuestionDrawnResponse.objects.filter(response=response)

        for question_response in question_responses:
            galaxy = question_response.survey_question.survey_element.galaxy
            y_axis.append(len(re.findall('NaN', question_response.x_coordinates)))
            x_axis.append(np.log10((galaxy.fpeak - 0.25) / galaxy.rms))

    except Response.DoesNotExist:  # No response yet
        pass

    return x_axis, y_axis


class Plot:
    """Class representing a plot.
    """
    label = ''
    script = None
    div = None

    def __init__(self, label):
        """Initialise the class.

        Parameters
        ----------
        label:
            plot label

        """
        self.label = label

        self.script, self.div = components(self._set_plot(), CDN)

    def _set_plot(self):
        """Set the bokeh plot.

        Returns
        -------
        plot:
            a bokeh figure.
        """
        fruits = ['Apples', 'Pears', 'Nectarines', 'Plums', 'Grapes', 'Strawberries']
        counts = [5, 3, 4, 2, 4, 6]

        source = ColumnDataSource(data=dict(fruits=fruits, counts=counts))

        plot = figure(x_range=fruits, y_range=(2, 8), width=display_plot_size_x, height=display_plot_size_y)
        plot.vbar(x='fruits', top='counts', width=0.9, source=source, legend="fruits",
                  line_color='white', fill_color=factor_cmap('fruits', palette=Spectral6, factors=fruits))
        plot.axis.visible = False
        plot.background_fill_color = "#FFFFFF"
        plot.background_fill_alpha = 0.8
        plot.grid.grid_line_color = None

        return plot


class NComponentsSnrPlot(Plot):
    """Class representing the N-Components vs log(SNR) plot.
    """
    request = None

    def __init__(self, request):
        """Initialise the class

        Paramters
        ---------
        request:
            Post request
        """
        self.request = request
        super(NComponentsSnrPlot, self).__init__(label='NComponentsSnr')

    def _set_plot(self):
        """Set the plot.

        Returns
        -------
        plot :
            A bokeh.plotting.figure
        """
        plot = figure(
            width=scatterplot_x,
            height=scatterplot_y,
            logo=None,
            tools=['box_zoom,wheel_zoom,reset,pan'],
        )

        x, y = compute_request_n_components_over_log_snr(self.request)

        plot.scatter(x, y,
                     marker='asterisk',
                     line_color="#ca0020",
                     fill_color="#ca0020",
                     fill_alpha=1,
                     size=12,
                     )

        plot.xaxis.axis_label = 'log10(SNR)'
        plot.yaxis.axis_label = 'n components'

        return plot


class FluxSnrPlot(Plot):
    """Class representing the f_peak/f_int vs log(SNR) plot
    """
    request = None

    def __init__(self, request):
        """Initialise the class.

        Parameters
        ----------
        request:
            POST request
        """
        self.request = request
        super(FluxSnrPlot, self).__init__(label='FluxSnr')
        # self._set_plot()

    def _set_plot(self):
        """Set the plot.

        Returns
        -------
        plot :
            A bokeh.plotting.figure
        """
        plot = figure(
            width=scatterplot_x,
            height=scatterplot_y,
            logo=None,
            tools=['box_zoom,wheel_zoom,reset,pan'],
        )

        # Plot overall points.
        bins = get_global_fpeak_fint_over_log_snr()

        plot.hex_tile(q="q", r="r", size=0.1, line_color=None, source=bins,
                      fill_color=linear_cmap('counts', 'Blues8', 0, max(bins.counts)))

        x, y = compute_request_fpeak_fint_over_log_snr(self.request)

        plot.scatter(x, y,
                     marker='asterisk',
                     line_color="#ca0020",
                     fill_color="#ca0020",
                     fill_alpha=1,
                     size=12,
                     )

        plot.xaxis.axis_label = 'log10(SNR)'
        plot.yaxis.axis_label = 'f_peak / f_int'

        return plot


class SkyProjectionPlot(Plot):
    """Class representing the sky projection plot
    """
    request = None

    def __init__(self, request):
        """Initialise the class.

        Parameters
        ----------
        request:
            POST request.
        """
        self.request = request
        super(SkyProjectionPlot, self).__init__(label='SkyProjection')

    def _set_plot(self):
        """Set the plot.

        Returns
        -------
        plot :
            A bokeh.plotting.figure
        """
        url = generate_sky_projection(self.request)

        # constructing bokeh figure
        plot = figure(
            x_range=(0, 1),
            y_range=(0, 1),
            width=sky_projection_plot_x,
            height=sky_projection_plot_y,
            logo=None,
            tools=['box_zoom,wheel_zoom,reset,pan'],
        )

        # adding image to the figure
        plot.image_url(
            url=[url], x=0, y=0, w=1, h=1, anchor="bottom_left",
        )

        plot.axis.visible = False
        plot.background_fill_color = "#000000"
        plot.background_fill_alpha = 0.8
        plot.grid.grid_line_color = None
        return plot


def get_plots(request):
    """Get the different plots to be rendered on the page.

    Parameters
    ----------
    request:
        POST request

    Returns
    -------
    plots:
        list of bokeh.plotting.figure
    """
    return [SkyProjectionPlot(request=request), FluxSnrPlot(request=request), NComponentsSnrPlot(request=request), ]
