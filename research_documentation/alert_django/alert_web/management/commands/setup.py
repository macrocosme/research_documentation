"""
Distributed under the MIT License. See LICENSE.txt for more info.
"""

import os
from django.core.management import BaseCommand
from shutil import copyfile

from django.conf import settings


def create_path(path):
    """Create a path on drive.

    Parameters
    ----------
    path:
        Path to be created, if applicable.
    """
    if not os.path.exists(path):
        os.makedirs(path)


class Command(BaseCommand):
    """Class command superclassing BaseCommand
    """

    help = 'Performs a set up the required steps'

    def handle(self, *args, **options):
        """Handle a command

        Parameters
        ----------
        args:
            Arguments
        options:
            Options
        """

        # create database_images directory
        create_path(settings.MEDIA_ROOT + 'database_images/')

        # create csv directory
        create_path(settings.MEDIA_ROOT + 'csv/')

        # create protobuf directory
        create_path(settings.MEDIA_ROOT + 'database_protobufs/')

        # copy no_image.png to the media database image directory
        path_no_image = settings.MEDIA_ROOT + 'database_images/no_image.png'
        src = 'alert_web/static/images/no_image.png'

        copyfile(src, path_no_image)
