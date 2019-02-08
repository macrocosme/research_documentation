"""
Distributed under the MIT License. See LICENSE.txt for more info.
"""

import datetime

from django.core.management import BaseCommand

from alert_web.models import Galaxy, ImageStore
from alert_web.utility import constants
from alert_web.utility.first_images import construct_image_url
from alert_web.utility.tgss_images import construct_tgss_url


def populate_image_store():
    """Populate image store with all objects in catalog.

    Images from FIRST and TGSS are downloaded, when available, for all objects in the database.
    """

    start = datetime.datetime.now()

    galaxies = Galaxy.objects.all()

    for galaxy in galaxies:
        for database_type in [constants.FIRST, constants.TGSS]:
            try:
                ImageStore.objects.get(galaxy=galaxy, database_type=database_type)
            except ImageStore.DoesNotExist:
                url = construct_tgss_url(ra=galaxy.ra, dec=galaxy.dec) \
                    if database_type == constants.TGSS \
                    else construct_image_url(ra=galaxy.ra, dec=galaxy.dec, fits=1)

                ImageStore.objects.create(
                    galaxy=galaxy,
                    database_type=database_type,
                    actual_url=url,
                )

    end = datetime.datetime.now()
    time_diff = end - start
    print('Time taken: {} seconds for {} images'.format(time_diff.total_seconds(), len(galaxies) * 2))


def depopulate_image_store():
    """Remove all galaxy images from database.
    """
    ImageStore.objects.all().delete()


class Command(BaseCommand):
    """Class command superclassing BaseCommand
    """

    help = 'Populating ImageStore and downloading all images'

    def add_arguments(self, parser):
        """Add arguments

        Parameters
        ----------
        parser:
            parser object
        """
        parser.add_argument(
            '--task',
            dest='task',
            default='download',
            nargs='?',
            help='[download] for downloading and [reverse] for deleting the downloaded objects'
        )

    def handle(self, *args, **options):
        """Handle a command

        Parameters
        ----------
        args:
            Arguments
        options:
            Options

        Returns
        -------
            error message if applicable.
        """

        # checking for options
        if options['task'] == 'download':
            populate_image_store()
        elif options['task'] == 'reverse':
            depopulate_image_store()
        else:
            print('For usage: images -h')
            return
