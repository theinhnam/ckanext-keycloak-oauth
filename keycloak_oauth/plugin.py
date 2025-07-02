import os
import logging
from ckan.plugins import implements, SingletonPlugin
from ckan.plugins import IConfigurer, IAuthenticator, IBlueprint
from ckan.config.environment import config
from requests_oauthlib import OAuth2Session
from ckan.model.user import User
from flask import g
from flask import request, redirect
from .controller import get_blueprint
from ckan.common import session

log = logging.getLogger(__name__)

class KeycloakOAuthPlugin(SingletonPlugin):
    implements(IConfigurer)
    implements(IAuthenticator)
    implements(IBlueprint)

    def get_blueprint(self):
        return get_blueprint()

    def login(self):
        url = self.login_url()
        return redirect(url)

    def logout(self):
        id_token = session.get('id_token_hint', None)

        session.clear()

        keycloak_logout_base = config.get("ckan.keycloak_oauth.logout_url")
        redirect_uri = config.get("ckan.site_url")

        logout_url = f"{keycloak_logout_base}?post_logout_redirect_uri={redirect_uri}"
        if id_token is not None:
            logout_url += f"&id_token_hint={id_token}"

        return redirect(logout_url)

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
        oauth = self._get_oauth_session()  # đã khởi tạo với redirect_uri rồi
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
