
import json

from xigt import XigtCorpus, Igt, Tier, Item, Metadata, Meta, MetaChild
from xigt.errors import XigtError

##############################################################################
##############################################################################
# Pickle-API methods


def load(fh, mode='full'):
    if hasattr(fh, 'read'):
        return decode(json.load(fh), mode=mode)
    else:
        with open(fh, 'r') as fh_:
            return decode(json.load(fh_), mode=mode)


def loads(s):
    return decode(json.loads(s))


def dump(f, xc, encoding='utf-8', indent=2):
    if not isinstance(xc, XigtCorpus):
        raise XigtError(
            'Second argument of dump() must be an instance of XigtCorpus.'
        )
    json.dump(encode(xc), f, indent=indent)

def dumps(xc, encoding='unicode', indent=2):
    if not isinstance(xc, XigtCorpus):
        raise XigtError(
            'First argument of dumps() must be an instance of XigtCorpus.'
        )
    return json.dumps(encode(xc), indent=indent)


# Helper Functions #####################################################

def ns_split(name):
    if ':' in name:
        return name.split(':', 1)
    else:
        return (None, name)


# Validation ###########################################################

def validate(f):
    pass  # no DTDs for JSON... make simple validator?

# Decoding #############################################################

def decode(obj, mode='full', nsmap=None):
    nsmap = active_namespaces(obj, nsmap)
    return XigtCorpus(
        id=obj.get('id'),
        attributes=obj.get('attributes', {}),
        metadata=[decode_metadata(md, nsmap)
                  for md in obj.get('metadata', [])],
        igts=[decode_igt(igt, nsmap)
              for igt in obj.get('igts', [])],
        mode=mode,
        namespace=obj.get('namespace'),
        nsmap=obj.get('namespaces')
    )

def decode_igt(obj, nsmap=None):
    nsmap = active_namespaces(obj, nsmap)
    igt = Igt(
        id=obj.get('id'),
        type=obj.get('type'),
        attributes=obj.get('attributes', {}),
        metadata=[decode_metadata(md, nsmap)
                  for md in obj.get('metadata', [])],
        tiers=[decode_tier(tier, nsmap)
               for tier in obj.get('tiers', [])],
        namespace=obj.get('namespace'),
        nsmap=obj.get('namespaces')
    )
    return igt


def decode_tier(obj, nsmap=None):
    nsmap = active_namespaces(obj, nsmap)
    tier = Tier(
        id=obj.get('id'),
        type=obj.get('type'),
        attributes=obj.get('attributes', {}),
        metadata=[decode_metadata(md, nsmap)
                  for md in obj.get('metadata', [])],
        items=[decode_item(item, nsmap)
               for item in obj.get('items', [])],
        namespace=obj.get('namespace'),
        nsmap=obj.get('namespaces')
    )
    return tier


def decode_item(obj, nsmap=None):
    nsmap = active_namespaces(obj, nsmap)
    item = Item(
        id=obj.get('id'),
        type=obj.get('type'),
        attributes=obj.get('attributes', {}),
        text=obj.get('text'),
        namespace=obj.get('namespace'),
        nsmap=obj.get('namespaces')
    )
    return item


def decode_metadata(obj, nsmap=None):
    nsmap = active_namespaces(obj, nsmap)
    metadata = Metadata(
        id=obj.get('id'),
        type=obj.get('type'),
        attributes=obj.get('attributes', {}),
        metas=[decode_meta(meta, nsmap)
               for meta in obj.get('metas', [])],
        namespace=obj.get('namespace'),
        nsmap=obj.get('namespaces')
    )
    return metadata


def decode_meta(obj, nsmap=None):
    nsmap = active_namespaces(obj, nsmap)
    # a meta can simply have text, which is the easy case, or it can
    # have nested XML. In the latter case, store the XML in very basic
    # MetaChild objects
    meta = Meta(
        id=obj.get('id'),
        type=obj.get('type'),
        attributes=obj.get('attributes', {}),
        text=obj.get('text'),
        children=[decode_metachild(mc, nsmap)
                  for mc in obj.get('children', [])],
        namespace=obj.get('namespace'),
        nsmap=obj.get('namespaces')
    )
    return meta


def decode_metachild(obj, nsmap=None):
    nsmap = active_namespaces(obj, nsmap)
    name = obj['name']
    if ':' in name:
        prefix, name = name.split(':', 1)
        namespace = nsmap.get(prefix, prefix)
    else:
        namespace = obj.get('namespace')  # possibly None
    mc = MetaChild(
        name,
        attributes=obj.get('attributes', {}),
        text=obj.get('text'),
        children=[decode_metachild(mc, nsmap)
                  for mc in obj.get('children', [])],
        namespace=namespace,
        nsmap=obj.get('namespaces')
    )
    return mc


def active_namespaces(obj, nsmap):
    nsmap = {} if nsmap is None else dict(nsmap)
    nsmap.update(obj.get('namespaces', {}))
    return nsmap


# Encoding #############################################################

inv_nsmap = {}

def _make_obj(x, nscontext=None):
    if nscontext is None: nscontext = {}
    active_nsmap = dict(nscontext)
    active_nsmap.update(x.nsmap)
    inv_nsmap.clear()
    inv_nsmap.update((uri, pre) for pre, uri in active_nsmap.items())
    nsmap = dict(set(active_nsmap.items()).difference(nscontext.items()))
    obj = {}
    if x.id: obj['id'] = x.id
    if x.type: obj['type'] = x.type
    # might need to re-add prefixes to namespaced attribute keys
    if x.attributes:
        attrs = {}
        for k, v in x.attributes.items():
            if k.startswith('{'):
                uri, key = k[1:].split('}', 1)
                try:
                    k = '{}:{}'.format(inv_nsmap[uri], key)
                except KeyError:
                    pass  # don't change key if no namespace mapping
            attrs[k] = v
        obj['attributes'] = attrs
    if x.namespace: obj['namespace'] = x.namespace
    if nsmap: obj['namespaces'] = nsmap
    return obj, active_nsmap

def encode(xc):
    obj, ns = _make_obj(xc)
    if xc.metadata:
        obj['metadata'] = [encode_metadata(md, ns) for md in xc.metadata]
    obj['igts'] = [encode_igt(igt, ns) for igt in xc.igts]
    return obj

def encode_metadata(md, nscontext=None):
    obj, ns = _make_obj(md, nscontext)
    obj['metas'] = [encode_meta(m, ns) for m in md.metas]
    return obj

def encode_meta(m, nscontext=None):
    obj, ns = _make_obj(m, nscontext)
    if m.text is not None: obj['text'] = m.text
    if m.children:
        obj['children'] = [encode_metachild(mc, ns) for mc in m.children]
    return obj

def encode_metachild(mc, nscontext=None):
    obj, ns = _make_obj(mc, nscontext)
    if obj.get('namespace') in inv_nsmap:
        obj['name'] = '{}:{}'.format(inv_nsmap[obj['namespace']], mc.name)
        del obj['namespace']
    else:
        obj['name'] = mc.name
    if mc.text is not None: obj['text'] = mc.text
    if mc.children:
        obj['children'] = [encode_metachild(mc, ns) for mc in mc.children]
    return obj

def encode_igt(igt, nscontext=None):
    obj, ns = _make_obj(igt, nscontext)
    if igt.metadata:
        obj['metadata'] = [encode_metadata(md, ns) for md in igt.metadata]
    obj['tiers'] = [encode_tier(t, ns) for t in igt.tiers]
    return obj

def encode_tier(tier, nscontext=None):
    obj, ns = _make_obj(tier, nscontext)
    if tier.metadata:
        obj['metadata'] = [encode_metadata(md, ns) for md in tier.metadata]
    obj['items'] = [encode_item(t, ns) for t in tier.items]
    return obj

def encode_item(item, nscontext=None):
    obj, ns = _make_obj(item, nscontext)
    if item.text: obj['text'] = item.text
    return obj

