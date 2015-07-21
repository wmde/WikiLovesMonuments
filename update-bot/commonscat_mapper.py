# -*- coding: utf-8 -*-
import mwparserfromhell

class CommonscatMapper(object):

    mapping = {
        u"Kategorie:Liste (Kulturdenkmale in Baden-Württemberg)": u"Cultural heritage monuments in Baden-Württemberg‏‎",
        u"Kategorie:Liste (Baudenkmäler in Bayern)": u"Category:Cultural heritage monuments in Bavaria",
        u"Kategorie:Liste (Bodendenkmäler in Bayern)": u"Category:Cultural heritage monuments in Bavaria",
        u"Kategorie:Liste (Kulturdenkmäler in Berlin)": u"Cultural heritage monuments in Berlin‏‎",
        u"Kategorie:Liste (Baudenkmale in Brandenburg)": u"Category:Cultural heritage monuments in Brandenburg",
        u"Kategorie:Liste (Bodendenkmale in Brandenburg)": u"Category:Cultural heritage monuments in Brandenburg",
        u"Kategorie:Liste (Kulturdenkmäler in der Freien Hansestadt Bremen)": u"Category:Cultural heritage monuments in Bremen",
        u"Kategorie:Liste (Kulturdenkmäler in Hamburg)": u"Category:Cultural heritage monuments in Hamburg",
        u"Kategorie:Liste (Kulturdenkmäler in Hessen)": u"Category:Cultural heritage monuments in Hesse",
        u"Kategorie:Liste (Baudenkmale in Mecklenburg-Vorpommern)": u"Category:Cultural heritage monuments in Mecklenburg-Vorpommern",
        u"Kategorie:Liste (Baudenkmale in Niedersachsen)": u"Category:Cultural heritage monuments in Lower Saxony",
        u"Kategorie:Liste (Baudenkmäler in Nordrhein-Westfalen)": u"Category:Cultural heritage monuments in North Rhine-Westphalia",
        u"Kategorie:Liste (Bodendenkmäler in Nordrhein-Westfalen)": u"Category:Cultural heritage monuments in North Rhine-Westphalia",
        u"Kategorie:Liste (Kulturdenkmäler in Rheinland-Pfalz)": u"Category:Cultural heritage monuments in Rhineland-Palatinate",
        u"Kategorie:Liste (Baudenkmäler im Saarland)": u"Category:Cultural heritage monuments in Saarland",
        u"Kategorie:Liste (Kulturdenkmale in Sachsen)": u"Category:Cultural heritage ensembles in Saxony",
        u"Kategorie:Liste (Kulturdenkmale in Sachsen-Anhalt)": u"Category:Cultural heritage monuments in Saxony-Anhalt",
        u"Kategorie:Liste (Kulturdenkmale in Schleswig-Holstein)": u"Category:Cultural heritage monuments in Schleswig-Holstein",
        u"Kategorie:Liste (Kulturdenkmale in Thüringen)": u"Category:Cultural heritage monuments in Thuringia"
    }

    def get_commonscat_from_links(self, text):
        code = mwparserfromhell.parse(text)
        for link in code.filter_wikilinks():
            title = unicode(link.title)
            if title in self.mapping:
                return self.mapping[title]
