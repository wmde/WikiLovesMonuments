"""
Iterators for Categories and Articles
"""


class ArticleIterator(object):
    """ Iterate over articles in a category, limiting the number of articles returned """

    def __init__(self, category, config=None):
        self.limit = 0
        self.articles_per_category_limit = 0
        self.log_every_n = 100
        self.category = category
        self._excluded_articles = {}
        if config is not None:
            self.configure(config)
        self.counter_offset = 0

    def __iter__(self):
        return self.iterate_articles()

    def iterate_articles(self, article_arguments=None):
        counter = self.counter_offset
        category_counter = 0
        kwargs = self._get_default_article_arguments()
        if article_arguments:
            kwargs.update(article_arguments)
        for article in self.category.articles(**kwargs):
            if self._limit_reached(counter, category_counter):
                return
            if self._excluded_articles and article.title() in self._excluded_articles:
                continue
            yield article, self.category, counter
            counter += 1
            category_counter += 1

    def configure(self, config):
        """
        :param config: Configuration settings
        :type config: ArticleIteratorConfiguration
        """
        for prop in ["limit", "articles_per_category_limit", "excluded_articles"]:
            setattr(self, prop, getattr(config, prop))

    @property
    def excluded_articles(self):
        return self._excluded_articles.keys()

    @excluded_articles.setter
    def excluded_articles(self, value):
        self._excluded_articles = {i: True for i in value}

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


class ArticleIteratorConfiguration(object):
    """ Store configuration options for ArticleIterator
    """
    def __init__(self, limit=0, articles_per_category_limit=0, excluded_articles=None):
        self.limit = limit
        self.articles_per_category_limit = articles_per_category_limit
        self.excluded_articles = [] if excluded_articles is None else excluded_articles


class CallbackIterator(object):
    """
    Iterator class that calls the callback for every item.

    Returns every item unchanged.
    """

    def __init__(self, iterable, callback_function):
        self.iterable = iter(iterable)
        self.callback = callback_function

    def __iter__(self):
        return self

    def next(self):
        item = self.iterable.next()
        self.callback(item)
        return item


class LoggingIterator(object):
    """
        Logs every n articles
    """
    def __init__(self, iterable, log_function, log_every_n=100):
        self.iterable = iter(iterable)
        self.log_function = log_function
        self.log_every_n = log_every_n

    def __iter__(self):
        return self

    def next(self):
        article, category, counter = self.iterable.next()
        if counter % self.log_every_n == 0:
            self.log_function(u"Fetching page {} ({})".format(counter, article.title()))
        return article, category, counter


class CategoryIterator(object):

    def __init__(self, categories):
        self.categories = categories

    def __iter__(self):
        return self.categories

    def get_article_iterators(self, config):
        article_iterators = []
        for category in self.categories:
            article_iterators.append(ArticleIterator(category, config))
        return article_iterators


class ArticlesInCategoriesIterator(object):
    """
    Iterate over Articles in Categories.

    """

    def __init__(self, callbacks, categories=None):
        self.limit = 0
        self.articles_per_category_limit = 0
        self.log_every_n = 100
        self.callbacks = callbacks
        self.categories = [] or categories
        self.excluded_articles = {}

    def iterate_categories(self):
        counter = 0
        category_iterator = CategoryIterator(self.categories)
        config = ArticleIteratorConfiguration(self.limit, self.articles_per_category_limit, self.excluded_articles)
        for article_iterator in category_iterator.get_article_iterators(config):
            article_iterator.log_every_n = self.log_every_n
            article_iterator.counter_offset = counter
            wrapped_iterator = self._wrap_article_iterator(article_iterator)
            for _ in wrapped_iterator:
                counter += 1
            self.callbacks.category(category=article_iterator.category, counter=counter)
            if self.limit and counter >= self.limit:
                break

    def _wrap_article_iterator(self, article_iterator):
        logging = LoggingIterator(article_iterator, self.callbacks.logging)
        callback = CallbackIterator(logging, self._tuple_result_to_callback)
        return callback

    def _tuple_result_to_callback(self, tuple_result):
        article, category, counter = tuple_result
        self.callbacks.article(article=article, category=category, counter=counter)


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
