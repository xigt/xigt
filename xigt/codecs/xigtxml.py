
from xigt import XigtCorpus, Igt, Tier, Item, Metadata, Meta
from collections import OrderedDict
from itertools import chain
import logging
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape, quoteattr

##############################################################################
##############################################################################
# Pickle-API methods


def load(fh, mode='full'):
    events = iter(ET.iterparse(fh, events=('start', 'end')))
    return decode(events, mode=mode)


def loads(s):
    elem = ET.fromstring(s)
    return decode_xigtcorpus(elem.find('.'))


def dump(fh, xc, encoding='utf-8', indent=2):
    # if encoding is 'unicode', dumps() will return a string, otherwise
    # a bytestring (which must be written to a buffer)
    strings = encode(xc, encoding=encoding, indent=indent)
    if indent:
        strings = chain(strings, ['\n'])
    for s in strings:
        try:
            fh.write(s)
        except TypeError:
            fh.buffer.write(s)


def dumps(xc, encoding='unicode', indent=2):
    if encoding != 'unicode':
        return b''.join(encode(xc, encoding=encoding, indent=indent))
    else:
        return ''.join(encode(xc, encoding=encoding, indent=indent))


##############################################################################
##############################################################################
# Decoding

def validate_event(event, elem, expected=None):
    if expected is None:
        expected = []
    given = ('<{}>' if event == 'start' else '</{}>').format(elem.tag)
    if (event, elem) not in expected:
        expected = ' | '.join(('<{}>' if e == 'start' else '</{}>').format(t)
                              for e, t in expected)
        raise Exception('Unexpected tag: {} (expected: {})'
                        .format(given, expected))


def iter_elements(tag, events, root, break_on=None):
    if break_on is None:
        break_on = []
    event, elem = next(events)
    while (event, elem.tag) not in break_on:
        if event == 'end' and elem.tag == tag:
            yield elem
            root.clear()  # free memory after we're done with an element
        event, elem = next(events)


def default_decode(events, mode='full'):
    """Decode a XigtCorpus element."""
    event, elem = next(events)
    root = elem  # store root for later instantiation
    while (event, elem.tag) not in [('start', 'igt'), ('end', 'xigt-corpus')]:
        event, elem = next(events)
    igts = None
    if event == 'start' and elem.tag == 'igt':
        igts = (
            decode_igt(e)
            for e in iter_elements(
                'igt', events, root, break_on=[('end', 'xigt-corpus')]
            )
        )
    xc = decode_xigtcorpus(root, igts=igts, mode=mode)
    return xc


def default_get_attributes(elem, ignore=None):
    if ignore is None:
        ignore = tuple()
    return OrderedDict((k, v) for (k, v) in elem.items() if k not in ignore)


def default_decode_xigtcorpus(elem, igts=None, mode='full'):
    # xigt-corpus { attrs, metadata, content }
    # first get the attrs
    return XigtCorpus(
        id=elem.get('id'),
        attributes=get_attributes(elem, ignore=('id',)),
        metadata=[decode_metadata(md) for md in elem.findall('metadata')],
        igts=igts or [decode_igt(igt) for igt in elem.findall('igt')],
        mode=mode
    )


def default_decode_igt(elem):
    igt = Igt(
        id=elem.get('id'),
        type=elem.get('type'),
        attributes=get_attributes(elem, ignore=('id', 'type')),
        metadata=[decode_metadata(md) for md in elem.findall('metadata')],
        tiers=[decode_tier(tier) for tier in elem.findall('tier')]
    )
    elem.clear()
    return igt


def default_decode_tier(elem):
    tier = Tier(
        id=elem.get('id'),
        type=elem.get('type'),
        attributes=get_attributes(elem, ignore=('id','type')),
        metadata=[decode_metadata(md) for md in elem.findall('metadata')],
        items=[decode_item(item) for item in elem.findall('item')]
    )
    elem.clear()
    return tier


def default_decode_item(elem):
    item = Item(
        id=elem.get('id'),
        type=elem.get('type'),
        attributes=get_attributes(elem, ignore=('id','type')),
        text=elem.text
    )
    elem.clear()
    return item


def default_decode_metadata(elem):
    if elem is None:
        return None
    metadata = Metadata(
        id=elem.get('id'),
        type=elem.get('type'),
        attributes=get_attributes(elem, ignore=('id', 'type')),
        metas=[decode_meta(meta) for meta in elem.findall('meta')]
    )
    elem.clear()
    return metadata


def default_decode_meta(elem):
    # a meta can simply have text, which is the easy case, or it can
    # have nested XML. In the latter case, we don't know what the nested
    # XML will look like, so just reserialize it and store it as text.

    # python3 needs encoding='unicode' to get a native string, but for
    # python2 this gives a LookupError
    try:
        children = [ET.tostring(e, encoding='unicode') for e in elem]
    except LookupError:
        children = [ET.tostring(e) for e in elem]
    meta = Meta(
        id=elem.get('id'),
        type=elem.get('type'),
        attributes=get_attributes(elem, ignore=('id', 'type')),
        text=elem.text,
        children=children
    )
    elem.clear()
    return meta


##############################################################################
##############################################################################
# Encoding

def encode_attributes(obj, attrs):
    attributes = OrderedDict()
    for attr in attrs:
        if hasattr(obj, attr) and getattr(obj, attr) is not None:
            attributes[attr] = getattr(obj, attr)
    if hasattr(obj, 'attributes') and getattr(obj, 'attributes') is not None:
        attributes.update(obj.attributes)
    return ''.join(' {}={}'.format(k, quoteattr(v))
                   for k, v in attributes.items())


def default_encode(xc, encoding='unicode', indent=2):
    if encoding != 'unicode':
        enc = lambda s: s.encode(encoding)
        yield enc('<?xml version="1.0" encoding="{}"?>{}'
                  .format(encoding.upper(), '\n' if indent else ''))
    else:
        enc = lambda s: s
    for s in encode_xigtcorpus(xc, indent=indent):
        yield enc(s)


def default_encode_xigtcorpus(xc, indent=2):
    attrs = encode_attributes(xc, ['id'])
    yield '<xigt-corpus{}>{}'.format(attrs, '\n' if indent else '')
    for metadata in xc.metadata:
        yield encode_metadata(metadata, indent=indent, level=1)
        if indent:
            yield '\n'
    for igt in xc:
        yield encode_igt(igt, indent=indent)
        if indent:
            yield '\n'

    yield '</xigt-corpus>'


def default_encode_igt(igt, indent=2):
    attrs = encode_attributes(igt, ['id', 'type'])
    # indent - 2 so at indent 2 (compact, but readable), we aren't
    # wasting 2 extra spaces on nearly every line in the corpus. If
    # someone uses indent > 2, we assume they aren't concerned about
    # disk space, so give them the indent.
    lines = ['{}<igt{}>'.format(' ' * (indent - 2), attrs)]
    for metadata in igt.metadata:
        lines.append(encode_metadata(metadata, indent=indent, level=2))
    for tier in igt.tiers:
        lines.append(encode_tier(tier, indent=indent))
    lines.append('{}</igt>'.format(' ' * (indent - 2)))
    return ('\n' if indent else '').join(lines)


def default_encode_tier(tier, indent=2):
    attrs = encode_attributes(tier, ['id', 'type'])
    lines = ['{}<tier{}>'.format(' ' * indent, attrs)]
    lines.extend(
        encode_metadata(metadata, indent=indent, level=3)
        for metadata in tier.metadata
    )
    lines.extend(
        encode_item(item, indent=indent) for item in tier.items
    )
    lines.append('{}</tier>'.format(' ' * indent))
    return ('\n' if indent else '').join(lines)


def default_encode_item(item, indent=2):
    attrs = encode_attributes(item, ['id', 'type'])
    cnt = item.text
    s = '{}<item{}{}>'.format(
        ' ' * indent * 2,
        attrs,
        '/' if cnt is None else '>{}</item'.format(escape(cnt))
    )
    return s


def default_encode_metadata(metadata, indent=2, level=0):
    attrs = encode_attributes(metadata, ['id', 'type'])
    indent_space = ' ' * ((level * indent) - 2)
    lines = ['{}<metadata{}>'.format(indent_space, attrs)]
    lines.extend(
        encode_meta(meta, indent=indent, level=(level + 1))
        for meta in metadata.metas
    )
    lines.append('{}</metadata>'.format(indent_space))
    return ('\n' if indent else '').join(lines)


def default_encode_meta(meta, indent=2, level=1):
    #if meta.type.lower() not in ('language', 'date', 'author', 'source',
    #                             'comment'):
    #    raise ValueError('Invalid subtype of Meta: {}'
    #                     .format(meta.type))
    attrs = encode_attributes(meta, ['id', 'type'])
    cnt = ''.join([escape(meta.text)] + meta.children)
    s = '{}<meta{}{}>'.format(
        ' ' * ((level * indent) - 2),
        attrs,
        '/' if cnt is None else '>{}</meta>'.format(cnt)
    )
    return s


##############################################################################
# Default function mappings

get_attributes    = default_get_attributes
decode            = default_decode
decode_xigtcorpus = default_decode_xigtcorpus
decode_igt        = default_decode_igt
decode_tier       = default_decode_tier
decode_item       = default_decode_item
decode_metadata   = default_decode_metadata
decode_meta       = default_decode_meta

encode            = default_encode
encode_xigtcorpus = default_encode_xigtcorpus
encode_igt        = default_encode_igt
encode_tier       = default_encode_tier
encode_item       = default_encode_item
encode_metadata   = default_encode_metadata
encode_meta       = default_encode_meta
