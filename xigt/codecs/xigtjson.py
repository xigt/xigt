
import json

from xigt import XigtCorpus, Igt, Tier, Item, Metadata, Meta, MetaChild
from xigt.errors import XigtError

##############################################################################
##############################################################################
# Pickle-API methods


def load(fh, mode='full'):
    return decode(json.load(fh), mode=mode)


def loads(s):
    return decode(json.loads(s))


def dump(f, xc, encoding='utf-8', indent=2):
    if not isinstance(xc, XigtCorpus):
        raise XigtError(
            'Second argument of dump() must be an instance of XigtCorpus.'
        )
    json.dump(f, encode(xc), indent=indent)

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

def decode(obj, mode='full'):
    return XigtCorpus(
        id=obj.get('id'),
        attributes=obj.get('attributes', {}),
        metadata=[decode_metadata(md) for md in obj.get('metadata', [])],
        igts=[decode_igt(igt) for igt in obj.get('igts', [])],
        mode=mode,
        namespace=obj.get('namespace'),
        nsmap=obj.get('namespaces')
    )

def decode_igt(obj):
    igt = Igt(
        id=obj.get('id'),
        type=obj.get('type'),
        attributes=obj.get('attributes', {}),
        metadata=[decode_metadata(md) for md in obj.get('metadata', [])],
        tiers=[decode_tier(tier) for tier in obj.get('tiers', [])],
        namespace=obj.get('namespace'),
        nsmap=obj.get('namespaces')
    )
    return igt


def decode_tier(obj):
    tier = Tier(
        id=obj.get('id'),
        type=obj.get('type'),
        attributes=obj.get('attributes', {}),
        metadata=[decode_metadata(md) for md in obj.get('metadata', [])],
        items=[decode_item(item) for item in obj.get('items', [])],
        namespace=obj.get('namespace'),
        nsmap=obj.get('namespaces')
    )
    return tier


def decode_item(obj):
    item = Item(
        id=obj.get('id'),
        type=obj.get('type'),
        attributes=obj.get('attributes', {}),
        text=obj.get('text'),
        namespace=obj.get('namespace'),
        nsmap=obj.get('namespaces')
    )
    return item


def decode_metadata(obj):
    metadata = Metadata(
        id=obj.get('id'),
        type=obj.get('type'),
        attributes=obj.get('attributes', {}),
        metas=[decode_meta(meta) for meta in obj.get('metas', [])],
        namespace=obj.get('namespace'),
        nsmap=obj.get('namespaces')
    )
    return metadata


def decode_meta(obj):
    # a meta can simply have text, which is the easy case, or it can
    # have nested XML. In the latter case, store the XML in very basic
    # MetaChild objects
    meta = Meta(
        id=obj.get('id'),
        type=obj.get('type'),
        attributes=obj.get('attributes', {}),
        text=obj.get('text'),
        children=[decode_metachild(mc) for mc in obj.get('children', [])],
        namespace=obj.get('namespace'),
        nsmap=obj.get('namespaces')
    )
    return meta


def decode_metachild(obj):
    mc = MetaChild(
        obj['name'],
        attributes=obj.get('attributes', {}),
        text=obj.get('text'),
        children=[decode_metachild(mc) for mc in obj.get('children', [])],
        namespace=obj.get('namespace'),
        nsmap=obj.get('namespaces')
    )
    return mc

# Encoding #############################################################

def _make_obj(x):
    obj = {}
    if x.id: obj['id'] = x.id
    if x.type: obj['type'] = x.type
    if x.attributes: obj['attributes'] = x.attributes
    if x.namespace: obj['namespace'] = x.namespace
    if x.nsmap: obj['namespaces'] = x.nsmap
    return obj

def encode(xc):
    obj = _make_obj(xc)
    if xc.metadata:
        obj['metadata'] = [encode_metadata(md) for md in xc.metadata]
    obj['igts'] = [encode_igt(igt) for igt in xc.igts]
    return obj

def encode_metadata(md):
    obj = _make_obj(md)
    obj['metas'] = [encode_meta(m) for m in md.metas]
    return obj

def encode_meta(m):
    obj = _make_obj(m)
    if m.text is not None: obj['text'] = m.text
    if m.children:
        obj['children'] = [encode_metachild(mc) for mc in m.children]
    return obj

def encode_metachild(mc):
    obj = _make_obj(mc)
    obj['name'] = mc.name
    if mc.text is not None: obj['text'] = mc.text
    if mc.children:
        obj['children'] = [encode_metachild(mc) for mc in mc.children]
    return obj

def encode_igt(igt):
    obj = _make_obj(igt)
    if igt.metadata:
        obj['metadata'] = [encode_metadata(md) for md in igt.metadata]
    obj['tiers'] = [encode_tier(t) for t in igt.tiers]
    return obj

def encode_tier(tier):
    obj = _make_obj(tier)
    if tier.metadata:
        obj['metadata'] = [encode_metadata(md) for md in tier.metadata]
    obj['items'] = [encode_item(t) for t in tier.items]
    return obj

def encode_item(item):
    obj = _make_obj(item)
    if item.text: obj['text'] = item.text
    return obj
