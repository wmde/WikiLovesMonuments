import pywikibot

class Pagelist(object):
    """ Utility class top get subcategories and articles for WLM 2015 """
    def __init__(self, site):
        self.site = site

    def get_county_categories(self, recursive=True):
        """ Get all subcategories of Liste (Kulturdenkmale in Deutschland) """
        return pywikibot.Category(self.site, "Liste (Kulturdenkmale in Deutschland)").subcategories(recursive)

    def get_list_articles(self):
        """ Return all the pages for all the categories"""
        return [article for cat in self.get_county_categories() for article in cat.articles()]
