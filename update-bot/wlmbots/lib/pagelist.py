import pywikibot


class Pagelist( object ):
    """ Utility class top get subcategories and articles for WLM 2015 """


    def __init__( self, site, root_category_name = u"Liste (Kulturdenkmale in Deutschland)" ):
        self.site = site
        self.root_category = pywikibot.Category( self.site, root_category_name )


    def get_county_categories( self, recursive = True ):
        """ Get all subcategories of Liste (Kulturdenkmale in Deutschland) """
        return self.root_category.subcategories( recursive )


    def get_list_articles( self ):
        """ Return all the pages for all the categories"""
        return [article for cat in self.get_county_categories( ) for article in cat.articles( )]
