# -*- coding: utf-8 -*-
import html
import re


def encode_entities(string, quote=True):
    return html.escape(string, quote).encode('ascii', 'xmlcharrefreplace').decode('utf8')


def expand(string, args, tag='a', default_attribute='href'):

    def make_link(match):
        var = match.group(1)
        text = match.group(2)
        if text in args.keys():
            final_text = args[text]
        else:
            final_text = text

        if isinstance(args[var], dict):
            d = args[var]
        else:
            if default_attribute:
                d = {default_attribute: args[var]}
            else:
                d = {}
        attribs = ' '.join(["%s=\"%s\"" % (k, encode_entities(d[k])) for k
                            in sorted(d.keys())])
        if attribs:
            attribs = ' ' + attribs
        return '<%s%s>%s</%s>' % (tag, attribs, final_text, tag)

    def simple_expr(match):
        var = match.group(1)
        if var in args.keys():
            return args[var]
        return '{' + var + '}'

    r = '|'.join([re.escape(k) for k in args.keys()])

    r1 = re.compile('\{(' + r + ')\|(.*?)\}', re.UNICODE)
    r2 = re.compile('\{(' + r + ')\}', re.UNICODE)

    string = r1.sub(make_link, string)
    string = r2.sub(simple_expr, string)

    return string
