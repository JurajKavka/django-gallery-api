import logging
import urllib
from django.contrib.auth import get_user_model
from django.core import exceptions
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils.http import urlunquote
from requests_oauthlib import OAuth2Session
from requests_oauthlib.compliance_fixes import facebook_compliance_fix
from oauthlib.oauth2 import MobileApplicationClient


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = ''

    def add_arguments(self, parser):
        """
        parser.add_argument('--username', nargs='?', type=str, required=True,
                            help='Username')

        parser.add_argument('--password', nargs='?', type=str, required=True,
                            help='Password')

        parser.add_argument('--database', default=DEFAULT_DB_ALIAS,
                            help='Specifies the database to use. Default is "default".')
        """
        pass

    def handle_mobile(self, *args, **options):
        client_id = settings.FACEBOOK_APP_ID
        authorization_base_url = 'https://www.facebook.com/v6.0/dialog/oauth'
        redirect_uri = 'https://1413d4c3.ngrok.io'     # Should match Site URL
        
        oauth = OAuth2Session(
            client=MobileApplicationClient(client_id=client_id),
            redirect_uri=redirect_uri
        )

        authorization_url, state = oauth.authorization_url(authorization_base_url)

        logger.debug(authorization_url)
        logger.debug(state)

        self.stdout.write(authorization_url)

        redirect_response = input('Paste the full redirect URL here:')

        logger.debug(oauth.token_from_fragment(redirect_response))

        r = oauth.get('https://graph.facebook.com/me?')
        # p = r.prepared()

        # logger.debug(p.url)
        # logger.debug(p.headers)

        # resp = p.send()

        logger.debug(r.request.url)
        logger.debug(r.request.headers)



    def handle_web(self, *args, **options):
        logger.debug('Facebook login test ....')
        # authorization_base_url = 'https://www.facebook.com/dialog/oauth'
        authorization_base_url = 'https://www.facebook.com/v6.0/dialog/oauth'
        token_url = 'https://graph.facebook.com/oauth/access_token'
        redirect_uri = 'https://65996efc.ngrok.io/'     # Should match Site URL

        client_id = settings.FACEBOOK_APP_ID
        client_secret = settings.FACEBOOK_CLIENT_SECRET
        # client_secret = None

        logger.debug('client_id={}'.format(client_id))
        logger.debug('client_secret={}'.format(client_secret))

        # facebook = OAuth2Session(client=MobileApplicationClient(client_id=client_id), redirect_uri=redirect_uri)
        facebook = OAuth2Session(client_id=client_id, redirect_uri=redirect_uri)
        facebook = facebook_compliance_fix(facebook)

        # Redirect user to Facebook for authorization
        authorization_url, state = facebook.authorization_url(
            authorization_base_url, 
            state=None
        )
        authorization_url_splitted = urlunquote(authorization_url).split('&')
        logger.debug(authorization_url_splitted)
        self.stdout.write(authorization_url)

        # Get the authorization verifier code from the callback url
        redirect_response = input('Paste the full redirect URL here:')

        # Fetch the access token
        token = facebook.fetch_token(token_url, client_secret=client_secret,
                                     authorization_response=redirect_response)

        logger.debug(token)

        # Fetch a protected resource, i.e. user profile
        r = facebook.get('https://graph.facebook.com/me?')
        logger.debug(r.content)
        # self.stdout.write(r.content)

    def handle(self, *args, **options):
        self.handle_mobile(*args, **options)
