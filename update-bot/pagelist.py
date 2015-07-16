import pywikibot
from pywikibot import config

class Pagelist(object):

    def __init__(self, site):
        self.site = site

    def get_county_categories(self):
        return pywikibot.Category(self.site, "Liste (Kulturdenkmale in Deutschland)").subcategories()

    def get_list_articles(self):
        return [article for cat in self.get_county_categories() for article in cat.articles()]
