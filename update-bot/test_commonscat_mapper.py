# -*- coding: utf-8 -*-
import unittest

import commonscat_mapper

class TestStringMethods(unittest.TestCase):

    def test_mapping(self):
        mapper = commonscat_mapper.CommonscatMapper()
        commonscat = mapper.get_commonscat_from_links(u"Foo [[Kategorie:Liste (Kulturdenkmäler in Berlin)|Liste der Kulturdenkmäler in Berlin]] Bar")
        self.assertEqual(commonscat, u"Cultural heritage monuments in Berlin‏‎")

if __name__ == '__main__':
    unittest.main()
