# -*- coding: utf-8 -*-
import unittest

from mock import Mock  # unittest.mock for Python >= 3.3

from wlmbots.lib import pagelist


class TestArticleIterator(unittest.TestCase):


    def test_article_iterator_iterates_over_categories(self):
        category_callback = Mock()
        it = pagelist.ArticleIterator(category_callback = category_callback)
        category = Mock()
        category.articles.return_value = []
        it.categories = [category]
        it.iterate_categories()
        category_callback.assert_called_once_with(category, 0, it)

    def test_article_iterator_iterates_over_articles(self):
        article_callback = Mock()
        it = pagelist.ArticleIterator(article_callback = article_callback)
        article1 = Mock()
        article2 = Mock()
        category = Mock()
        category.articles.return_value = [article1, article2]
        it.categories = [category]
        it.iterate_categories()
        article_callback.assert_any_call(article1, category, 0, it)
        article_callback.assert_any_call(article2, category, 1, it)

    def test_article_iterator_logs_every_n_articles(self):
        log_callback = Mock()
        it = pagelist.ArticleIterator(logging_callback = log_callback)
        it.log_every_n = 1
        article1 = Mock()
        article2 = Mock()
        article1.title.return_value = "Foo"
        article2.title.return_value = "Bar"
        category = Mock()
        category.articles.return_value = [article1, article2]
        it.categories = [category]
        it.iterate_categories()
        log_callback.assert_any_call(u"Fetching page 0 (Foo)")
        log_callback.assert_any_call(u"Fetching page 1 (Bar)")



class TestArticleIteratorArgumentParser(unittest.TestCase):


    def test_limit_is_set(self):
        article_iterator = Mock()
        parser = pagelist.ArticleIteratorArgumentParser(article_iterator, Mock())
        self.assertTrue(parser.check_argument("-limit:5"))
        self.assertEqual(article_iterator.limit, 5)


    def test_parser_returns_false_when_no_valid_argument_is_found(self):
        parser = pagelist.ArticleIteratorArgumentParser(Mock(), Mock())
        self.assertFalse(parser.check_argument("-foo"))


    def test_category_sets_pywikibot_category(self):
        article_iterator = Mock()
        pagelister = Mock()
        category = Mock()
        pagelister.get_county_categories_by_name.return_value = [category]
        parser = pagelist.ArticleIteratorArgumentParser(article_iterator, pagelister)
        self.assertTrue(parser.check_argument(u"-category:Baudenkmäler in Sachsen"))
        self.assertEqual(article_iterator.categories, [category])


if __name__ == '__main__':
    unittest.main()
