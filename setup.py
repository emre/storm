import sys

from setuptools import setup

setup(
    name='stormssh',
    version='0.4.8',
    packages=['storm'],
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
        "argparse" if sys.version_info[:2] < (2, 7) else None,
    ])),)
