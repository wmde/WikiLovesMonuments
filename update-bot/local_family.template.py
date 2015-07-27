# -*- coding: utf-8  -*-

from pywikibot import family

# Local test wiki

class Family(family.Family):

    def __init__(self):
        family.Family.__init__(self)
        self.name = 'local' # Set the family name; this should be the same as in the filename.
        self.langs = {
            'de': 'de.wikimedia.dev', # Put the hostname here.
        }

    def version(self, code):
        return "1.25.1"  # The MediaWiki version used. Not very important in most cases.

    def scriptpath(self, code):
        return '/w' # The relative path of index.php, api.php : look at your wiki address.
# This line may need to be changed to /wiki or /w,
# depending on the folder where your mediawiki program is located.
# Note: Do not _include_ index.php, etc.
