import sys

from setuptools import setup

setup(
    name='stormssh',
    version='0.5',
    packages=['storm'],
    url='http://github.com/emre/storm',
    license='MIT',
    author='Emre Yilmaz',
    author_email='mail@emreyilmaz.me',
    description='Management commands to ssh config files.',
    data_files=[
        ('storm/static/css', [
            'storm/static/css/style.css'
        ]),
        ('storm/static/css/themes/storm', [
            'storm/static/css/themes/storm/normalize.min.css',
            'storm/static/css/themes/storm/style.css'
        ]),
        ('storm/static/css/themes/storm/img', [
            'storm/static/css/themes/storm/img/delete.png',
            'storm/static/css/themes/storm/img/edit.png',
            'storm/static/css/themes/storm/img/info.png',
            'storm/static/css/themes/storm/img/logo.png'
        ]),
        ('storm/static/js', [
            'storm/static/js/main.js'
        ]),
        ('storm/static/js/core', [
            'storm/static/js/core/angular.min.js'
        ])
    ],
    entry_points={
        'console_scripts': [
            'storm = storm.__main__:main',
        ],
    },
    install_requires=list(filter(None, [
        "paramiko",
        "termcolor",
        "argparse" if sys.version_info[:2] < (2, 7) else None,
    ])),)
