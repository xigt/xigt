
from xigt import (
  XigtCorpus, Igt, Tier, Item, Metadata, Meta, MetaChild
)

# no alignments
xc1 = XigtCorpus(id='xc1', igts=[
  Igt(id='i1', tiers=[
    Tier(id='p', type='phrases', items=[
      Item(id='p1', text='inu=ga san-biki hoe-ru')
    ]),
    Tier(id='t', type='translations', items=[
      Item(id='t1', text='Three dogs bark.')
    ])
  ])
])

# no alignments, with metadata
xc1m = XigtCorpus(id='xc1', igts=[
  Igt(id='i1', metadata=[
    Metadata(id="md1", metas=[
      Meta(id="meta1", children=[
        MetaChild(name='subject',
          namespace='http://purl.org/dc/elements/1.1/',
          attributes={
            '{http://www.w3.org/2001/XMLSchema-instance}type': 'olac:language',
            '{http://www.language-archives.org/OLAC/1.1/}code': 'jpn'
          },
          text='Japanese'
        ),
        MetaChild(name='language',
          namespace='http://purl.org/dc/elements/1.1/',
          attributes={
            '{http://www.w3.org/2001/XMLSchema-instance}type': 'olac:language',
            '{http://www.language-archives.org/OLAC/1.1/}code': 'eng'
          },
          text='English'
        )
      ])
    ])],
    tiers=[
        Tier(id='p', type='phrases', items=[
          Item(id='p1', text='inu=ga san-biki hoe-ru')
        ]),
        Tier(id='t', type='translations', items=[
          Item(id='t1', text='Three dogs bark.')
        ])
      ]
  )],
  nsmap={
    'olac': 'http://www.language-archives.org/OLAC/1.1/',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
  }
)

# basic alignment
xc2 = XigtCorpus(id='xc1', igts=[
  Igt(id='i1', tiers=[
    Tier(id='p', type='phrases', items=[
      Item(id='p1', text='inu=ga san-biki hoe-ru')
    ]),
    Tier(id='t', type='translations', alignment='p', items=[
      Item(id='t1', alignment='p1', text='Three dogs bark.')
    ])
  ])
])

# multi-level alignments
# basic alignment
xc3 = XigtCorpus(id='xc1', igts=[
  Igt(id='i1', tiers=[
    Tier(id='p', type='phrases', items=[
      Item(id='p1', text='inu=ga san-biki hoe-ru')
    ]),
    Tier(id='w', type='words', segmentation='p', items=[
      Item(id='w1', segmentation='p1[0:6]'),
      Item(id='w2', segmentation='p1[7:15]'),
      Item(id='w3', segmentation='p1[16:22]')
    ]),
    Tier(id='m', type='morphemes', segmentation='w', items=[
      Item(id='m1', segmentation='w1[0:3]'),
      Item(id='m2', segmentation='w1[4:6]'),
      Item(id='m3', segmentation='w2[0:3]'),
      Item(id='m4', segmentation='w2[4:8]'),
      Item(id='m5', segmentation='w3[0:3]'),
      Item(id='m6', segmentation='w3[4:6]')
    ]),
    Tier(id='g', type='glosses', alignment='m', items=[
      Item(id='g1', alignment='m1', text='dog'),
      Item(id='g2', alignment='m2', text='NOM'),
      Item(id='g3', alignment='m3', text='three'),
      Item(id='g4', alignment='m4', text='NUMCL.animal'),
      Item(id='g5', alignment='m5', text='bark'),
      Item(id='g6', alignment='m6', text='IMP')
    ]),
    Tier(id='x', type='syntax', alignment='w',
       attributes={'children': 'x'}, items=[
      Item(id='x1', alignment='w1', text='NP'),
      Item(id='x2', alignment='w2', text='NUMCL'),
      Item(id='x3', alignment='w3', text='VBZ'),
      Item(id='x4', attributes={'children': 'x1 x2'}, text='NP'),
      Item(id='x5', attributes={'children': 'x4 x3'}, text='S')
    ]),
    Tier(id='t', type='translations', alignment='p', items=[
      Item(id='t1', alignment='p1', text='Three dogs bark.')
    ])
  ])
])

# cycle 1
xc4 = XigtCorpus(id='xc1', igts=[
  Igt(id='i1', tiers=[
    Tier(id="w", type="words", segmentation="w", items=[
      Item(id="w1", segmentation="w1")
    ])
  ])
])

# cycle 2
xc5 = XigtCorpus(id='xc1', igts=[
  Igt(id='i1', tiers=[
    Tier(id="w", type="words", segmentation="w", items=[
      Item(id="w1", segmentation="w1,w2"),
      Item(id="w2", segmentation="w1,w2")
    ])
  ])
])

if __name__ == '__main__':
  from xigt.codecs import xigtxml
  print(xigtxml.dumps(xc1m))