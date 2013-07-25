from xigt.core import XigtCorpus, Igt, Tier, Item, Metadata
from xigt.codecs import xigtxml

xc = XigtCorpus(
  id="xc1",
  metadata=Metadata(content="<author>me</author>"),
  igts=[Igt(id='igt1',
            attributes={'judgment':'g'},
            tiers=[Tier(type='sentences', id='s',
                        items=[Item(id='s1',
                                    content='a sentence.')]),
                   Tier(type='words', id='w', ref='s',
                        items=[Item(id='w1',ref='s1[0:1]'),
                               Item(id='w2',ref='s1[2:10]'),
                               Item(id='w3',ref='s1[10:11]')])])]
)
# get items using ids as keys:
print('xc1:igt1:w:w1: {}'
      .format(xc['igt1']['w'].get('w1').resolve_ref()))
# numerical indices also work (0-indexed):
print('xc1:igt1:w:w2: {}'
      .format(xc[0][1][1].resolve_ref()))
# or indices on list members:
print('xc1:igt1:w:w3: {}'
      .format(xc.igts[0].tiers[1].items[2].resolve_ref()))
# print to xml with formatting
print(xigtxml.dumps(xc, pretty_print=True))
