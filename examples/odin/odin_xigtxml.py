from collections import OrderedDict
from xigt.codecs import xigtxml

# etree is either from lxml.etree or xml.etree.ElementTree
etree = xigtxml.etree

class Meta(object):
    def __init__(self, type, attributes=None, content=None):
        self.type = type
        self.attributes = attributes or OrderedDict()
        self.content = content

def odin_decode_metadata(elem):
    if elem is None: return None
    if elem.get('type') != 'odin-meta':
        raise TypeError('Metadata must be of type odin-meta.')
    return xigtxml.Metadata(
        type=elem.get('type'),
        attributes=xigtxml.get_attributes(elem, ignore=('type',)),
        content=[decode_meta(meta) for meta in elem.iter('meta')]
    )

def decode_meta(elem):
    metatype = elem.get('type').lower()
    metaattrs = xigtxml.get_attributes(elem, ignore=('type',))
    if metatype == 'language':
        return Meta(type=metatype,
                    attributes=metaattrs)
    else:
        raise ValueError('Meta element was not a valid subtype.')

### Encoding ###

def odin_encode_metadata(metadata):
    if metadata.type != 'odin-meta':
        raise TypeError('Metadata must be of type odin-meta')
    attributes = metadata.attributes
    attributes['type'] = 'odin-meta'
    e = etree.Element('metadata', attrib=attributes)
    for meta in metadata.content:
        e.append(encode_meta(meta))
    return e

def encode_meta(meta):
    attributes = {'type': meta.type}
    attributes.update(meta.attributes)
    e = etree.Element('meta', attrib=attributes)
    return e

### Function maps ###

xigtxml.decode_metadata = odin_decode_metadata
xigtxml.encode_metadata = odin_encode_metadata

if __name__ == '__main__':
    import sys
    f = sys.argv[1]
    xc = xigtxml.load(open(f,'r'))
    print(xigtxml.dumps(xc, pretty_print=True))
    