#!/usr/bin/python
import pywikibot


def main():
    site = pywikibot.Site("de", "local")
    page = pywikibot.Page(site, "Liste_der_Baudenkmale_in_Klein_Vielen")

    print page.get()
