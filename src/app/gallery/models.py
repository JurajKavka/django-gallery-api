# -*- coding: utf-8 -*-
import logging
import os
import shutil
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.storage import get_storage_class
from django.db import models
from django.utils.translation import gettext as _
from django.utils.encoding import escape_uri_path
from PIL import Image as PILImage
from . import settings as app_settings


logger = logging.getLogger(__name__)
storage = get_storage_class()()


def validate_gallery_name(value):
    """
    Validator fot the `Gallery.name` field. It can't contain '/' character.
    """
    if value and value.find('/') > -1:
        raise ValidationError(_('Gallery name can\'t contain \'/\' character'))


class Gallery(models.Model):
    """
    Model that represents gallery model.
    """
    name = models.CharField(
        _('Name'),
        max_length=1024,
        unique=True,
        help_text=_('Name of the gallery. Must be unique.'),
        validators=[validate_gallery_name],
    )

    created = models.DateTimeField(
        _('Created'),
        auto_now_add=True,
        help_text=_('Timestamp of creation.'),
    )

    modified = models.DateTimeField(
        _('Modified'),
        auto_now=True,
        help_text=_('Timestamp of last modification.'),
    )

    class Meta:
        verbose_name = _('Gallery')
        verbose_name_plural = _('Galleries')

    def __str__(self):
        return self.name

    @property
    def path(self):
        """
        Returns escaped name if the gallery for the URL (e.g. "My%20Gallery")
        """
        return escape_uri_path(self.name)

    def delete_gallery_directory(self):
        """
        Deletes gallery directory recursively with all the images and
        thumbnails.
        """
        path = escape_uri_path(self.name)

        # absolute path to gallery directory
        absolute_path = os.path.join(storage.location,
                                     app_settings.GALLERIES_SUBDIRECTORY,
                                     path)

        # detele recursively
        shutil.rmtree(absolute_path)


def image_directory_path(instance, filename):
    """
    Helper function that returns full directory where the images are uploaded.
    It is composed by main gallery subdirectory, gallery name subdirectory
    and the image file name.
    """
    return '{}/{}/{}'.format(app_settings.GALLERIES_SUBDIRECTORY,
                             instance.gallery.path, filename)


class Image(models.Model):
    """
    Model that represents image which belongs to gallery.
    """
    gallery = models.ForeignKey(
        _('Gallery'),
        verbose_name=_('Gallery'),
        help_text=_('Image belongs to gallery.'),
        on_delete=models.CASCADE,
    )

    file = models.ImageField(
        _('Image file'),
        max_length=1024,
        upload_to=image_directory_path,
        height_field='height',
        width_field='width',
        help_text=_('Representation of image in filesystem.')
    )

    height = models.PositiveSmallIntegerField(
        _('Image height'),
        null=True,
        blank=True,
        help_text=_('Image height. It will be populated automatically.')
    )

    width = models.PositiveSmallIntegerField(
        _('Image width'),
        null=True,
        blank=True,
        help_text=_('Image width. It will be populated automatically.')
    )

    path = models.CharField(
        _('Path'),
        max_length=1024,
        null=True,
        blank=True,
        help_text=_('Name of the image file (e.g. elephant.jpg).'),
    )

    fullpath = models.CharField(
        _('Full path'),
        max_length=1024,
        null=True,
        blank=True,
        unique=True,
        help_text=_('Full path is composed from gallery `name` and image path.'),
    )

    name = models.CharField(
        _('Name'),
        max_length=1024,
        null=True,
        blank=True,
        help_text=_('Name of the image. It is generated from filename.'),
    )

    created = models.DateTimeField(
        _('Created'),
        auto_now_add=True,
        help_text=_('Timestamp of creation.'),
    )

    modified = models.DateTimeField(
        _('Modified'),
        auto_now=True,
        help_text=_('Timestamp of last modification.'),
    )

    class Meta:
        verbose_name = _('Image')
        verbose_name_plural = _('Images')

    def __str__(self):
        return self.name or _('This image has no name')

    @property
    def fullpath(self):
        """
        Fullpath of the image for access image detail in URL.  It is composed
        by gallery path and the image filename.
        """
        return '{}/{}'.format(self.gallery.path, self.path)

    @classmethod
    def create_from_file(cls, gallery, file):
        """
        Cretes `Image` instance from the file (Django `File` object). Parses
        and generates `name` and assigns image to gallery.
        """
        name, extension = os.path.splitext(file.name)
        image = cls(
            gallery=gallery,
            path=file.name,
            name=name,
            file=file
        )
        return image

    def _get_image_directory(self):
        """
        Returns directory, where the image is stored. It is relative path to
        `MEDIA_ROOT`.
        """
        return os.path.dirname(self.file.name)

    def _get_thumbnail_directory(self):
        """
        Returns directory, where the thumbnail are stored within their gallery.
        """
        return os.path.join(self._get_image_directory(),
                            app_settings.THUMBNAILS_SUBDIRECTORY)

    def _get_thumbnail_name(self, x_size, y_size):
        """
        Generates and returns name for the thumbnail image. Returns tuple
        where first item is thumbnail file name and second is extension.
        """
        basename = os.path.basename(self.file.name)
        filename, extension = os.path.splitext(basename)

        thumbnail_name = '{filename}_{x_size}x{y_size}'.format(
            filename=filename,
            x_size=x_size,
            y_size=y_size,
        )

        return thumbnail_name, extension

    def _generate_thumbnail(self, pil_image, x_size, y_size):
        """
        Generates thumbanil of image (`pil_image` is Pillow image object) with
        size `x_size` and `y_size`.

        It does NOT maintain aspect ratio, only when one of the sizes is zero.
        """
        img_width = self.width
        img_height = self.height

        perserve_aspect_ratio = False

        # i don't allow to upscale images
        if x_size > img_width or y_size > img_height:
            return pil_image

        # calculate ratio
        if x_size > 0 and y_size > 0:
            if perserve_aspect_ratio:
                ratio = min(float(x_size) / img_width,
                            float(y_size) / img_height)
                new_dimensions = (int(round(img_width * ratio)),
                                  int(round(img_height * ratio)))
            else:
                new_dimensions = (x_size, y_size)
        else:
            if x_size == 0:
                ratio = float(y_size) / img_height
            else:
                ratio = float(x_size) / img_width

            new_dimensions = (int(round(img_width * ratio)),
                              int(round(img_height * ratio)))

        # thumbnail method perserves apect ratio and updates image in place,
        # so no `return` is needed
        # pil_image.thumbnail(new_dimensions)
        return pil_image.resize(new_dimensions)

    def get_thumbnail(self, x_size, y_size):
        """
        Returns thumbnail of the image with size `x_size` and `y_size`. One of
        these sizes can be zero and the other will be calculated to perserving
        aspect ratio.

        First, thumbnail is looking in storage. If exists, thumbnail is
        returnded. If does not exists, thumbnail file is generated, saved and
        returned.
        """
        # generate thumbnail name
        thumbnail_name, extension = self._get_thumbnail_name(x_size, y_size)

        # thumbnail filename with subdirectory
        thumbnail_name_with_path = os.path.join(
            self._get_thumbnail_directory(),
            '{}{}'.format(thumbnail_name, extension),
        )

        # check if `thumbnail` subdirecotry exists, if not create it
        if not storage.exists(self._get_thumbnail_directory()):
            os.mkdir(os.path.join(storage.location,
                                  self._get_thumbnail_directory()))

        # check, if thumbnail already exists. if not, create thumbnail file
        if not storage.exists(thumbnail_name_with_path):
            image = PILImage.open(self.file.path)
            image = self._generate_thumbnail(image, x_size, y_size)
            image.save(os.path.join(settings.MEDIA_ROOT,
                                    thumbnail_name_with_path))
            image.close()

        image = storage.open(thumbnail_name_with_path)
        return image

    def delete_image_file(self):
        """
        Deletes image file with all its thumbnails.
        """
        basename = os.path.basename(self.file.name)
        filename, extension = os.path.splitext(basename)

        thumbnail_directory = self._get_thumbnail_directory()

        # delete all the thumbnails
        thumbnail_files = storage.listdir(thumbnail_directory)[1]
        for thumb in thumbnail_files:
            if thumb.startswith(filename):
                storage.delete(os.path.join(thumbnail_directory, thumb))

        # delete image file
        storage.delete(self.file.name)
