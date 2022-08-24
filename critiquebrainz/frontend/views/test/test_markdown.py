from critiquebrainz.frontend.testing import FrontendTestCase

from critiquebrainz.frontend.views import markdown

class MarkdownTestCase(FrontendTestCase):

    def test_link_attrs(self):
        md = "This is [text with link](https://example.com) and more"
        html = markdown.format_markdown_as_safe_html(md)

        assert """<a href="https://example.com" rel="nofollow">""" in html

    def test_inline_link_attrs(self):
        md = "This is a url: https://example.net, and more"
        html = markdown.format_markdown_as_safe_html(md)

        assert """<a href="https://example.net" rel="nofollow">https://example.net</a>""" in html
