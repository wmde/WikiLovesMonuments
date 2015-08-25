# -*- coding: utf-8 -*-
import unittest

from mock import Mock  # unittest.mock for Python >= 3.3

from wlmbots.lib.article_iterator import ArticlesInCategoriesIterator, ArticleIteratorArgumentParser, \
    ArticleIteratorCallbacks


class TestMultiCallbackIterator(unittest.TestCase):
    def test_iterate_over_categories(self):
        callbacks = Mock()
        iterator = ArticlesInCategoriesIterator(callbacks)
        category = Mock()
        category.articles.return_value = []
        iterator.categories = [category]
        iterator.iterate_categories()
        callbacks.category.assert_called_once_with(category=category, counter=0)

    def test_article_iterator_iterates_over_articles(self):
        callbacks = Mock()
        iterator = ArticlesInCategoriesIterator(callbacks)
        article1 = Mock()
        article2 = Mock()
        category = Mock()
        category.articles.return_value = [article1, article2]
        iterator.categories = [category]
        iterator.iterate_categories()
        callbacks.article.assert_any_call(article=article1, category=category, counter=0)
        callbacks.article.assert_any_call(article=article2, category=category, counter=1)

    def test_article_iterator_with_limit_stops_at_limit(self):
        category_callback = Mock()
        article_callback = Mock()
        callbacks = ArticleIteratorCallbacks(category_callback=category_callback, article_callback=article_callback)
        iterator = ArticlesInCategoriesIterator(callbacks)
        iterator.limit = 10
        articles = [Mock()] * 20
        category = Mock()
        category.articles.return_value = articles
        iterator.categories = [category]
        iterator.iterate_categories()
        category_callback.assert_called_once_with(category=category, counter=10)
        self.assertEqual(article_callback.call_count, 10)

    def test_article_iterator_with_multiple_categories_stops_at_limit(self):
        category_callback = Mock()
        callbacks = ArticleIteratorCallbacks(category_callback=category_callback)
        iterator = ArticlesInCategoriesIterator(callbacks)
        iterator.limit = 10
        articles = [Mock()] * 10
        category = Mock()
        category.articles.return_value = articles
        iterator.categories = [category, category]
        iterator.iterate_categories()
        category_callback.assert_called_once_with(category=category, counter=10)

    def test_category_limit_is_respected_together_with_limit(self):
        category_callback = Mock()
        article_callback = Mock()
        callbacks = ArticleIteratorCallbacks(category_callback=category_callback, article_callback=article_callback)
        iterator = ArticlesInCategoriesIterator(callbacks)
        iterator.limit = 5
        iterator.articles_per_category_limit = 3
        articles = [Mock()] * 10
        category = Mock()
        category.articles.return_value = articles
        iterator.categories = [category, category, category, category]
        iterator.iterate_categories()
        self.assertEqual(article_callback.call_count, 5)
        self.assertEqual(category_callback.call_count, 2)

    def test_article_iterator_returns_correct_counter(self):
        category_callback = Mock()
        callbacks = ArticleIteratorCallbacks(category_callback=category_callback)
        iterator = ArticlesInCategoriesIterator(callbacks)
        articles = [Mock()] * 10
        category = Mock()
        category.articles.return_value = articles
        iterator.categories = [category]
        iterator.iterate_categories()
        category_callback.assert_called_once_with(category=category, counter=10)

    def test_article_iterator_logs_every_n_articles(self):
        log_callback = Mock()
        callbacks = ArticleIteratorCallbacks(logging_callback=log_callback)
        iterator = ArticlesInCategoriesIterator(callbacks)
        iterator.log_every_n = 1
        article1 = Mock()
        article2 = Mock()
        article1.title.return_value = "Foo"
        article2.title.return_value = "Bar"
        category = Mock()
        category.articles.return_value = [article1, article2]
        iterator.categories = [category]
        iterator.iterate_categories()
        log_callback.assert_any_call(u"Fetching page 0 (Foo)")
        log_callback.assert_any_call(u"Fetching page 1 (Bar)")

    def test_excluded_articles_are_skipped(self):
        article_callback = Mock()
        callbacks = ArticleIteratorCallbacks(article_callback=article_callback)
        iterator = ArticlesInCategoriesIterator(callbacks)
        article1 = Mock()
        article2 = Mock()
        article1.title.return_value = "Foo"
        article2.title.return_value = "Bar"
        category = Mock()
        category.articles.return_value = [article1, article2]
        iterator.categories = [category]
        iterator.excluded_articles = ["Foo"]
        iterator.iterate_categories()
        article_callback.assert_called_once_with(article=article2, category=category, counter=0)


class TestArticleIteratorArgumentParser(unittest.TestCase):
    def test_limit_is_set(self):
        article_iterator = Mock()
        parser = ArticleIteratorArgumentParser(article_iterator, Mock())
        self.assertTrue(parser.check_argument("-limit:5"))
        self.assertEqual(article_iterator.limit, 5)

    def test_category_limit_is_set(self):
        article_iterator = Mock()
        parser = ArticleIteratorArgumentParser(article_iterator, Mock())
        self.assertTrue(parser.check_argument("-limit-per-category:10"))
        self.assertEqual(article_iterator.articles_per_category_limit, 10)

    def test_parser_returns_false_when_no_valid_argument_is_found(self):
        parser = ArticleIteratorArgumentParser(Mock(), Mock())
        self.assertFalse(parser.check_argument("-foo"))

    def test_category_sets_pywikibot_category(self):
        article_iterator = Mock()
        category_fetcher = Mock()
        category = Mock()
        category_fetcher.get_categories_filtered_by_name.return_value = [category]
        parser = ArticleIteratorArgumentParser(article_iterator, category_fetcher)
        self.assertTrue(parser.check_argument(u"-category:Baudenkmäler in Sachsen"))
        self.assertEqual(article_iterator.categories, [category])

    def test_category_is_cleaned_up(self):
        article_iterator = Mock()
        category_fetcher = Mock()
        category = Mock()
        category_fetcher.get_categories_filtered_by_name.return_value = [category]
        parser = ArticleIteratorArgumentParser(article_iterator, category_fetcher)
        self.assertTrue(parser.check_argument(u"-category:Baudenkmäler_in_Sachsen"))
        category_fetcher.get_categories_filtered_by_name.assert_called_once_with([u"Kategorie:Baudenkmäler in Sachsen"])

    def test_multiple_categories_are_supported(self):
        article_iterator = Mock()
        category_fetcher = Mock()
        category = Mock()
        category_fetcher.get_categories_filtered_by_name.return_value = [category]
        parser = ArticleIteratorArgumentParser(article_iterator, category_fetcher)
        self.assertTrue(parser.check_argument(u"-category:Baudenkmäler_in_Sachsen,Baudenkmäler in Bayern"))
        category_fetcher.get_categories_filtered_by_name.assert_called_once_with([u"Kategorie:Baudenkmäler in Sachsen", u"Kategorie:Baudenkmäler in Bayern"])


class TestArticleIteratorCallbacks(unittest.TestCase):

    def test_logging_callback_can_be_called(self):
        logging_callback = Mock()
        callbacks = ArticleIteratorCallbacks(logging_callback=logging_callback)
        callbacks.logging("foo")
        logging_callback.assert_called_once_with("foo")

    def test_article_callback_can_be_called(self):
        article_callback = Mock()
        article = Mock()
        callbacks = ArticleIteratorCallbacks(article_callback=article_callback)
        callbacks.article(article=article, counter=0)
        article_callback.assert_called_once_with(article=article, counter=0)

    def test_category_callback_can_be_called(self):
        category_callback = Mock()
        article = Mock()
        callbacks = ArticleIteratorCallbacks(category_callback=category_callback)
        callbacks.category(article=article, counter=0)
        category_callback.assert_called_once_with(article=article, counter=0)

    def test_unconfigured_callbacks_are_ignored(self):
        # just to check if there is no exception
        callbacks = ArticleIteratorCallbacks()
        article = Mock()
        callbacks.article(article=article, counter=0)


if __name__ == '__main__':
    unittest.main()
