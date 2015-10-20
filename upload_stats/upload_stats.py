# -*- coding: utf-8 -*-

# This script queries the API for image updates by the upload bot and generates a table
import mwclient
import datetime
from collections import Counter

site = mwclient.Site("de.wikipedia.org")

counts = Counter()
for uc in site.usercontributions('WLMUploadVorlageBot', namespace=0, prop="comment|title"):
    if not uc["comment"].startswith(u"Bot: Bild "):
        continue
    counts[uc["title"]] += 1

print u"Eingefügt\tSeite"
for page, updates in counts.most_common():
    print u"{}\t{}".format(updates, page)
