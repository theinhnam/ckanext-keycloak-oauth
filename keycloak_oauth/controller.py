import logging
from flask import request, redirect, Blueprint
from ckan.plugins import toolkit
from ckan.lib.helpers import url_for
from ckan.logic import get_action
from ckan.config.environment import config
from ckan.common import session
from requests_oauthlib import OAuth2Session
from ckan.lib.authenticator import User
from flask_login import login_user
from .ckan_user import CKANUser
from datetime import timedelta

log = logging.getLogger(__name__)
keycloak = Blueprint(u'keycloak', __name__, url_prefix=u'/keycloak')


def login_url():
    oauth = _get_oauth_session()
    auth_url = config.get('ckan.keycloak_oauth.auth_url')
    authorization_url, state = oauth.authorization_url(auth_url)

    from ckan.lib.base import request
    sess = request.environ['beaker.session']
    sess['oauth_state'] = state
    sess.save()
    return authorization_url

def _get_oauth_session(token=None, state=None):
    client_id = config.get('ckan.keycloak_oauth.client_id')
    scope = config.get('ckan.keycloak_oauth.scope', 'openid')
    redirect_uri = config.get('ckan.keycloak_oauth.redirect_uri')

    if token:
        return OAuth2Session(client_id, token=token)

    return OAuth2Session(
        client_id=client_id,
        redirect_uri=redirect_uri,
        scope=scope,
        state=state
    )


def login():
    url = login_url()
    return redirect(url)

def callback():
    oauth = _get_oauth_session(state=session.get('oauth_state'))
    token = oauth.fetch_token(
        config.get('ckan.keycloak_oauth.token_url'),
        client_secret=config.get('ckan.keycloak_oauth.client_secret'),
        authorization_response=request.url
    )

    userinfo = oauth.get(config.get('ckan.keycloak_oauth.userinfo_url')).json()

    user_name = userinfo.get('preferred_username')
    email = userinfo.get('email')
    fullname = userinfo.get('name')

    user_dict = {
        'name': user_name,
        'email': email,
        'fullname': fullname,
        'password': "123456789"  # Hoặc random nếu muốn bảo mật
    }

    try:
        user = get_action('user_show')(data_dict={'id': user_name})
    except toolkit.ObjectNotFound:
        user = get_action('user_create')(data_dict=user_dict)

    user_obj = CKANUser(user_name)

    duration_time = timedelta(days=730)
    login_user(user_obj, remember=True, duration=duration_time)

    rotate_token()

    session['user'] = user_name
    session['userinfo'] = userinfo
    print("TOKE ======", token.get('id_token'))
    session['id_token_hint'] = token.get('id_token')
    session.save()

    return redirect('/')

def rotate_token():
    """
    Change the CSRF token - should be done on login
    for security purposes.
    """
    from flask_wtf.csrf import generate_csrf

    field_name = config.get("WTF_CSRF_FIELD_NAME")
    if session.get(field_name):
        session.pop(field_name)
        generate_csrf()

keycloak.add_url_rule('oauth_login', '/oauth_login', view_func=login)
keycloak.add_url_rule('oauth_callback', '/oauth_callback', view_func=callback)

def get_blueprint():
    return keycloak
