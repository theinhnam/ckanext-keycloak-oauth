import logging
from ckan.plugins import implements, SingletonPlugin
from ckan.plugins import IConfigurer, IRoutes, IAuthenticator
from requests_oauthlib import OAuth2Session
from pylons import config

log = logging.getLogger(__name__)

class KeycloakOAuthPlugin(SingletonPlugin):
    implements(IConfigurer)
    implements(IRoutes)
    implements(IAuthenticator)

    def update_config(self, config_):
        extra = config_.get('extra_template_paths', [])
        extra.append(__import__('keycloak_oauth').__path__[0] + '/templates')
        config_['extra_template_paths'] = extra

    def before_map(self, map_):
        from keycloak_oauth.controller import KeycloakController
        map_.connect('oauth_login', '/oauth_login', controller='keycloak_oauth.controller:KeycloakController', action='login')
        map_.connect('oauth_callback', '/oauth_callback', controller='keycloak_oauth.controller:KeycloakController', action='callback')
        return map_

    def login_url(self):
        oauth = self._get_oauth_session()
        auth_url = self._get_setting('auth_url')
        redirect_uri = self._get_setting('redirect_uri')
        authorization_url, state = oauth.authorization_url(
            auth_url,
            redirect_uri=redirect_uri
        )
        session = __import__('pylons').request.environ['beaker.session']
        session['oauth_state'] = state
        session.save()
        return authorization_url

    def identify(self, environ):
        session = environ['beaker.session']
        token = session.get('oauth_token')
        if token:
            oauth = self._get_oauth_session(token)
            resp = oauth.get(self._get_setting('userinfo_url'))
            data = resp.json()
            return data.get('preferred_username')
        return None

    def authenticate(self, environ, data_dict):
        return environ.get('REMOTE_USER')

    def _get_oauth_session(self, token=None):
        client_id = self._get_setting('client_id')
        scope = self._get_setting('scope') or 'openid'
        if token:
            return OAuth2Session(client_id, token=token)
        return OAuth2Session(
            client_id,
            redirect_uri=self._get_setting('redirect_uri'),
            scope=scope
        )

    def _get_setting(self, name):
        return config.get(f'ckan.keycloak_oauth.{name}')