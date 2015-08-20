"""
The class ArticleIterator iterats over categories and their article pages,
depending on category and limit settings.

The class ArticleIteratorArgumentParser takes arguments form the command line and
sets them to an ArticleIterator instance.
"""


class ArticleIterator(object):
    """ Iterate over categories and their article pages depending on category and limit settings """

    def __init__(self, callbacks, categories=None):
        self.limit = 0
        self.articles_per_category_limit = 0
        self.log_every_n = 100
        self.callbacks = callbacks
        self.categories = [] if categories is None else categories
        self._excluded_articles = {}

    def iterate_categories(self):
        counter = 0
        for category in self.categories:
            counter = self.iterate_articles(category, counter)
            self.callbacks("category", category=category, counter=counter, article_iterator=self)
            if self.limit and counter >= self.limit:
                return

    def iterate_articles(self, category, counter=0, article_arguments=None):
        category_counter = 0
        kwargs = self._get_default_article_arguments()
        if article_arguments:
            kwargs.update(article_arguments)
        for article in category.articles(**kwargs):
            if self._limit_reached(counter, category_counter):
                return counter
            if self._excluded_articles and article.title() in self._excluded_articles:
                continue
            if counter % self.log_every_n == 0:
                self.callbacks("logging", u"Fetching page {} ({})".format(counter, article.title()))
            self.callbacks("article", article=article, category=category, counter=counter,
                           article_iterator=self)
            counter += 1
            category_counter += 1
        return counter

    @property
    def excluded_articles(self):
        return self._excluded_articles.keys()

    @excluded_articles.setter
    def excluded_articles(self, value):
        self._excluded_articles = {i : True for i in value}

    def _get_default_article_arguments(self):
        args = {}
        if self.limit:
            args["total"] = self.limit
        if self.articles_per_category_limit and self.articles_per_category_limit < self.limit:
            args["total"] = self.articles_per_category_limit
        return args

    def _limit_reached(self, counter, category_counter):
        """ Return True if the absolute or category limit is reached. """
        return (
            self.articles_per_category_limit and category_counter >= self.articles_per_category_limit
            ) or (
                self.limit and counter >= self.limit
            )

class ArticleIteratorCallbacks(object):

    def __init__(self, category_callback=None, article_callback=None, logging_callback=None):
        self.category = category_callback
        self.article = article_callback
        self.logging = logging_callback

    def has_callback(self, name):
        return getattr(self, name) is not None

    def __call__(self, name, *args, **kwargs):
        """
        Dispatch call to callback function or return None if no callback
        function is configured.
        """
        if self.has_callback(name):
            return getattr(self, name)(*args, **kwargs)
        else:
            return None

class ArticleIteratorArgumentParser(object):
    """ Parse command line arguments -limit: and -category: and set to ArticleIterator """

    def __init__(self, article_iterator, pagelister):
        self.article_iterator = article_iterator
        self.pagelister = pagelister

    def check_argument(self, argument):
        if argument.find("-limit:") == 0:
            self.article_iterator.limit = int(argument[7:])
            return True
        if argument.find("-limit-per-category:") == 0:
            self.article_iterator.articles_per_category_limit = int(argument[20:])
            return True
        elif argument.find("-category:") == 0:
            category_names = argument[10:].split(",")
            category_names = [self._format_category(n) for n in category_names]
            self.article_iterator.categories = self.pagelister.get_county_categories_by_name(category_names)
            return True
        else:
            return False

    def _format_category(self, category_name):
        name = category_name.strip().replace(u"_", u" ")
        if name.find(u"Kategorie:") == -1 and name.find(u"Category:") == -1:
            name = u"Kategorie:{}".format(name)
        return name
