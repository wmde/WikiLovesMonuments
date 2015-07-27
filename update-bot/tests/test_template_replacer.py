# -*- coding: utf-8 -*-
import unittest

from wlmbots.lib import template_replacer


class TemplateForTesting( object ):
    def __init__( self, name = { }, params = { } ):
        self.name = name
        self.params = params


class TestTemplateReplacer( unittest.TestCase ):
    def test_get_value_returns_values( self ):
        fixture = TemplateForTesting( "", [u"a=5", u"b=Übertrag"] )
        replacer = template_replacer.TemplateReplacer( fixture )
        self.assertEqual( replacer.get_value( 'a' ), u"5" )
        self.assertEqual( replacer.get_value( 'b' ), u"Übertrag" )


    def test_get_value_strips_spaces_from_param_names( self ):
        fixture = TemplateForTesting( "", [u"a        =5", u"b\t\t=Übertrag"] )
        replacer = template_replacer.TemplateReplacer( fixture )
        self.assertEqual( replacer.get_value( 'a' ), u"5" )
        self.assertEqual( replacer.get_value( 'b' ), u"Übertrag" )


    def test_get_value_keeps_whitespace_in_values( self ):
        fixture = TemplateForTesting( "", [u"a=5\n", u"b =  Übertrag  "] )
        replacer = template_replacer.TemplateReplacer( fixture )
        self.assertEqual( replacer.get_value( 'a' ), u"5\n" )
        self.assertEqual( replacer.get_value( 'b' ), u"  Übertrag  " )


    def test_to_string_works_as_expected( self ):
        fixture = TemplateForTesting( "myTest", [u"a=5\n", u"b =  Übertrag  "] )
        replacer = template_replacer.TemplateReplacer( fixture )
        self.assertEqual( unicode( replacer ), u"{{myTest|a=5\n|b =  Übertrag  }}" )


    def test_set_value_replaces_values( self ):
        fixture = TemplateForTesting( "myTest", [u"a=5", u"b =  Übertrag  "] )
        replacer = template_replacer.TemplateReplacer( fixture )
        replacer.set_value( "a", "99" )
        self.assertEqual( unicode( replacer ), u"{{myTest|a=99|b =  Übertrag  }}" )


    def test_set_value_preserves_whitespace_in_values( self ):
        fixture = TemplateForTesting( "myTest", [u"a=5\n", u"b =  Übertrag  "] )
        replacer = template_replacer.TemplateReplacer( fixture )
        replacer.set_value( "a", "99" )
        replacer.set_value( "b", "Maximum" )
        self.assertEqual( unicode( replacer ), u"{{myTest|a=99\n|b =  Maximum  }}" )


    def test_set_value_puts_newlines_at_end_of_value( self ):
        fixture = TemplateForTesting( "myTest", [u"a=\n", u"b =\r\n"] )
        replacer = template_replacer.TemplateReplacer( fixture )
        replacer.set_value( "a", "99" )
        replacer.set_value( "b", "Maximum" )
        self.assertEqual( unicode( replacer ), u"{{myTest|a=99\n|b =Maximum\r\n}}" )


    def test_set_value_puts_newlines_at_end_of_value_while_preserving_leading_whitespace( self ):
        fixture = TemplateForTesting( "myTest", [u"a= \n", u"b =\t\r\n"] )
        replacer = template_replacer.TemplateReplacer( fixture )
        replacer.set_value( "a", "99" )
        replacer.set_value( "b", "Maximum" )
        self.assertEqual( unicode( replacer ), u"{{myTest|a= 99\n|b =\tMaximum\r\n}}" )


    def test_get_available_params( self ):
        fixture = TemplateForTesting( "", [u"a        =5", u"b\t\t=Übertrag"] )
        replacer = template_replacer.TemplateReplacer( fixture )
        self.assertEqual( replacer.get_available_params( ), [u"a", u"b"] )


    def test_param_is_empty_is_true_for_empty_params( self ):
        fixture = TemplateForTesting( "", [u"a=", u"b\t\t=Übertrag"] )
        replacer = template_replacer.TemplateReplacer( fixture )
        self.assertTrue( replacer.param_is_empty( "a" ) )


    def test_param_is_empty_is_true_for_params_with_whitespace( self ):
        fixture = TemplateForTesting( "", [u"a=  \n", u"b\t\t=Übertrag"] )
        replacer = template_replacer.TemplateReplacer( fixture )
        self.assertTrue( replacer.param_is_empty( "a" ) )


if __name__ == '__main__':
    unittest.main( )
