from distutils.command.install_egg_info import safe_name
import bleach
from markdown import markdown


def format_markdown_as_safe_html(md_text):
    linker = bleach.linkifier.Linker()
    html = markdown(md_text)
    safe_html = linker.linkify(html)
    return safe_html
