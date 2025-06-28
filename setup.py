from setuptools import setup, find_packages

setup(
    name='ckanext-keycloak-oauth',
    version='0.1.0',
    description='CKAN extension for Keycloak OAuth2 authentication',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Nam Nguyen Duy Thanh',
    author_email='your@email.com',
    url='https://github.com/youruser/ckanext-keycloak-oauth',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'requests-oauthlib',
        'beaker',
    ],
    entry_points='''
        [ckan.plugins]
        keycloak_oauth = keycloak_oauth.plugin:KeycloakOAuthPlugin
    ''',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        # 'Framework :: CKAN',  ← xoá dòng này đi
    ],
    python_requires='>=3.6',
)