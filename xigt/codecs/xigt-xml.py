
from .core import Xigt
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

def dump(fh, m, encoding='unicode', pretty_print=False):
    fh.write(dumps(m, encoding=encoding, pretty_print=pretty_print))

def dumps(m, encoding='unicode', pretty_print=False):
    return encode(m, encoding=encoding, pretty_print=pretty_print)

##############################################################################
##############################################################################
### Decoding

def decode_list(fh):
    """Decode """
    # element xigt-corpus { xigt* }
    # if memory becomes a big problem, consider catching start events,
    # get the root element (later start events can be ignored), and
    # root.clear() after decoding each xigt
    for event, elem in etree.iterparse(fh, events=('end')):
        yield decode_igt(elem)
        elem.clear()

def decode(fh):
    """Decode an igt XML element."""
    elem = etree.parse(fh)
    return decode_igt(elem)

def decode_igt(elem):
    # Igt = element igt { attribute id { Igt.id }, Igt.subtype }
    # Igt.subtype = attribute type { Igt.type }?, Igt.metadata, Igt.content
    # Igt.metadata = Metadata?
    # Igt.content = ( BasicTier | Tier )*
    elem = elem.find('.') # in case elem is an ElementTree rather than Element
    return Xigt(id=elem.get('id'),
                type=elem.get('type'),
                metadata=decode_metadata(elem.find('metadata')),
                tiers=[decode_tier(tier) for tier in elem.iter('tier')])

def decode_metadata(elem):
    # Metadata = element metadata { anything }
    # anything = attribute * { token }* & element * { anything }* & text
    # metadata elements can be redefined, but at this point just parse anything
    return elem

def decode_tier(elem):
    # 

##############################################################################
##############################################################################
### Encoding

def encode(m, encoding='unicode', pretty_print=False):
    attributes = {}
    if m.lnk is not None and m.lnk.type == Lnk.CHARSPAN:
        attributes['cfrom'] = str(m.lnk.data[0])
        attributes['cto'] = str(m.lnk.data[1])
    if m.surface is not None:
        attributes['surface'] = m.surface
    if m.identifier is not None:
        attributes['ident'] = m.identifier
    e = etree.Element('mrs', attrib=attributes)
    listed_vars = set()
    e.append(encode_label(m.ltop))
    e.append(encode_variable(m.index, listed_vars))
    for ep in m.rels:
        e.append(encode_ep(ep, listed_vars))
    for hcon in m.hcons:
        e.append(encode_hcon(hcon))
    if pretty_print:
        import re
        pprint_re = re.compile(r'(<ep\s|<fvpair>|<extrapair>|<hcons\s|</mrs>)',
                               re.IGNORECASE)
        string = etree.tostring(e, encoding=encoding)
        return pprint_re.sub(r'\n\1', string)
    return etree.tostring(e, encoding=encoding)

def encode_label(label):
    return etree.Element('label', vid=str(label.vid))

def encode_variable(v, listed_vars=set()):
    var = etree.Element('var', vid=str(v.vid), sort=v.sort)
    if v.vid not in listed_vars and v.properties:
        var.extend(encode_extrapair(key, val)
                   for key, val in v.properties.items())
        listed_vars.add(v.vid)
    return var
