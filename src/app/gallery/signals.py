# -*- coding: utf-8 -*-
import logging
import os
import shutil
from django.core.files.storage import get_storage_class
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.utils.text import slugify
from .models import Gallery, Image
from . import settings as app_settings


logger = logging.getLogger(__name__)


Storage = get_storage_class()


@receiver(pre_save, sender=Gallery)
def gallery_presave(sender, instance, *args, **kwargs):
    if not instance.path:
        instance.path = slugify(instance.name)


@receiver(post_delete, sender=Gallery)
def gallery_postdelete(sender, instance, *args, **kwargs):
    logger.debug('Delete gallery directory: {}/{}'.format(
                 app_settings.GALLERIES_SUBDIRECTORY,
                 instance.path))
    try:
        instance.delete_gallery_directory()
    except Exception as e:
        logger.error(e)


@receiver(post_save, sender=Image)
def image_postsave(sender, instance, created, *args, **kwargs):
    if created:
        instance.path = os.path.basename(instance.file.name)
        instance.save(update_fields=['path'])


@receiver(post_delete, sender=Image)
def image_postdelete(sender, instance, *args, **kwargs):
    try:
        instance.delete_image_file()
    except Exception as e:
        logger.error(e)
