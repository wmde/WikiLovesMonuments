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
            self.callbacks.category(category=category, counter=counter, article_iterator=self)
            if self.limit and counter >= self.limit:
                return

    def iterate_articles(self, category, counter=0, article_arguments=None):
        category_counter = 0
        kwargs = self._get_default_article_arguments()
        if article_arguments:
            kwargs.update(article_arguments)
        for article in category.articles(**kwargs):
            if self.limit_reached(counter, category_counter):
                return counter
            if self._excluded_articles and article.title() in self._excluded_articles:
                continue
            if counter % self.log_every_n == 0:
                self.callbacks.logging(u"Fetching page {} ({})".format(counter, article.title()))
            self.callbacks.article(article=article, category=category, counter=counter,
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

    def limit_reached(self, counter, category_counter):
        """ Return True if the absolute or category limit is reached. """
        return (
            self.articles_per_category_limit and category_counter >= self.articles_per_category_limit
            ) or (
                self.limit and counter >= self.limit
            )


class ArticleIteratorCallbacks(object):

    def __init__(self, **kwargs):
        self.category = self.cb_do_nothing
        self.article = self.cb_do_nothing
        self.logging = self.cb_do_nothing
        for attr in ['category', 'article', 'logging']:
            callback_name = attr + "_callback"
            if callback_name in kwargs and kwargs[callback_name]:
                setattr(self, attr, kwargs[callback_name])

    def cb_do_nothing(self, *args, **kwargs):
        """
        Placeholder function that returns None
        """
        return None


class ArticleIteratorArgumentParser(object):
    """ Parse command line arguments -limit: and -category: and set to ArticleIterator """

    def __init__(self, article_iterator, category_fetcher):
        self.article_iterator = article_iterator
        self.category_fetcher = category_fetcher

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
            self.article_iterator.categories = self.category_fetcher.get_categories_filtered_by_name(category_names)
            return True
        else:
            return False

    def _format_category(self, category_name):
        name = category_name.strip().replace(u"_", u" ")
        if name.find(u"Kategorie:") == -1 and name.find(u"Category:") == -1:
            name = u"Kategorie:{}".format(name)
        return name
