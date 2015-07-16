import pywikibot

s = pywikibot.Site("de", "local")
p = pywikibot.Page(s, "Liste_der_Baudenkmale_in_Klein_Vielen")

print p.get()
