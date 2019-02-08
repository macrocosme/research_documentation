"""
Distributed under the MIT License. See LICENSE.txt for more info.
"""

from astropy.utils.data import download_file
from astropy.io import fits
from matplotlib.image import imsave
from django.conf import settings
from astropy import visualization as vis

import logging

logger = logging.getLogger(__name__)


def replace_space(string):
    """Replace a space to %20 for url.

    Parameters
    ----------
    string:
        A string

    Returns
    -------
    string:
        A reformatted string.
    """
    return string.replace(' ', '%20')


def replace_plus_minus(string):
    """Replace the + symbol to %2B for url.

    Parameters
    ----------
    string:
        A string

    Returns
    -------
    string:
        A reformatted string.
    """
    return str(string).replace('-', '%2D').replace('+', '%2B')


def remove_plus_minus(string):
    """Remove the - and + symbols to '' for url.

    Parameters
    ----------
    string:
        A string

    Returns
    -------
    string:
        A reformatted string.
    """
    return str(string).replace('-', '').replace('+', '')


def construct_image_url(ra, dec, size=3, maxint=10, fits=1):
    """Construct the image url.

    Parameters
    ----------
    ra:
        Right ascension (HMS format)
    dec:
        Declination (HMS format)
    size:
        Size in arcmin
    maxint:
        If the image is returned as a GIF image, this parameter determines the contrast enhancement.
    fits:
        If 1, returns the image as a fits file. If 0, returns image as GIF.
    :return:
    """

    ra_dec = "{} {}".format(remove_plus_minus(ra),
                            remove_plus_minus(dec))

    ra_dec = replace_space(ra_dec)

    url = "https://third.ucllnl.org/cgi-bin/firstimage?" \
          "RA={}&" \
          "Dec=&Equinox=J2000&" \
          "ImageSize={}&" \
          "MaxInt={}&" \
          "FITS={}".format(ra_dec, size, maxint, fits)

    return url


def download_first_image(url, galaxy):
    """
    Download first image from the url
    :param url: link of the image
    :param galaxy: galaxy object
    :return: url of the saved image
    """
    stretch = vis.AsinhStretch(0.01) + vis.MinMaxInterval()

    file_url = settings.MEDIA_ROOT + 'database_images/' + galaxy.first + '.png'
    try:
        imsave(file_url, stretch(fits.open(download_file(url, cache=True))[0].data), cmap='inferno')
    except OSError:
        logger.info("Something is wrong with the fits file for url = {}".format(url))
        logger.error(OSError)
        file_url = settings.MEDIA_ROOT + 'temp_images/no_image.png'

    return file_url
