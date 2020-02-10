from django.conf import settings


GALLERIES_SUBDIRECTORY = getattr(settings, 'GALLERIES_SUBDIRECTORY', 'galleries')

THUMBNAILS_SUBDIRECTORY = getattr(settings, 'THUMBNAILS_SUBDIRECTORY', 'thumbnails')

FACEBOOK_AUTHORIZATION_BASE_URL = getattr(
    settings,
    'FACEBOOK_AUTHORIZATION_BASE_URL',
    'https://www.facebook.com/v6.0/dialog/oauth'
)

FACEBOOK_APP_ID = getattr(settings, 'FACEBOOK_APP_ID', None)

FACEBOOK_CLIENT_SECRET = getattr(settings, 'FACEBOOK_CLIENT_SECRET', None)

FACEBOOK_REDIRECT_URI = getattr(settings, 'FACEBOOK_REDIRECT_URI', None)

FACEBOOK_GRAPH_API_ME_URL = getattr(
    settings,
    'FACEBOOK_GRAPH_API_ME_URL',
    'https://graph.facebook.com/me?'
)
