"""
The classes in this module wrap the pywikibot classes so unit tests don't need a working pywikibot configuration.
"""

import pywikibot


class CategoryFetcher(object):
    """ Utility class to get pywikibot.Category objects (and their subcategories) from strings """

    def __init__(self, site, root_category_name=u"Liste (Kulturdenkmale in Deutschland)"):
        """
        :param site: The wiki to fetch the categories from
        :type site: pywikibot.Site
        :param root_category_name: Root category name
        :type root_category_name: unicode
        """
        self.site = site
        self.root_category = pywikibot.Category(self.site, root_category_name)

    def get_categories(self, recursive=True):
        """ Get all subcategories of the root category """
        return self.root_category.subcategories(recursive)

    def get_categories_filtered_by_name(self, names, recursive=True):
        """ Get all subcategories of Liste (Kulturdenkmale in Deutschland) """
        return [c for c in self.get_categories(recursive) if c.title() in names]
