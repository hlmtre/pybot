from distutils.core import setup

setup(
  name = 'yapybot',
  packages = ['yapybot'],
  version = '0.8.6.1',
  description = 'yet another python irc bot',
  author = 'Matt Weller',
  author_email = 'hellmitre@gmail.com',
  url = 'https://github.com/hlmtre/pybot',
  download_url = 'https://github.com/hlmtre/pybot/tarball/v0.8.6.1',
  keywords = ['irc', 'bot', 'modular'],
  install_requires = ['praw', 'mysql-python', 'python-twitter', 'imgurpython', 'isodate'],
  classifiers = [],
)

