setup(
    name='ckanext-keycloak-oauth',
    version='0.1',
    description='CKAN OAuth2 authentication with Keycloak',
    long_description=open('README.md').read(),
    author='Nguyen Duy Thanh Nam',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'requests-oauthlib',
        'beaker',
    ],
    entry_points="""
    [ckan.plugins]
    keycloak_oauth = keycloak_oauth.plugin:KeycloakOAuthPlugin
    """,
)
