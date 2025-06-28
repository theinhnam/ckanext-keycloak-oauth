import logging
from ckan.lib.base import BaseController, request
from pylons import config

log = logging.getLogger(__name__)

class KeycloakController(BaseController):
    def login(self):
        from keycloak_oauth.plugin import KeycloakOAuthPlugin
        url = KeycloakOAuthPlugin().login_url()
        return self.redirect_to(url)

    def callback(self):
        from keycloak_oauth.plugin import KeycloakOAuthPlugin
        plugin = KeycloakOAuthPlugin()
        oauth = plugin._get_oauth_session()
        token = oauth.fetch_token(
            config.get('ckan.keycloak_oauth.token_url'),
            client_secret=config.get('ckan.keycloak_oauth.client_secret'),
            authorization_response=request.url
        )
        session = request.environ['beaker.session']
        session['oauth_token'] = token
        session.save()
        return self.redirect_to('home')