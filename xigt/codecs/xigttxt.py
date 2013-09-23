
from xigt.core import XigtCorpus, Igt, Tier, Item, Metadata
from collections import OrderedDict

##############################################################################
##############################################################################
### Pickle-API methods

#def load(fh):
#    return decode(fh)
#
#def loads(s):
#    return decode(s)

def dump(fh, xc, encoding='utf-8', pretty_print=False):
    # if encoding is 'unicode', dumps() will return a string, otherwise
    # a bytestring (which must be written to a buffer)
    outstring = dumps(xc, encoding=encoding, pretty_print=pretty_print)
    try:
        fh.write(outstring)
    except TypeError:
        fh.buffer.write(outstring)

def dumps(xc, encoding='unicode', pretty_print=False):
    s = encode(xc)
    return s

##############################################################################
##############################################################################
### Decoding

def default_decode(s):
    """Decode a XigtCorpus element."""
    return decode_xigtcorpus(s)

def default_get_attributes(s, ignore=None):
    # attributes are not encoded in txt
    return OrderedDict()

def default_decode_xigtcorpus(s):
    # xigt-corpus { attrs, metadata, content }
    return XigtCorpus(
        #id=elem.get('id'),
        #attributes=get_attributes(elem, ignore=('id',)),
        #metadata=decode_metadata(elem.find('metadata')),
        #igts=[decode_igt(igt) for igt in elem.iter('igt')]
    )

def default_decode_igt(s):
    return Igt(
        #id=elem.get('id'),
        #type=elem.get('type'),
        #attributes=get_attributes(elem, ignore=('id','type')),
        #metadata=decode_metadata(elem.find('metadata')),
        #tiers=[decode_tier(tier) for tier in elem.iter('tier')]
    )

def default_decode_tier(s):
    return Tier(
        #id=elem.get('id'),
        #ref=elem.get('ref'),
        #type=elem.get('type'),
        #attributes=get_attributes(elem, ignore=('id','ref','type')),
        #metadata=decode_metadata(elem.find('metadata')),
        #items=[decode_item(item) for item in elem.iter('item')]
    )

def default_decode_item(s):
    return Item(
        #id=elem.get('id'),
        #ref=elem.get('ref'),
        #type=elem.get('type'),
        #attributes=get_attributes(elem, ignore=('id','ref','type')),
        #content=elem.text
    )

def default_decode_metadata(s):
    return Metadata(
        #type=elem.get('type'),
        #attributes=get_attributes(elem, ignore=('type',)),
        #content=elem.text
    )

##############################################################################
##############################################################################
### Encoding

def default_encode(xc):
    return encode_xigtcorpus(xc)

def default_encode_xigtcorpus(xc):
    #attributes = xc.attributes
    #if xc.id is not None:
    #    attributes['id'] = xc.id
    #if xc.metadata is not None:
    #    e.append(encode_metadata(xc.metadata))
    return '\n'.join(encode_igt(igt) for igt in xc.igts)

def default_encode_igt(igt):
    #attributes = igt.attributes
    #if igt.id is not None:
    #    attributes['id'] = igt.id
    #if igt.metadata is not None:
    #    e.append(encode_metadata(igt.metadata))
    return '\n'.join(encode_tier(tier) for tier in igt.tiers)

def default_encode_tier(tier, ignore=None):
    tiertype = tier.type.lower()
    if ignore and tiertype in ignore: return
    #attributes = tier.attributes
    #if tier.type is not None:
    #    attributes['type'] = tier.type
    #if tier.id is not None:
    #    attributes['id'] = tier.id
    #if tier.ref is not None:
    #    attributes['ref'] = tier.ref
    #if tier.metadata is not None:
    #    e.append(encode_metadata(tier.metadata))
    delim = ' '
    if tiertype in ('phrases', 'translations'):
        delim = '\n'
    elif tiertype in ('morphemes', 'glosses'):
        # this is not sufficient, because it joins all morphs with - and not
        # just those aligned to a word
        delim = '-'
    return delim.join(encode_item(item) for item in tier.items)

def default_encode_item(item):
    return item.content

def default_encode_metadata(metadata):
    #attributes = metadata.attributes
    #if metadata.type is not None:
    #    attributes['type'] = metadata.type
    #e.text = metadata.content
    return None

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

