# from flask import Blueprint
# from keycloak_oauth import controller

# keycloak = Blueprint(u'keycloak', __name__, url_prefix=u'/keycloak')

# def make_routes(blueprint:Blueprint):
#     keycloak.add_url_rule('oauth_login', '/oauth_login', view_func=controller.login())
#     keycloak.add_url_rule('oauth_callback', '/oauth_callback', view_func=controller.callback())

# make_routes(keycloak)