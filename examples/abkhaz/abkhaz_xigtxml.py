
from collections import OrderedDict
from xigt.codecs import xigtxml

# etree is either from lxml.etree or xml.etree.ElementTree
etree = xigtxml.etree

### Decoding ###

def matrix_decode_meta(elem):
    metatype = elem.get('type').lower()
    if metatype in ('judgment', 'vetted', 'phenomena'):
        metaattrs = xigtxml.get_attributes(elem, ignore=('type',))
        content = None
        if metatype == 'phenomena':
            content = [p.text for p in elem.iter('phenomenon')]
        return xigtxml.Meta(type=metatype,
                            attributes=metaattrs,
                            content=content)
    else:
        return xigtxml.default_decode_meta(elem)

### Encoding ###

def encode_meta(meta):
    metatype = meta.type.lower()
    if metatype in ('judgment', 'vetted', 'phenomena'):
        attributes = dict(type=meta.type, **meta.attributes)
        e = etree.Element('meta', attrib=attributes)
        if metatype == 'phenomena':
            for phenomenon in meta.content:
                p = etree.Element('phenomenon')
                p.text = phenomenon
                e.append(p)
        return e
    else:
        return xigtxml.default_encode_meta(meta)

### Function maps ###

xigtxml.decode_meta = matrix_decode_meta
xigtxml.encode_meta = matrix_encode_meta

if __name__ == '__main__':
    import sys
    f = sys.argv[1]
    xc = xigtxml.load(open(f,'r'))
    print(xigtxml.dumps(xc, pretty_print=True))
    xigtxml.dump(open('abkhaz-out.xigt','w'), xc, pretty_print=True)
