"""
Distributed under the MIT License. See LICENSE.txt for more info.
"""

import os

from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver

from alert_web.models import ImageStore
from alert_web.utility.first_images import download_first_image
from alert_web.utility.tgss_images import download_tgss_image


@receiver(pre_delete, sender=ImageStore, dispatch_uid='delete_image_file')
def delete_image_file(instance, **kwargs):
    """Delete the image when the database object is deleted

    Parameters
    ----------
    instance:
        instance of the ImageStore object
    kwargs:
        keyword arguments
    """
    if instance.pk and 'no_image' not in instance.image:
        os.remove(instance.image)


@receiver(pre_save, sender=ImageStore, dispatch_uid='download_image')
def download_image(instance, **kwargs):
    """Download the image and save it to the media file

    Parameters
    ----------
    instance:
        instance of the object
    kwargs:
        keyword arguments
    """

    if not instance.pk:
        instance.image = download_first_image(instance.actual_url, instance.galaxy) \
            if instance.database_type == instance.FIRST \
            else download_tgss_image(instance.actual_url)
