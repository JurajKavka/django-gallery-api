import logging
import requests
from django.utils.translation import gettext as _
from oauthlib.oauth2 import MobileApplicationClient
from rest_framework.authentication import TokenAuthentication
from rest_framework import status
from rest_framework import exceptions
from rest_framework.permissions import BasePermission
from requests_oauthlib import OAuth2Session
from .. import settings as app_settings


logger = logging.getLogger(__name__)


class SimpleFbAuthentication(TokenAuthentication):

    keyword = 'Bearer'

    def authenticate_credentials(self, key):
        logger.debug('Key: {} {}'.format(self.keyword, key))

        # take token from header and check the user againts FB graph API
        headers = {
            'Authorization': '{keyword} {key}'.format(keyword=self.keyword,
                                                      key=key)
        }

        response = requests.get(app_settings.FACEBOOK_GRAPH_API_ME_URL,
                                headers=headers)

        response_body = None
        error = None

        if response.status_code != requests.codes.ok:
            logger.debug('status code: {}'.format(response.status_code))

            if response.status_code == status.HTTP_401_UNAUTHORIZED:

                try:
                    response_body = response.json()
                    error = response_body.get('error')
                except Exception as e:
                    logger.debug(e)
                    raise exceptions.AuthenticationFailed(
                        _('Authentication failed.')
                    )

                if error and error.get('type') == 'OAuthException':

                    # call facebook api for login URL
                    client_id = app_settings.FACEBOOK_APP_ID
                    redirect_uri = app_settings.FACEBOOK_REDIRECT_URI

                    authorization_base_url = \
                        app_settings.FACEBOOK_AUTHORIZATION_BASE_URL

                    oauth = OAuth2Session(
                        client=MobileApplicationClient(client_id=client_id),
                        redirect_uri=redirect_uri
                    )

                    authorization_url, state = oauth.authorization_url(
                        authorization_base_url
                    )
                    raise exceptions.AuthenticationFailed(
                        detail={
                            'detail': _('Ivalid token'),
                            'redirect_url': authorization_url,
                        }
                    )

            else:
                raise exceptions.AuthenticationFailed(
                    _('Authentication failed.')
                )

        logger.debug(response.json())

        return (response.json(), key)

    def authenticate(self, request):
        logger.debug('authenticate')
        try:
            result = super(SimpleFbAuthentication, self).authenticate(request)
        except Exception as e:
            logger.debug(e)
            raise e
        return result


class IsFbAuthenticated(BasePermission):

    def has_permission(self, request, view):
        logger.debug(request.user)

        if request.user and request.user.get('id') is not None:
            return True
        else:
            return False
