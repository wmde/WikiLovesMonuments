from setuptools import setup

setup(name='wlmbots',
      version='0.2.5',
      description='Bots and scripts for the Wiki Loves Monuments contents',
      url='https://github.com/wmde/WikiLovesMonuments',
      author='Wikimedia DE',
      author_email='kasia.odrozek@wikimedia.de',
      license='GPL2',
      packages=['wlmbots'],
      install_requires=[
        'httplib2',
        'mwparserfromhell',
        'pywikibot'
      ],
      data_files=[
        ('config', ['config/commonscat_mapping.json', 'config/templates.json'])
      ],
      zip_safe=False)
