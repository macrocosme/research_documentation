"""
Distributed under the MIT License. See LICENSE.txt for more info.
"""

import astropy.units as u
import astropy.visualization as vis
import matplotlib
import os
import requests
import shutil
import tarfile
from astropy.coordinates import SkyCoord
from astropy.io import fits
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from matplotlib.image import imsave

from alert_celery.tasks import generate_survey_and_email
from alert_celery.utility import survey_generation_in_progress
from alert_web.models import Galaxy, Survey, QuestionResponse, Response, QuestionOption

# this must be used like the following, as there are some crashing issues in second request to the page
# setting up the matplotlib backend as 'Agg'
matplotlib.use('Agg')
# now importing the pyplot
import matplotlib.pyplot as plt


def generate_sky_projection(request):
    """Generate a sky projection plot using matplotlib.

    Parameters
    ----------
    request:
        POST request

    Returns
    -------
    image_path:
         Full path to local image
    """
    # should not run every time, should check pickle file
    galaxies = Galaxy.objects.all()

    ra = []
    dec = []

    for galaxy in galaxies:
        ra.append(galaxy.ra)
        dec.append(galaxy.dec)

    c = SkyCoord(ra=ra, dec=dec, frame='icrs', unit=(u.hourangle, u.degree))
    ra_rad = c.ra.wrap_at(180 * u.deg).radian
    dec_rad = c.dec.radian

    plt.figure(figsize=(8, 4.2))
    plt.subplot(111, projection="aitoff")
    plt.title("Sky Projection")
    plt.grid(True)
    plt.plot(ra_rad, dec_rad, 'o', markersize=2, alpha=0.3)

    plt.subplots_adjust(top=0.95, bottom=0.0)
    image = 'sky_projection_{}.png'.format(request.user.username)
    plt.savefig(settings.MEDIA_ROOT + image)
    return settings.MEDIA_URL + image


def download_tgss_images(ra=337.95469167, dec=-8.40781389):
    """Download TGSS images

    Parameters
    ----------
    ra:
        Right ascension
    dec:
        Declination
    """
    url = 'http://vo.astron.nl/tgssadr/q_fits/cutout/form?__nevow_form__=genForm' \
          '&hPOS={}%2C{}' \
          '&hSIZE=0.5' \
          '&hINTERSECT=OVERLAPS' \
          '&hFORMAT=image%2Ffits' \
          '&_DBOPTIONS_ORDER=' \
          '&_DBOPTIONS_DIR=ASC' \
          '&MAXREC=100' \
          '&_FORMAT=tar' \
          '&submit=Go'.format(ra, dec)

    local_file_name = '{}_{}.tar'.format(ra, dec)

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

    # removing the temp file
    os.remove(local_file_name)

    fits_image = temp_folder + '/' + members[0].name
    hdu_list = fits.open(fits_image)
    stretch = vis.MinMaxInterval() + vis.AsinhStretch(0.01)
    file_url = settings.MEDIA_ROOT + 'database_images/' + temp_folder + '_tgss.png'

    image_data = hdu_list[0].data[0, 0]

    try:
        imsave(file_url, stretch(image_data), cmap='copper')
    except OSError:
        # TODO: this should go in a log.
        print("Something is wrong with the fits file")
        print(OSError)
    hdu_list.close()
    shutil.rmtree(temp_folder)


@user_passes_test(lambda usr: usr.is_staff)
def administration(request):
    """Administration actions ((re)train acton predictor for a new survey)

    Parameters
    ----------
    request:
        POST request
    Returns
    -------
    render:
        django.shortcuts.render (a page to be rendered)
    """

    message = ''
    message_class = ''

    if request.method == 'POST':
        next_action = request.POST.get('submit', None)

        if next_action == '(Re)Train Recommender':
            previous_survey = Survey.objects.filter(active=True).order_by('-creation_date').first()

            try:
                # Are there any responses for this survey?
                if previous_survey:
                    for option in QuestionOption.objects.all():
                        QuestionResponse.objects.filter(
                            response=Response.objects.get(
                                status=Response.FINISHED,
                                survey=previous_survey
                            ),
                            answer=option.option
                        )
            except (QuestionOption.DoesNotExist, QuestionResponse.DoesNotExist, Response.DoesNotExist):
                message = 'You do not have enough question responses saved yet for the current survey! ' \
                          'Try again later.'
                message_class = 'warning'
            else:

                if not survey_generation_in_progress():
                    generate_survey_and_email.delay(
                        email=request.user.email,
                        title=request.user.title,
                        first_name=request.user.first_name,
                        last_name=request.user.last_name,
                        username=request.user.username,
                    )
                    message_class = 'success'
                    message = 'A new survey creation request has been made! You will be notified via email once done.'
                else:
                    message_class = 'info'
                    message = 'A new survey creation is already underway! You need to wait until it is finished.'

    return render(
        request,
        'administration/administration.html',
        {
            'message': message,
            'message_class': message_class,
        }
    )
