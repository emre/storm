import sys

from setuptools import setup, find_packages

setup(
    name='stormssh',
    version='0.5',
    packages=find_packages(),
    package_data={'storm': ['templates/*.html', 'static/css/*.css',
                            'static/css/themes/storm/*.css', 'static/css/themes/storm/img/*.png',
                            'static/js/*.js', 'static/js/core/*.js']},
    include_package_data=True,
    url='http://github.com/emre/storm',
    license='MIT',
    author='Emre Yilmaz',
    author_email='mail@emreyilmaz.me',
    description='Management commands to ssh config files.',
    entry_points={
        'console_scripts': [
            'storm = storm.__main__:main',
        ],
    },
    install_requires=list(filter(None, [
        "paramiko",
        "termcolor",
        "flask",
        "argparse" if sys.version_info[:2] < (2, 7) else None,
    ])),)
