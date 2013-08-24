
from collections import OrderedDict
from xigt.codecs import xigtxml

# etree is either from lxml.etree or xml.etree.ElementTree
etree = xigtxml.etree

class Meta(object):
    def __init__(self, type, attributes=None, content=None):
        self.type = type
        self.attributes = attributes or OrderedDict()
        self.content = content

### Decoding ###

def matrix_decode_metadata(elem):
    if elem is None: return None
    if elem.get('type') != 'matrix-meta':
        raise TypeError('Metadata must be of type matrix-meta.')
    return xigtxml.Metadata(
        type=elem.get('type'),
        attributes=xigtxml.get_attributes(elem, ignore=('type',)),
        content=[decode_meta(meta) for meta in elem.iter('meta')]
    )

def decode_meta(elem):
    metatype = elem.get('type').lower()
    metaattrs = xigtxml.get_attributes(elem, ignore=('type',))
    # the following subtypes are easy---just attributes
    if metatype in ('language', 'vetted', 'judgment'):
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
    elif metatype == 'phenomena':
        return Meta(type=metatype,
                    attributes=metaattrs,
                    content=[p.text for p in elem.iter('phenomenon')])
    else:
        raise ValueError('Meta element was not a valid subtype.')

### Encoding ###

def matrix_encode_metadata(metadata):
    if metadata.type != 'matrix-meta':
        raise TypeError('Metadata must be of type matrix-meta')
    attributes = metadata.attributes
    attributes['type'] = 'matrix-meta'
    e = etree.Element('metadata', attrib=attributes)
    for meta in metadata.content:
        e.append(encode_meta(meta))
    return e

def encode_meta(meta):
    attributes = {'type': meta.type}
    attributes.update(meta.attributes)
    e = etree.Element('meta', attrib=attributes)
    if meta.type.lower() in ('date', 'author', 'source', 'comment'):
        e.text = meta.content
    elif meta.type.lower() == 'phenomena':
        for phenomenon in meta.content:
            p = etree.Element('phenomenon')
            p.text = phenomenon
            e.append(p)
    return e

### Function maps ###

xigtxml.decode_metadata = matrix_decode_metadata
xigtxml.encode_metadata = matrix_encode_metadata

if __name__ == '__main__':
    import sys
    f = sys.argv[1]
    xc = xigtxml.load(open(f,'r'))
    print(xigtxml.dumps(xc, pretty_print=True))
