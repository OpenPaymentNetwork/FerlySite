import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.txt')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

requires = [
    'alembic==1.0.11',
    'asn1crypto==0.24.0',
    'atomicwrites==1.3.0',
    'attrs==19.1.0',
    'beautifulsoup4==4.7.1',
    'boto3==1.9.188',
    'botocore==1.12.188',
    'certifi==2019.6.16',
    'cffi==1.12.3',
    'Chameleon==3.6.2',
    'chardet==3.0.4',
    'cognitojwt==1.1.0',
    'colander==1.7.0',
    'coverage==4.5.3',
    'cryptography==2.7',
    'deform==2.0.7',
    'ecdsa==0.13.2',
    'future==0.17.1',
    'hupper==1.8.1',
    'idna==2.8',
    'iso8601==0.1.12',
    'Jinja2==2.10.1',
    'Mako==1.0.13',
    'MarkupSafe==1.1.1',
    'more-itertools==7.1.0',
    'nose-cov==1.6',
    'nose==1.3.7',
    'Paste==3.0.8',
    'PasteDeploy==2.0.1',
    'phonenumbers==8.10.15',
    'plaster-pastedeploy==0.7',
    'plaster==1.0',
    'pluggy==0.12.0',
    'psycopg2==2.8.3',
    'py==1.8.0',
    'pyasn1==0.4.5',
    'pycparser==2.19',
    'Pygments==2.4.2',
    'pyramid-chameleon==0.3',
    'pyramid-debugtoolbar==4.5',
    'pyramid-jinja2==2.8',
    'pyramid-mako==1.0.2',
    'pyramid-retry==2.0',
    'pyramid-tm==2.2.1',
    'pyramid==1.10.4',
    'pytest-cov==2.7.1',
    'pytest==5.0.1',
    'python-jose==3.0.1',
    'repoze.lru==0.7',
    'requests==2.22.0',
    'rsa==4.0',
    'sendgrid==6.0.5',
    'six==1.12.0',
    'SQLAlchemy==1.3.5',
    'stripe==2.32.1',
    'transaction==2.4.0',
    'translationstring==1.3',
    'twilio==6.29.1',
    'urllib3==1.25.3',
    'venusian==1.2.0',
    'waitress==1.3.0',
    'WebOb==1.8.5',
    'WebTest==2.0.33',
    'zope.deprecation==4.4.0',
    'zope.interface==4.6.0',
    'zope.sqlalchemy==1.1',
]

tests_require = []

setup(
    name='backend',
    version='0.0',
    description='ferly-backend',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Pyramid',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
    ],
    author='',
    author_email='',
    url='',
    keywords='web pyramid pylons',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    extras_require={
        'testing': tests_require,
    },
    install_requires=requires,
    entry_points={
        'paste.app_factory': [
            'main = backend:main',
        ],
        'console_scripts': [
            'initialize_backend_db = backend.database.initializedb:main',
        ],
    },
)
