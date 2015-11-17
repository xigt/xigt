
from io import StringIO
from xml.etree.ElementTree import (
    tostring,
    iterparse,
    Element,
    ElementTree,
    QName
)
# this is not part of the public API, so be careful about importing it
try:
    from xml.etree.ElementTree import _namespace_map
except ImportError:
    # reduced set
     _namespace_map = {
         "http://www.w3.org/XML/1998/namespace": "xml",
         "http://www.w3.org/2001/XMLSchema": "xs",
         "http://www.w3.org/2001/XMLSchema-instance": "xsi",
         "http://purl.org/dc/elements/1.1/": "dc",
    }

# Python2 doesn't have 'unicode' as an encoding option, so fake it
# (inefficiently, but oh well)
try:
    tostring(Element('tag'), encoding='unicode')
    _tostring = tostring
except LookupError:
    def _tostring(elem, encoding='unicode', **kwargs):
        if encoding == 'unicode':
            return tostring(elem, encoding='utf-8', **kwargs).decode('utf-8')
        else:
            return tostring(elem, encoding=encoding, **kwargs)

# a little bit of mitigation for Python2/3 problems
# try:
#     basestring
# except NameError:
#     basestring = str
#     unicode = str
# else:
#     bytes = str


from xigt import XigtCorpus, Igt, Tier, Item, Metadata, Meta, MetaChild
from xigt.errors import XigtError


##############################################################################
##############################################################################
# Pickle-API methods


def load(fh, mode='full'):
    events = ns_iterparse(fh)
    return decode(events, mode=mode)


def loads(s):
    if hasattr(s, 'decode'): s = s.decode('utf-8')
    return load(StringIO(s))


def dump(f, xc, encoding='utf-8', indent=2):
    if not isinstance(xc, XigtCorpus):
        raise XigtError(
            'Second argument of dump() must be an instance of XigtCorpus.'
        )
    if hasattr(f, 'buffer') and encoding != 'unicode':
        f = f.buffer
    root = _build_corpus(xc)
    _indent(root, indent=indent)
    ElementTree(root).write(f, encoding=encoding)


def dumps(xc, encoding='unicode', indent=2):
    if not isinstance(xc, XigtCorpus):
        raise XigtError(
            'First argument of dumps() must be an instance of XigtCorpus.'
        )
    return encode_xigtcorpus(xc, encoding=encoding, indent=indent)


# XML Utilities#########################################################

class _QName(QName):
    def __init__(self, text_or_uri, tag=None, sortkey=None):
        QName.__init__(self, text_or_uri, tag=tag)
        self.sortkey = sortkey
    def __hash__(self):
        return QName.__hash__(self)
    def __lt__(self, other):
        sortkey = self.sortkey
        if isinstance(other, QName):
            other = other.text
        if sortkey is not None:
            return sortkey(self.text) < sortkey(other)
        return self.text < other
    def __le__(self, other):
        sortkey = self.sortkey
        if isinstance(other, QName):
            other = other.text
        if sortkey is not None:
            return sortkey(self.text) <= sortkey(other)
        return self.text <= other
    def __gt__(self, other):
        sortkey = self.sortkey
        if isinstance(other, QName):
            other = other.text
        if sortkey is not None:
            return sortkey(self.text) > sortkey(other)
        return self.text > other
    def __ge__(self, other):
        sortkey = self.sortkey
        if isinstance(other, QName):
            other = other.text
        if sortkey is not None:
            return sortkey(self.text) >= sortkey(other)
        return self.text >= other
    def __eq__(self, other):
        sortkey = self.sortkey
        if isinstance(other, QName):
            other = other.text
        if sortkey is not None:
            return sortkey(self.text) == sortkey(other)
        return self.text == other
    def __ne__(self, other):
        sortkey = self.sortkey
        if isinstance(other, QName):
            other = other.text
        if sortkey is not None:
            return sortkey(self.text) != sortkey(other)
        return self.text != other
    # for python2 support
    def __cmp__(self, other):
        sortkey = self.sortkey
        if isinstance(other, QName):
            other = other.text
        if sortkey is not None:
            self = sortkey(self.text)
            other = sortkey(other)
        if self < other:
            return -1
        elif self > other:
            return 1
        else:
            return 0


def _qname_split(qname):
    if isinstance(qname, QName):
        qname = str(qname)
    if qname.startswith('{'):
        return qname[1:].split('}', 1)
    else:
        return (None, qname)


class NSAttribDict(dict):
    def __init__(self, data, namespaces=None):
        dict.__init__(self, data)
        self.nsmap = dict(namespaces or [])


def xigt_attrsort(attr):
    return (
        not attr.startswith('xmlns:'),
        attr != 'id',
        attr != 'type',
        attr != 'alignment',
        attr != 'content',
        attr != 'segmentation',
        attr
    )

def ns_iterparse(fh, events=('start', 'end')):
    events = iter(
        iterparse(fh, events=['start-ns', 'end-ns'] + list(events))
    )
    # thanks: http://effbot.org/elementtree/iterparse.htm
    namespaces = []
    for event, elem in events:
        if event == 'start-ns':
            namespaces.append(elem)
        elif event == 'end-ns':
            namespaces.pop()
        elif event == 'start':
            elem.tag = _QName(elem.tag)
            elem.attrib = NSAttribDict(
                elem.attrib,
                # [(_QName(k, sortkey=xigt_attrsort), v)
                #   for k, v, in elem.attrib.items()],
                namespaces=namespaces
            )
            yield event, elem
        elif event == 'end':
            yield event, elem


# Decoding #############################################################

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
    items = [(k, v) for (k, v) in elem.items() if k not in ignore]
    return dict(items)


def default_decode_xigtcorpus(elem, igts=None, mode='full'):
    # xigt-corpus { attrs, metadata, content }
    # first get the attrs
    ns, tag = _qname_split(elem.tag)
    assert tag == 'xigt-corpus'
    return XigtCorpus(
        id=elem.get('id'),
        attributes=get_attributes(elem, ignore=('id',)),
        metadata=[decode_metadata(md) for md in elem.findall('metadata')],
        # NOTE: possible bug here; does nsiterparse run with elem.findall?
        igts=igts or [decode_igt(igt) for igt in elem.findall('igt')],
        mode=mode,
        namespace=ns,
        nsmap=elem.attrib.nsmap
    )


def default_decode_igt(elem):
    ns, tag = _qname_split(elem.tag)
    assert tag == 'igt'
    igt = Igt(
        id=elem.get('id'),
        type=elem.get('type'),
        attributes=get_attributes(elem, ignore=('id', 'type')),
        metadata=[decode_metadata(md) for md in elem.findall('metadata')],
        tiers=[decode_tier(tier) for tier in elem.findall('tier')],
        namespace=ns,
        nsmap=elem.attrib.nsmap
    )
    elem.clear()
    return igt


def default_decode_tier(elem):
    ns, tag = _qname_split(elem.tag)
    assert tag == 'tier'
    tier = Tier(
        id=elem.get('id'),
        type=elem.get('type'),
        attributes=get_attributes(elem, ignore=('id','type')),
        metadata=[decode_metadata(md) for md in elem.findall('metadata')],
        items=[decode_item(item) for item in elem.findall('item')],
        namespace=ns,
        nsmap=elem.attrib.nsmap
    )
    elem.clear()
    return tier


def default_decode_item(elem):
    ns, tag = _qname_split(elem.tag)
    assert tag == 'item'
    item = Item(
        id=elem.get('id'),
        type=elem.get('type'),
        attributes=get_attributes(elem, ignore=('id','type')),
        text=elem.text,
        namespace=ns,
        nsmap=elem.attrib.nsmap
    )
    elem.clear()
    return item


def default_decode_metadata(elem):
    if elem is None:
        return None
    ns, tag = _qname_split(elem.tag)
    assert tag == 'metadata'
    metadata = Metadata(
        id=elem.get('id'),
        type=elem.get('type'),
        attributes=get_attributes(elem, ignore=('id', 'type')),
        metas=[decode_meta(meta) for meta in elem.findall('meta')],
        namespace=ns,
        nsmap=elem.attrib.nsmap
    )
    elem.clear()
    return metadata


def default_decode_meta(elem):
    # a meta can simply have text, which is the easy case, or it can
    # have nested XML. In the latter case, store the XML in very basic
    # MetaChild objects
    ns, tag = _qname_split(elem.tag)
    assert tag == 'meta'
    text = elem.text or ''
    meta = Meta(
        id=elem.get('id'),
        type=elem.get('type'),
        attributes=get_attributes(elem, ignore=('id', 'type')),
        text=text if text.strip() else None,
        children=[decode_metachild(mc) for mc in elem],
        namespace=ns,
        nsmap=elem.attrib.nsmap
    )
    elem.clear()
    return meta


def default_decode_metachild(elem):
    ns, tag = _qname_split(elem.tag)
    text = elem.text or ''
    mc = MetaChild(
        tag,
        attributes=get_attributes(elem, ignore=('id', 'type')),
        text=text if text.strip() else None,
        children=[decode_metachild(mc) for mc in elem],
        namespace=ns,
        nsmap=elem.attrib.nsmap
    )
    elem.clear()
    return mc


##############################################################################
##############################################################################
# Encoding

# thanks: http://effbot.org/zone/element-namespaces.htm
def _build_elem(tag, obj, nscontext):
    ns = getattr(obj, 'namespace', None)
    revmap = dict((v, k) for k, v in getattr(obj, 'nsmap', {}).items())
    if revmap.get(ns) is not None:
        tag = '{}:{}'.format(revmap[ns], tag)
    e = Element(tag)
    # element attributes (including namespaces)
    if hasattr(obj, 'nsmap'):
        for pre, uri in obj.nsmap.items():
            if nscontext.get(pre) != uri:
                e.set(_QName('xmlns:%s' % pre, sortkey=xigt_attrsort), uri)
    if getattr(obj, 'id') is not None:
        e.set(_QName('id', sortkey=xigt_attrsort), obj.id)
    if getattr(obj, 'type') is not None:
        e.set(_QName('type', sortkey=xigt_attrsort), obj.type)
    if hasattr(obj, 'attributes'):
        for attr, val in obj.attributes.items():
            uri, attr = _qname_split(attr)
            if uri:
                # get the prefix from the nsmap,
                # backing off to the default set
                try:
                    pre = revmap[uri]
                except KeyError:
                    pre = _namespace_map[uri]
                attr = '{}:{}'.format(pre, attr)
            e.set(_QName(attr, sortkey=xigt_attrsort), val)
    return e


def _build_corpus(xc):
    e = _build_elem('xigt-corpus', xc, {})
    nsmap = xc.nsmap
    for md in xc.metadata:
        e.append(_build_metadata(md, nsmap))
    for igt in xc:
        e.append(_build_igt(igt, nsmap))
    return e


def _build_igt(igt, nscontext):
    e = _build_elem('igt', igt, nscontext)
    igt_nsmap = igt.nsmap
    for md in igt.metadata:
        e.append(_build_metadata(md, igt_nsmap))
    for tier in igt:
        e.append(_build_tier(tier, igt_nsmap))
    return e


def _build_tier(tier, nscontext):
    e = _build_elem('tier', tier, nscontext)
    tier_nsmap = tier.nsmap
    for md in tier.metadata:
        e.append(_build_metadata(md, tier_nsmap))
    for item in tier:
        e.append(_build_item(item, tier_nsmap))
    return e


def _build_item(item, nscontext):
    e = _build_elem('item', item, nscontext)
    e.text = item.text
    return e


def _build_metadata(md, nscontext):
    e = _build_elem('metadata', md, nscontext)
    nsmap = md.nsmap
    for meta in md:
        e.append(_build_meta(meta, nsmap))
    return e


def _build_meta(m, nscontext):
    e = _build_elem('meta', m, nscontext)
    e.text = m.text
    nsmap = m.nsmap
    for child in m:
        e.append(_build_metachild(child, nsmap))
    return e


def _build_metachild(mc, nscontext):
    e = _build_elem(mc.name, mc, nscontext)
    e.text = mc.text
    nsmap = mc.nsmap
    for child in mc:
        e.append(_build_metachild(child, nsmap))
    return e


# thanks: http://effbot.org/zone/element-lib.htm#prettyprint
def _indent(elem, indent=2, level=0):
    # don't even output newlines if indent is None (unlike indent=0)
    if indent is None:
        return
    i = "\n" + (indent * level * ' ')
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + (' ' * indent)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            _indent(elem, indent=indent, level=level+1)
        # this is now the last elem from the previous for-loop
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


# def _encode_str(s, encoding):
#     if encoding is None or encoding == 'unicode':
#         if isinstance(s, bytes):
#             return unicode(s)
#         return s
#     elif encoding:
#         return s.encode(encoding)
#     return s  # this can fail. is it encoded already or not?


# def _write_declaration(xf, encoding):
#     if encoding and encoding.lower() not in ('unicode', 'utf-8', 'us-ascii'):
#         xf.write('<?xml version="1.0" encoding="{}"?>\n'.format(encoding))


# def default_encode(xf, xc, encoding='unicode', indent=2):
#     _write_declaration(xf, encoding)
#     # write the root node manually
#     root = _build_elem('xigt-corpus', xc, {})  # just to format attrs
#     root_attrs = ['{}="{}"'.format(k, v) for k, v in root.items()]
#     open_tag = _encode_str(
#         '<{}{}>{}'.format(
#             root.tag,
#             '' if not root_attrs else ' ' + ' '.join(root_attrs),
#             '' if indent is None else '\n'),
#         encoding
#     )
#     xf.write(open_tag)

#     nsmap = xc.nsmap  # for context of lower elements
#     _ind = _encode_str(' ' * (indent or 0), encoding)  # for level-1 elements

#     # metadata
#     for md in xc.metadata:
#         md_elem = _build_metadata(md, nsmap)
#         # indenting out of context means the tail needs to be fixed
#         _indent(md_elem, indent=indent, level=1)
#         md_elem.tail = '' if indent is None else '\n'
#         xf.write(_ind + _tostring(md_elem, encoding=encoding))

#     for igt in xc:
#         igt_elem = _build_igt(igt, nsmap)
#         # indenting out of context means the tail needs to be fixed
#         _indent(igt_elem, indent=indent, level=1)
#         igt_elem.tail = '' if indent is None else '\n'
#         xf.write(_ind + _tostring(igt_elem, encoding=encoding))

#     closing_tag = _encode_str(
#         '</{}>{}'.format(root.tag, '' if indent is None else '\n'),
#         encoding
#     )
#     xf.write(closing_tag)


def default_encode_xigtcorpus(xc, encoding='unicode', indent=2):
    # this encodes the whole xigtcorpus at once.
    # for incremental encoding, see encode() (default_encode())
    root = _build_corpus(xc)
    _indent(root, indent=indent)
    return _tostring(root, encoding=encoding)


def default_encode_igt(igt, encoding='unicode', indent=2):
    elem = _build_igt(igt, {})
    _indent(elem, indent=indent)
    return _tostring(elem, encoding=encoding)


def default_encode_tier(tier, encoding='unicode', indent=2):
    elem = _build_tier(tier, {})
    _indent(elem, indent=indent)
    return _tostring(elem, encoding=encoding)


def default_encode_item(item, encoding='unicode', indent=2):
    elem = _build_item(item, {})
    _indent(elem, indent=indent)
    return _tostring(elem, encoding=encoding)


def default_encode_metadata(metadata, encoding='unicode', indent=2):
    elem = _build_metadata(metadata, {})
    _indent(elem, indent=indent)
    return _tostring(elem, encoding=encoding)


def default_encode_meta(meta, encoding='unicode', indent=2):
    elem = _build_meta(meta, {})
    _indent(elem, indent=indent)
    return _tostring(elem, encoding=encoding)


def default_encode_metachild(metachild, encoding='unicode', indent=2):
    elem = _build_metachild(metachild, {})
    _indent(elem, indent=indent)
    return _tostring(elem, encoding=encoding)


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
decode_metachild  = default_decode_metachild

#encode            = default_encode
encode_xigtcorpus = default_encode_xigtcorpus
encode_igt        = default_encode_igt
encode_tier       = default_encode_tier
encode_item       = default_encode_item
encode_metadata   = default_encode_metadata
encode_meta       = default_encode_meta
encode_metachild  = default_encode_metachild
