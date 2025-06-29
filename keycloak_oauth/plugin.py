import os
import logging
from ckan.plugins import implements, SingletonPlugin
from ckan.plugins import IConfigurer, IAuthenticator
from ckan.config.environment import config
from requests_oauthlib import OAuth2Session
from ckan.model.user import User
from flask import g
from flask import request, redirect

log = logging.getLogger(__name__)

class KeycloakOAuthPlugin(SingletonPlugin):
    implements(IConfigurer)
    implements(IAuthenticator)

    def login(self):
        url = self.login_url()
        return redirect(url)

    def update_config(self, config_):
        root = os.path.dirname(os.path.abspath(__file__))
        tpl = os.path.join(root, 'templates')
        existing = config_.get('extra_template_paths')
        if not existing:
            paths = [tpl]
        elif isinstance(existing, str):
            paths = [existing, tpl]
        else:
            paths = existing + [tpl]
        config_['extra_template_paths'] = ','.join(paths)

    def login_url(self):
        oauth = self._get_oauth_session()
        auth_url = config.get('ckan.keycloak_oauth.auth_url')
        authorization_url, state = oauth.authorization_url(auth_url)
        
        from ckan.lib.base import request
        sess = request.environ['beaker.session']
        sess['oauth_state'] = state
        sess.save()
        return authorization_url

    def identify(self):
        environ = request.environ
        sess = environ['beaker.session']
        token = sess.get('oauth_token')
        if not token:
            return None
        oauth = self._get_oauth_session(token)
        resp = oauth.get(config.get('ckan.keycloak_oauth.userinfo_url'))
        data = resp.json()
        return data.get('preferred_username')


    def authenticate(self, environ, data_dict):
        return environ.get('REMOTE_USER')

    def _get_oauth_session(self, token=None):
        client_id = config.get('ckan.keycloak_oauth.client_id')
        scope = config.get('ckan.keycloak_oauth.scope', 'openid')
        redirect_uri = config.get('ckan.keycloak_oauth.redirect_uri')
        
        if token:
            return OAuth2Session(client_id, token=token)
        return OAuth2Session(client_id, redirect_uri=redirect_uri, scope=scope)