
from xigt import XigtCorpus, Igt, Tier, Item, Metadata, Meta
from collections import OrderedDict

# Import LXML if available, otherwise fall back to another etree implementation
try:
  from lxml import etree
except ImportError:
  import xml.etree.ElementTree as etree

##############################################################################
##############################################################################
### Pickle-API methods

def load(fh):
    elem = etree.parse(fh)
    return decode(elem)

def loads(s):
    elem = etree.fromstring(s)
    return decode(elem)

def dump(fh, xc, encoding='utf-8', pretty_print=False):
    # if encoding is 'unicode', dumps() will return a string, otherwise
    # a bytestring (which must be written to a buffer)
    outstring = dumps(xc, encoding=encoding, pretty_print=pretty_print)
    try:
        fh.write(outstring)
    except TypeError:
        fh.buffer.write(outstring)

def dumps(xc, encoding='unicode', pretty_print=False):
    e = encode(xc)
    xmldecl = encoding != 'unicode'
    try:
        return etree.tostring(e, encoding=encoding,
                              xml_declaration=xmldecl,
                              pretty_print=pretty_print)
    except TypeError:
        return etree.tostring(e, encoding=encoding,
                              xml_declaration=xmldecl)

##############################################################################
##############################################################################
### Decoding

def default_decode(elem):
    """Decode a XigtCorpus element."""
    return decode_xigtcorpus(elem.find('.'))

def default_get_attributes(elem, ignore=None):
    if ignore is None: ignore = tuple()
    return OrderedDict((k,v) for (k,v) in elem.items() if k not in ignore)

def default_decode_xigtcorpus(elem):
    # xigt-corpus { attrs, metadata, content }
    return XigtCorpus(
        id=elem.get('id'),
        attributes=get_attributes(elem, ignore=('id',)),
        metadata=decode_metadata(elem.find('metadata')),
        igts=[decode_igt(igt) for igt in elem.iter('igt')]
    )

def default_decode_igt(elem):
    return Igt(
        id=elem.get('id'),
        type=elem.get('type'),
        attributes=get_attributes(elem, ignore=('id','type')),
        metadata=decode_metadata(elem.find('metadata')),
        tiers=[decode_tier(tier) for tier in elem.iter('tier')]
    )

def default_decode_tier(elem):
    return Tier(
        id=elem.get('id'),
        type=elem.get('type'),
        attributes=get_attributes(elem, ignore=('id','type')),
        metadata=decode_metadata(elem.find('metadata')),
        items=[decode_item(item) for item in elem.iter('item')]
    )

def default_decode_item(elem):
    return Item(
        id=elem.get('id'),
        type=elem.get('type'),
        attributes=get_attributes(elem, ignore=('id','type')),
        content=elem.text
    )

def default_decode_metadata(elem):
    if elem is None: return None
    # no metadata type... just treat contents as text
    if elem.get('type') is None:
        return Metadata(
            type=elem.get('type'),
            attributes=get_attributes(elem, ignore=('type',)),
            content=elem.text
        )
    # basic metadata subtype allowed by default schema
    elif elem.get('type') == 'xigt-meta':
        return Metadata(
            type=elem.get('type'),
            attributes=get_attributes(elem, ignore=('type',)),
            content=[decode_meta(meta) for meta in elem.iter('meta')]
        )
    else:
        raise TypeError('Invalid subtype of Metadata: {}'
                        .format(elem.get('type')))

def default_decode_meta(elem):
    metatype = elem.get('type').lower()
    metaattrs = get_attributes(elem, ignore=('type',))
    # language is easy---just attributes
    if metatype == 'language':
        return Meta(type=metatype,
                    attributes=metaattrs)
    # and the following have basic content
    elif metatype in ('date', 'author', 'comment'):
        return Meta(type=metatype,
                    attributes=metaattrs,
                    content=elem.text)
    # source has two alternatives
    elif metatype == 'source' and elem.get('id') is not None:
        return Meta(type=metatype,
                    attributes=metaattrs,
                    content=elem.text)
    elif metatype == 'source' and elem.get('ref') is not None:
        return Meta(type=metatype,
                    attributes=metaattrs)
    else:
        raise ValueError('Invalid subtype of Meta: {}'
                         .format(metatype))

##############################################################################
##############################################################################
### Encoding

def default_encode(xc):
    return encode_xigtcorpus(xc)

def default_encode_xigtcorpus(xc):
    attributes = xc.attributes
    if xc.id is not None:
        attributes['id'] = xc.id
    e = etree.Element('xigt-corpus', attrib=attributes)
    if xc.metadata is not None:
        e.append(encode_metadata(xc.metadata))
    for igt in xc.igts:
        e.append(encode_igt(igt))
    return e

def default_encode_igt(igt):
    attributes = igt.attributes
    if igt.id is not None:
        attributes['id'] = igt.id
    e = etree.Element('igt', attrib=attributes)
    if igt.metadata is not None:
        e.append(encode_metadata(igt.metadata))
    for tier in igt.tiers:
        e.append(encode_tier(tier))
    return e

def default_encode_tier(tier):
    attributes = tier.attributes
    if tier.type is not None:
        attributes['type'] = tier.type
    if tier.id is not None:
        attributes['id'] = tier.id
    e = etree.Element('tier', attrib=attributes)
    if tier.metadata is not None:
        e.append(encode_metadata(tier.metadata))
    for item in tier.items:
        e.append(encode_item(item))
    return e

def default_encode_item(item):
    attributes = item.attributes
    if item.id is not None:
        attributes['id'] = item.id
    e = etree.Element('item', attrib=attributes)
    if item.content is not None:
        e.text = item.content
    return e

def default_encode_metadata(metadata):
    attributes = metadata.attributes
    if metadata.type is None:
        e = etree.Element('metadata', attrib=attributes)
        e.text = metadata.content
        return e
    elif metadata.type == 'xigt-meta':
        attributes['type'] = metadata.type
        e = etree.Element('metadata', attrib=attributes)
        for meta in metadata.content:
            e.append(encode_meta(meta))
        return e
    else:
        raise ValueError('Invalid subtype of Metadata: {}'
                         .format(metadata.type))

def default_encode_meta(meta):
    if meta.type.lower() not in ('language', 'date', 'author', 'source',
                                 'comment'):
        raise ValueError('Invalid subtype of Meta: {}'
                         .format(meta.type))
    attributes = OrderedDict(type=meta.type, **meta.attributes)
    e = etree.Element('meta', attrib=attributes)
    e.text = meta.content
    return e

##############################################################################
### Default function mappings

decode            = default_decode
get_attributes    = default_get_attributes
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
