
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
    return decode(fh)

def loads(s):
    return decode_string(s)

def dump(fh, xc, encoding='unicode', pretty_print=False):
    fh.write(dumps(xc, encoding=encoding, pretty_print=pretty_print))

def dumps(xc, encoding='unicode', pretty_print=False):
    return encode(xc, encoding=encoding, pretty_print=pretty_print)

##############################################################################
##############################################################################
### Decoding

#def decode_list(fh):
#    """Decode """
#    # element xigt-corpus { xigt* }
#    # if memory becomes a big problem, consider catching start events,
#    # get the root element (later start events can be ignored), and
#    # root.clear() after decoding each xigt
#    for event, elem in etree.iterparse(fh, events=('end')):
#        yield decode_igt(elem)
#        elem.clear()
#
#def decode(fh):
#    """Decode an igt XML element."""
#    elem = etree.parse(fh)
#    return decode_igt(elem)
#
#def decode_igt(elem):
#    # Igt = element igt { attribute id { Igt.id }, Igt.subtype }
#    # Igt.subtype = attribute type { Igt.type }?, Igt.metadata, Igt.content
#    # Igt.metadata = Metadata?
#    # Igt.content = ( BasicTier | Tier )*
#    elem = elem.find('.') # in case elem is an ElementTree rather than Element
#    return Xigt(id=elem.get('id'),
#                type=elem.get('type'),
#                metadata=decode_metadata(elem.find('metadata')),
#                tiers=[decode_tier(tier) for tier in elem.iter('tier')])
#
#def decode_metadata(elem):
#    # Metadata = element metadata { anything }
#    # anything = attribute * { token }* & element * { anything }* & text
#    # metadata elements can be redefined, but at this point just parse anything
#    return elem
#
#def decode_tier(elem):
#    #
#    pass

##############################################################################
##############################################################################
### Encoding

def encode(xc, encoding='unicode', pretty_print=False):
    attributes = xc.attributes
    if xc.id is not None:
        attributes['id'] = xc.id
    e = etree.Element('xigt-corpus', attrib=attributes)
    if xc.metadata is not None:
        e.append(encode_metadata(xc.metadata))
    for igt in xc.igts:
        e.append(encode_igt(igt))
    try:
        xmlstring = etree.tostring(e, encoding=encoding,
                                   pretty_print=pretty_print)
    except TypeError:
        xmlstring = etree.tostring(e, encoding=encoding)
    return xmlstring

def encode_igt(igt):
    attributes = igt.attributes
    if igt.id is not None:
        attributes['id'] = igt.id
    e = etree.Element('igt', attrib=attributes)
    if igt.metadata is not None:
        e.append(encode_metadata(igt.metadata))
    for tier in igt.tiers:
        e.append(encode_tier(tier))
    return e

def encode_tier(tier):
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

def encode_item(item):
    attributes = item.attributes
    if item.id is not None:
        attributes['id'] = item.id
    if item.ref is not None:
        attributes['ref'] = item.ref
    e = etree.Element('item', attrib=attributes)
    if item.content is not None:
        e.text = item.content
    return e

def encode_metadata(metadata):
    attributes = metadata.attributes
    if metadata.type is not None:
        attributes['type'] = metadata.type
    e = etree.Element('metadata', attrib=attributes)
    e.text = metadata.content
    return e
