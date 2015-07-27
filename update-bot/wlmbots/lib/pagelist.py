import pywikibot


class Pagelist(object):
    """ Utility class top get subcategories and articles for WLM 2015 """


    def __init__(self, site, root_category_name=u"Liste (Kulturdenkmale in Deutschland)"):
        self.site = site
        self.root_category = pywikibot.Category(self.site, root_category_name)


    def get_county_categories(self, recursive=True):
        """ Get all subcategories of Liste (Kulturdenkmale in Deutschland) """
        return self.root_category.subcategories(recursive)


    def get_list_articles(self):
        """ Return all the pages for all the categories"""
        return [article for cat in self.get_county_categories() for article in cat.articles()]


class ArticleIterator(object):
    """ Iterate over categories and their article pages depending on category and limit settings """

    def __init__(self, category_callback = None, article_callback = None):
        self.limit = 0
        self.categories = []
        self.category_callback = category_callback
        self.article_callback = article_callback


    def iterate_categories(self):
        counter = 0
        for category in self.categories:
            counter = self.iterate_articles(category, counter)
            if self.category_callback:
                self.category_callback(category, counter, self)
            if self.limit and counter > self.limit:
                return;

    def iterate_articles(self, category, counter):
        for article in category.articles():
            if self.article_callback:
                self.article_callback(article, category, counter, self)
            counter += 1
            if self.limit and counter > self.limit:
                return counter;
        return counter


class ArticleIteratorArgumentParser(object):
    """ Parse command line arguments -limit: and -category: and set to ArticleIterator """


    def __init__(self, article_iterator):
        self.article_iterator = article_iterator


    def check_argument(self, argument):
        if argument.find("-limit:") == 0:
            self.article_iterator.limit = int(argument[7:])
