from setuptools import setup

project = "critiquebrainz"

setup(
    name=project,
    version='0.1',
    url='https://github.com/mjjc/critiquebrainz',
    description='CritiqueBrainz is a music reviews repository.',
    author='mjjc',
    author_email='mjjc1337@gmail.com',
    packages=["critiquebrainz"],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Flask',
        'Flask-SQLAlchemy',
        'Flask-WTF',
        'Flask-Script',
        'Flask-Testing',
        'Flask-Login',
        'Flask-OAuthlib',
        'Flask-RESTful',
        'nose',
        'psycopg2',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries'
    ]
)
