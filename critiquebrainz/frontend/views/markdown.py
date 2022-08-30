from distutils.command.install_egg_info import safe_name
import bleach
from markdown import markdown


def bleach_cb_nofollow(attrs, new=False):
    """A callback to bleach's Linker which adds rel="nofollow noopener" to all
    links found in some text.
    Based on `bleach.callbacks.nofollow`
    """
    href_key = (None, "href")

    if href_key not in attrs:
        return attrs

    if attrs[href_key].startswith("mailto:"):
        return attrs

    rel_key = (None, "rel")
    rel_values = [val for val in attrs.get(rel_key, "").split(" ") if val]
    if "nofollow" not in [rel_val.lower() for rel_val in rel_values]:
        rel_values.append("nofollow")
    if "noopener" not in [rel_val.lower() for rel_val in rel_values]:
        rel_values.append("noopener")
    attrs[rel_key] = " ".join(rel_values)

    return attrs


def format_markdown_as_safe_html(md_text):
    linker = bleach.linkifier.Linker(callbacks=[bleach_cb_nofollow])
    html = markdown(md_text)
    safe_html = linker.linkify(html)
    return safe_html
