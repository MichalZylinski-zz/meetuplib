from setuptools import setup

# to build and upload
# python setup.py sdist bdist_wheel
# python setup.py bdist_wheel upload

setup(name='meetuplib',
      version='0.25',
      description='Meetup API library',
      url='http://github.com/michalzylinski/meetuplib',
      author='Michal Zylinski',
      author_email='michal.zylinski@gmail.com',
      license='Apache',
      packages=['meetuplib'],
      zip_safe=False)
