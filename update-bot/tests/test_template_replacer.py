# -*- coding: utf-8 -*-
import unittest
import mwparserfromhell

from wlmbots.lib import template_replacer


def create_template(text):
    return mwparserfromhell.parse(text).filter_templates()[0]


class TestTemplateReplacer(unittest.TestCase):
    def test_get_value_returns_values(self):
        fixture = create_template(u"{{MyTest|a=5|b=Übertrag}}")
        replacer = template_replacer.TemplateReplacer(fixture)
        self.assertEqual(replacer.get_value('a'), u"5")
        self.assertEqual(replacer.get_value('b'), u"Übertrag")

    def test_get_value_strips_spaces_from_param_names(self):
        fixture = create_template(u"{{MyTest|a        =5|b\t\t=Übertrag}}")
        replacer = template_replacer.TemplateReplacer(fixture)
        self.assertEqual(replacer.get_value('a'), u"5")
        self.assertEqual(replacer.get_value('b'), u"Übertrag")

    def test_get_value_keeps_whitespace_in_values(self):
        fixture = create_template(u"{{MyTest|a=5\n|b =  Übertrag  }}")
        replacer = template_replacer.TemplateReplacer(fixture)
        self.assertEqual(replacer.get_value('a'), u"5\n")
        self.assertEqual(replacer.get_value('b'), u"  Übertrag  ")

    def test_to_string_works_as_expected(self):
        fixture = create_template(u"{{myTest|a=5\n|b =  Übertrag  }}")
        replacer = template_replacer.TemplateReplacer(fixture)
        self.assertEqual(unicode(replacer), u"{{myTest|a=5\n|b =  Übertrag  }}")

    def test_set_value_replaces_values(self):
        fixture = create_template(u"{{myTest|a=5|b =  Übertrag  }}")
        replacer = template_replacer.TemplateReplacer(fixture)
        replacer.set_value("a", "99")
        self.assertEqual(unicode(replacer), u"{{myTest|a=99|b =  Übertrag  }}")

    def test_set_value_preserves_whitespace_in_values(self):
        fixture = create_template(u"{{myTest|a=5\n|b =  Übertrag  }}")
        replacer = template_replacer.TemplateReplacer(fixture)
        replacer.set_value("a", "99")
        replacer.set_value("b", "Maximum")
        self.assertEqual(unicode(replacer), u"{{myTest|a=99\n|b =  Maximum  }}")

    def test_set_value_puts_newlines_at_end_of_value(self):
        fixture = create_template(u"{{myTest|a=\n|b =\r\n}}")
        replacer = template_replacer.TemplateReplacer(fixture)
        replacer.set_value("a", "99")
        replacer.set_value("b", "Maximum")
        self.assertEqual(unicode(replacer), u"{{myTest|a=99\n|b =Maximum\r\n}}")

    def test_set_value_puts_newlines_at_end_of_value_and_preserves_leading_whitespace(self):
        fixture = create_template(u"{{myTest|a= \n|b =\t\r\n}}")
        replacer = template_replacer.TemplateReplacer(fixture)
        replacer.set_value("a", "99")
        replacer.set_value("b", "Maximum")
        self.assertEqual(unicode(replacer), u"{{myTest|a= 99\n|b =\tMaximum\r\n}}")

    def test_get_available_params(self):
        fixture = create_template(u"{{myTest|a        =5|b\t\t=Übertrag}}")
        replacer = template_replacer.TemplateReplacer(fixture)
        self.assertEqual(replacer.get_available_params(), [u"a", u"b"])

    def test_param_is_empty_is_true_for_empty_params(self):
        fixture = create_template(u"{{myTest|a=|b\t\t=Übertrag}}")
        replacer = template_replacer.TemplateReplacer(fixture)
        self.assertTrue(replacer.param_is_empty("a"))

    def test_param_is_empty_is_true_for_missing_params(self):
        fixture = create_template(u"{{myTest|b\t\t=Übertrag}}")
        replacer = template_replacer.TemplateReplacer(fixture)
        self.assertTrue(replacer.param_is_empty("a"))

    def test_param_is_empty_is_true_for_params_with_whitespace(self):
        fixture = create_template(u"{{myTest|a=  \n|b\t\t=Übertrag}}")
        replacer = template_replacer.TemplateReplacer(fixture)
        self.assertTrue(replacer.param_is_empty("a"))

    def test_to_string_preserves_empty_params(self):
        fixture = create_template(u"{{myTest|a=  \n|\n|b\t\t=Übertrag}}")
        replacer = template_replacer.TemplateReplacer(fixture)
        self.assertEqual(unicode(replacer), u"{{myTest|a=  \n|\n|b\t\t=Übertrag}}")

if __name__ == '__main__':
    unittest.main()
