from django.conf import settings


GALLERIES_SUBDIRECTORY = getattr(settings, 'GALLERIES_SUBDIRECTORY', 'galleries')
THUMBNAILS_SUBDIRECTORY = getattr(settings, 'THUMBNAILS_SUBDIRECTORY', 'thumbnails')
