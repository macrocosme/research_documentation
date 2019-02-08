"""
Distributed under the MIT License. See LICENSE.txt for more info.
"""

import os
import shutil
import logging

import astropy.units as u
import requests
import tarfile
import astropy.visualization as vis

from astropy.io import fits
from astropy.coordinates import SkyCoord
from matplotlib.image import imsave
from django.conf import settings
from future.standard_library import install_aliases

install_aliases()
from urllib.parse import urlparse, parse_qs

logger = logging.getLogger(__name__)


def construct_tgss_url(ra, dec):
    """Construct a query url for an image at position ra and dec.

    Note that we query for hSIZE=0.05 degree, which is equivalent to 3 arcmin.

    Parameters
    ----------
    ra:
        Right ascension (HMS format)
    dec:
        Declination (HMS format)

    Returns
    -------
    url:
        Remote query url
    """
    c = SkyCoord(ra=ra, dec=dec, frame='icrs', unit=(u.hourangle, u.degree))
    url = 'http://vo.astron.nl/tgssadr/q_fits/cutout/form?__nevow_form__=genForm' \
          '&hPOS={}%2C{}' \
          '&hSIZE=0.05' \
          '&hINTERSECT=OVERLAPS' \
          '&hFORMAT=image%2Ffits' \
          '&_DBOPTIONS_ORDER=' \
          '&_DBOPTIONS_DIR=ASC' \
          '&MAXREC=100' \
          '&_FORMAT=tar' \
          '&submit=Go'.format(c.ra.value, c.dec.value)
    return url


def download_tgss_image(url):
    """Download an image for TGSS.

    Parameters
    ----------
    url:
        url of the image.

    Returns
    -------
    file_url:
        Url of the newly downloaded file.
    """

    # parsing ra and dec from the url
    query = urlparse(url).query
    h_pos = parse_qs(query)['hPOS'][0]
    ra, dec = h_pos.split(',')

    # name of the temporary tar file to be saved locally
    local_file_name = '{}_{}.tar'.format(ra, dec)

    # getting the tar file downloaded
    request = requests.get(url, stream=True)
    with open(local_file_name, 'wb') as f:
        for chunk in request.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
        f.flush()

    tar = tarfile.open(local_file_name)
    members = tar.getmembers()

    # temp folder for the fits file
    temp_folder = local_file_name.replace('.tar', '')
    tar.extract(member=members[0], path=temp_folder)

    # removing the temporary file
    os.remove(local_file_name)

    fits_image = temp_folder + '/' + members[0].name
    hdu_list = fits.open(fits_image)
    stretch = vis.AsinhStretch(0.01) + vis.MinMaxInterval()
    file_url = settings.MEDIA_ROOT + 'database_images/' + temp_folder + '_tgss.png'

    image_data = hdu_list[0].data[0, 0]

    try:
        imsave(file_url, stretch(image_data), cmap='copper')
    except OSError:
        logger.info("Something is wrong with the fits file for url = {}".format(url))
        logger.error(OSError)
        file_url = settings.MEDIA_ROOT + 'database_images/no_image.png'

    hdu_list.close()
    shutil.rmtree(temp_folder)

    return file_url
