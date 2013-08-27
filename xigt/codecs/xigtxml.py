
from xigt.core import XigtCorpus, Igt, Tier, Item, Metadata
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
        ref=elem.get('ref'),
        type=elem.get('type'),
        attributes=get_attributes(elem, ignore=('id','ref','type')),
        metadata=decode_metadata(elem.find('metadata')),
        items=[decode_item(item) for item in elem.iter('item')]
    )

def default_decode_item(elem):
    return Item(
        id=elem.get('id'),
        ref=elem.get('ref'),
        type=elem.get('type'),
        attributes=get_attributes(elem, ignore=('id','ref','type')),
        content=elem.text
    )

def default_decode_metadata(elem):
    if elem is None: return None
    return Metadata(
        type=elem.get('type'),
        attributes=get_attributes(elem, ignore=('type',)),
        content=elem.text
    )

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
    if tier.ref is not None:
        attributes['ref'] = tier.ref
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
    if item.ref is not None:
        attributes['ref'] = item.ref
    e = etree.Element('item', attrib=attributes)
    if item.content is not None:
        e.text = item.content
    return e

def default_encode_metadata(metadata):
    attributes = metadata.attributes
    if metadata.type is not None:
        attributes['type'] = metadata.type
    e = etree.Element('metadata', attrib=attributes)
    e.text = metadata.content
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

encode            = default_encode
encode_xigtcorpus = default_encode_xigtcorpus
encode_igt        = default_encode_igt
encode_tier       = default_encode_tier
encode_item       = default_encode_item
encode_metadata   = default_encode_metadata
