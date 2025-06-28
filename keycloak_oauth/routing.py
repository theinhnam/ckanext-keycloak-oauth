from keycloak_oauth import controller

def make_routes(map):
    map.connect('oauth_login', '/oauth_login', controller=controller, action='login')
    map.connect('oauth_callback', '/oauth_callback', controller=controller, action='callback')
