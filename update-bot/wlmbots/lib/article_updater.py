"""
The class ArticleUpdater saves text to MediaWiki article if the new text is
different from the old one.

It also supports replacing text between comment markers only.
"""

import re

class ArticleUpdater(object):

    def __init__(self, article, begin_marker="WLMBOT: BEGIN UPDATE", end_marker="WLMBOT: END UPDATE"):
        self.article = article
        self.begin_marker = begin_marker
        self.end_marker = end_marker
        pattern = r"(<!--\s*{}\s*-->\s*)(.*)(<!--\s*{}\s*-->)".format(
            re.escape(begin_marker),
            re.escape(end_marker)
        )
        self.marker_pattern = re.compile(pattern, re.DOTALL)

    def save_text(self, text, summary=""):
        """ Save text if it has changed or the article does not exist. """
        if not self.article.exists():
            self.article.text = text
            self.article.save(summary=summary)
            return True
        article_text = self.article.get()
        pattern_match = self.marker_pattern.search(article_text)
        if pattern_match and pattern_match.group(2) != text:
            self.article.text = u"".join([
                article_text[0:pattern_match.end(1)],
                text,
                article_text[pattern_match.end(2):]
            ])
            self.article.save(summary=summary)
            return True
        elif not pattern_match and article_text != text:
            self.article.text = text
            self.article.save(summary=summary)
            return True
        else:
            return False
