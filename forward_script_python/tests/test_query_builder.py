# -*- coding: utf-8 -*-
import unittest

from forward_script.lib import query_builder
from mock import Mock


class TestQueryBuilder(unittest.TestCase):

    def setUp(self):
        self._page_info = Mock()

    def test_category_is_added(self):
        self._page_info.category = 'Test'
        query = query_builder.get_query('', self._page_info, 'Test_Page')
        self.assertTrue('&categories=Test' in query)

    def test_category_prefix_is_removed(self):
        self._page_info.category = 'Category:Test'
        query = query_builder.get_query('', self._page_info, 'Test_Page')
        self.assertTrue('&categories=Test' in query)

    def test_additional_categories_are_added(self):
        self._page_info.category = 'Test'
        query = query_builder.get_query('', self._page_info, 'Test Page', '', None, ['Foo', 'Bar'])
        self.assertTrue('&categories=Test%7CFoo%7CBar' in query)

    def test_lat_and_lon_are_added(self):
        self._page_info.category = ''
        query = query_builder.get_query('', self._page_info, 'Test Page', '', {'lat': 1, 'lon': 2.2335455})
        self.assertTrue('&lat=1' in query)
        self.assertTrue('&lon=2.2335455' in query)

    def test_empty_lat_and_lon_are_filtered(self):
        self._page_info.category = ''
        query = query_builder.get_query('', self._page_info, 'Test Page', '', {'lat': '', 'lon': ''})
        self.assertFalse('&lat=' in query)
        self.assertFalse('&lon=' in query)

    def test_objref_is_added_if_id_is_usable(self):
        self._page_info.category = ''
        self._page_info.has_usable_id = True
        query = query_builder.get_query('', self._page_info, 'Test Page', '123')
        self.assertTrue('&objref=de%7CTest+Page%7C123' in query)

    def test_objref_is_left_out_if_id_is_not_usable(self):
        self._page_info.category = ''
        self._page_info.has_usable_id = False
        query = query_builder.get_query('', self._page_info, 'Test Page', '123')
        self.assertFalse('&objref=de%7CTest+Page%7C123' in query)

    def test_objref_encodes_as_utf_8(self):
        self._page_info.category = ''
        self._page_info.has_usable_id = True
        query = query_builder.get_query('', self._page_info, u'Baudenkmäler', '123')
        self.assertTrue('&objref=de%7CBaudenkm%C3%A4ler%7C123' in query)

    def test_fields_are_added_if_id_is_valid(self):
        self._page_info.category = ''
        self._page_info.has_valid_id = True
        query = query_builder.get_query('', self._page_info, 'Test Page', '123')
        self.assertTrue('&fields%5B%5D=123' in query)

    def test_fields_are_left_out_if_id_is_invalid(self):
        self._page_info.category = ''
        self._page_info.has_valid_id = False
        query = query_builder.get_query('', self._page_info, 'Test Page', '123')
        self.assertFalse('&fields%5B%5D=123' in query)

    def test_update_list_is_added_if_no_image_exists(self):
        self._page_info.category = ''
        self._page_info.has_image = False
        query = query_builder.get_query('', self._page_info, 'Test Page', '123')
        self.assertTrue('&updateList=1' in query)

    def test_update_list_is_left_out_if_image_exists(self):
        self._page_info.category = ''
        self._page_info.has_image = True
        self._page_info.has_usable_id = True
        query = query_builder.get_query('', self._page_info, 'Test Page', '123')
        self.assertFalse('&updateList=1' in query)

if __name__ == '__main__':
    unittest.main()
