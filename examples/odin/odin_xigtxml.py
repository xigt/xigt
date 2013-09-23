from collections import OrderedDict
from xigt.codecs import xigtxml

# etree is either from lxml.etree or xml.etree.ElementTree
etree = xigtxml.etree

### Decoding ###

### Encoding ###

### Function maps ###

if __name__ == '__main__':
    import sys
    from xigt.codecs import xigttxt
    f = sys.argv[1]
    xc = xigtxml.load(open(f,'r'))
    print(xigttxt.dumps(xc, pretty_print=True))
