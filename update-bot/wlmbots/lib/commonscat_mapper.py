# -*- coding: utf-8 -*-
import mwparserfromhell
import re


class CommonscatMapper(object):
    mapping = {
        u"Kategorie:Liste (Kulturdenkmale in Baden-Württemberg)": u"Category:Cultural heritage monuments in Baden-Württemberg",
        u"Kategorie:Liste (Baudenkmäler in Bayern)": u"Category:Cultural heritage monuments in Bavaria",
        u"Kategorie:Liste (Bodendenkmäler in Bayern)": u"Category:Cultural heritage monuments in Bavaria",
        u"Kategorie:Liste (Kulturdenkmäler in Berlin)": u"Category:Cultural heritage monuments in Berlin",
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
        u"Kategorie:Liste (Kulturdenkmale in Thüringen)": u"Category:Cultural heritage monuments in Thuringia",
        # Saxony has nested subcategories
        u"Kategorie:Liste (Kulturdenkmale in Bannewitz)": u"Category:Cultural heritage ensembles in Saxony",
        u"Kategorie:Liste (Kulturdenkmale in Bautzen)": u"Category:Cultural heritage ensembles in Saxony",
        u"Kategorie:Liste (Kulturdenkmale in Chemnitz)": u"Category:Cultural heritage ensembles in Saxony",
        u"Kategorie:Liste (Kulturdenkmale in Dresden)": u"Category:Cultural heritage ensembles in Saxony",
        u"Kategorie:Liste (Kulturdenkmale in Freiberg)": u"Category:Cultural heritage ensembles in Saxony",
        u"Kategorie:Liste (Kulturdenkmale in Freital)": u"Category:Cultural heritage ensembles in Saxony",
        u"Kategorie:Liste (Kulturdenkmale in Görlitz)": u"Category:Cultural heritage ensembles in Saxony",
        u"Kategorie:Liste (Kulturdenkmale in Leipzig)": u"Category:Cultural heritage ensembles in Saxony",
        u"Kategorie:Liste (Kulturdenkmale in Meißen)": u"Category:Cultural heritage ensembles in Saxony",
        u"Kategorie:Liste (Kulturdenkmale in Pirna)": u"Category:Cultural heritage ensembles in Saxony",
        u"Kategorie:Liste (Kulturdenkmale in Plauen)": u"Category:Cultural heritage ensembles in Saxony",
        u"Kategorie:Liste (Kulturdenkmale in Radebeul)": u"Category:Cultural heritage ensembles in Saxony",
        u"Kategorie:Liste (Kulturdenkmale in Zittau)": u"Category:Cultural heritage ensembles in Saxony",
    }


    def __init__(self):
        self.category_cache = {}


    def get_commonscat_from_category_links(self, text):
        """ Get the commonscat from the Category links (which is guaranteed to
            be on every page of the WLM pages)
        """
        code = mwparserfromhell.parse(text)
        for link in code.filter_wikilinks():
            title = unicode(link.title)
            if title in self.mapping:
                return self.mapping[title]


    def get_commonscat_from_weblinks_template(self, text):
        header_pos = re.search(r'=+\s+Weblinks', text, re.IGNORECASE)
        if not header_pos:
            return ""
        weblink_text = text[header_pos.start(0):]
        for template in mwparserfromhell.parse(weblink_text).filter_templates():
            if template.name.matches("Commonscat"):
                return u"Category:" + unicode(template.params[0])
        return ""


    def get_commonscat_from_table_row_template(self, template):
        """ Check mwparserfromhell template if it has a non-empty Commonscat parameter. """
        try:
            param = unicode(template.get("Commonscat")).strip()
            if param:
                _, commonscat = param.split("=", 1)
                return u"Category:" + commonscat.strip()
            else:
                return ""
        except ValueError as error:
            if str(error) == "Commonscat":
                return ""
            else:
                raise


    def get_commonscat(self, text, template):
        text_id = id(text)
        if text_id not in self.category_cache:
            self.category_cache[text_id] = [
                self.get_commonscat_from_weblinks_template(text),
                self.get_commonscat_from_category_links(text)
            ]
        category_candidates = [self.get_commonscat_from_table_row_template(template)] + self.category_cache[text_id]
        return next(category for category in category_candidates if category)  # return first non-empyt element
