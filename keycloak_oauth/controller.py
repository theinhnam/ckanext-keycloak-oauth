import logging
from flask import request, redirect
from ckan.plugins import toolkit
from ckan.config.environment import config
from keycloak_oauth.plugin import KeycloakOAuthPlugin

log = logging.getLogger(__name__)

def login():
    url = KeycloakOAuthPlugin().login_url()
    return redirect(url)

def callback():
    plugin = KeycloakOAuthPlugin()
    oauth = plugin._get_oauth_session()
    token = oauth.fetch_token(
        config.get('ckan.keycloak_oauth.token_url'),
        client_secret=config.get('ckan.keycloak_oauth.client_secret'),
        authorization_response=request.url
    )
    sess = request.environ['beaker.session']
    sess['oauth_token'] = token
    sess.save()
    return redirect(toolkit.url_for('home.index'))
