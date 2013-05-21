from distutils.core import setup

setup(
    name='stormssh',
    version='0.2.1',
    packages=['storm'],
    url='http://github.com/emre/storm',
    license='MIT',
    author='Emre Yilmaz',
    author_email='mail@emreyilmaz.me',
    description='Management commands to ssh config files.',
    scripts=[
        'storm/bin/storm'
    ],
    install_requires=[
        "paramiko",
        "manage.py",
        "termcolor",
    ],)
