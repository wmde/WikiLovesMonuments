from setuptools import setup

setup(name='forward_script',
      version='0.1.0',
      description='Forward script for the Wiki Loves Monuments contents',
      url='https://github.com/wmde/WikiLovesMonuments',
      author='Wikimedia DE',
      author_email='kasia.odrozek@wikimedia.de',
      license='GPL2',
      packages=['forward_script'],
      install_requires=[
        'flask',
        'mwparserfromhell',
        'wlmbots',
        'mwclient',
        'wsgi-request-logger'
      ],
      zip_safe=False)
