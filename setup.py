from distutils.core import setup

setup(
    name='storm',
    version='0.1',
    packages=['storm'],
    url='http://github.com/emre/storm',
    license='MIT',
    author='Emre Yilmaz',
    author_email='mail@emreyilmaz.me',
    description='Management commands to ssh config files.',
    scripts=[
        'bin/storm'
    ],
)
