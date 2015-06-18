import unittest

from xigt import (
    XigtCorpus, Igt, Tier, Item, Metadata, Meta
)
from xigt.query import (ancestors, descendants)
from xigt.errors import (
    XigtError, XigtStructureError, XigtLookupError
)


class TestQueries(unittest.TestCase):

    def setUp(self):
        # no alignments
        self.xc1 = XigtCorpus(id='xc1', igts=[
            Igt(id='i1', tiers=[
                Tier(id='p', type='phrases', items=[
                    Item(id='p1', text='inu=ga san-biki hoe-ru')
                ]),
                Tier(id='t', type='translations', items=[
                    Item(id='t1', text='Three dogs bark.')
                ])
            ])
        ])

        # basic alignment
        self.xc2 = XigtCorpus(id='xc1', igts=[
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
        self.xc3 = XigtCorpus(id='xc1', igts=[
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
        self.xc4 = XigtCorpus(id='xc1', igts=[
            Igt(id='i1', tiers=[
                Tier(id="w", type="words", segmentation="w", items=[
                    Item(id="w1", segmentation="w1")
                ])
            ])
        ])

        # cycle 2
        self.xc5 = XigtCorpus(id='xc1', igts=[
            Igt(id='i1', tiers=[
                Tier(id="w", type="words", segmentation="w", items=[
                    Item(id="w1", segmentation="w1,w2"),
                    Item(id="w2", segmentation="w1,w2")
                ])
            ])
        ])

    def check(self, result, srcid, refattr, refid, refitemids):
        srctier, refattr_, reftier, refitems = result
        self.assertEqual(srctier.id, srcid)
        self.assertEqual(refattr_, refattr)
        self.assertEqual(reftier.id, refid)
        self.assertEqual(len(refitems), len(refitemids))
        self.assertEqual([i.id for i in refitems], refitemids)


    def test_ancestors(self):
        ancs = list(ancestors(self.xc1[0]['t']))
        self.assertEqual(ancs, [])

        ancs = list(ancestors(self.xc2[0]['t']))
        self.assertEqual(len(ancs), 1)
        self.check(ancs[0], 't', 'alignment', 'p', ['p1'])

        ancs = list(ancestors(self.xc3[0]['m']))
        self.assertEqual(len(ancs), 2)
        self.check(ancs[0], 'm', 'segmentation', 'w', ['w1', 'w2', 'w3'])
        self.check(ancs[1], 'w', 'segmentation', 'p', ['p1'])

        ancs = list(ancestors(self.xc3[0]['m']['m1']))
        self.assertEqual(len(ancs), 2)
        self.check(ancs[0], 'm', 'segmentation', 'w', ['w1'])
        self.check(ancs[1], 'w', 'segmentation', 'p', ['p1'])

        ancs = list(ancestors(self.xc4[0]['w']['w1']))
        self.assertEqual(len(ancs), 1)
        self.check(ancs[0], 'w', 'segmentation', 'w', ['w1'])

        ancs = list(ancestors(self.xc5[0]['w']))
        self.assertEqual(len(ancs), 1)
        self.check(ancs[0], 'w', 'segmentation', 'w', ['w1', 'w2'])

    def test_descendants(self):
        desc = list(descendants(self.xc1[0]['p']))
        self.assertEqual(desc, [])

        desc = list(descendants(self.xc2[0]['p']))
        self.assertEqual(len(desc), 1)
        self.check(desc[0], 'p', 'alignment', 't', ['t1'])

        desc = list(descendants(self.xc3[0]['p']))
        self.assertEqual(len(desc), 3)
        self.check(desc[0], 'p', 'segmentation', 'w', ['w1', 'w2', 'w3'])
        self.check(desc[1], 'w', 'segmentation', 'm',
                   ['m1', 'm2', 'm3', 'm4', 'm5', 'm6'])
        self.check(desc[2], 'm', 'alignment', 'g',
                   ['g1', 'g2', 'g3', 'g4', 'g5', 'g6'])

        desc = list(descendants(self.xc3[0]['w']['w1']))
        self.assertEqual(len(desc), 2)
        self.check(desc[0], 'w', 'segmentation', 'm', ['m1', 'm2'])
        self.check(desc[1], 'm', 'alignment', 'g', ['g1', 'g2'])

        desc = list(descendants(self.xc3[0]['p'], follow='all'))
        self.assertEqual(len(desc), 5)
        self.check(desc[0], 'p', 'segmentation', 'w', ['w1', 'w2', 'w3'])
        self.check(desc[1], 'p', 'alignment', 't', ['t1'])
        self.check(desc[2], 'w', 'segmentation', 'm',
                   ['m1', 'm2', 'm3', 'm4', 'm5', 'm6'])
        self.check(desc[3], 'w', 'alignment', 'x',
                   ['x1', 'x2', 'x3'])
        self.check(desc[4], 'm', 'alignment', 'g',
                   ['g1', 'g2', 'g3', 'g4', 'g5', 'g6'])

        desc = list(
            descendants(self.xc3[0]['p'],
                        refattrs=('segmentation', 'alignment', 'children'),
                        follow='all')
        )
        self.assertEqual(len(desc), 6)
        self.check(desc[0], 'p', 'segmentation', 'w', ['w1', 'w2', 'w3'])
        self.check(desc[1], 'p', 'alignment', 't', ['t1'])
        self.check(desc[2], 'w', 'segmentation', 'm',
                   ['m1', 'm2', 'm3', 'm4', 'm5', 'm6'])
        self.check(desc[3], 'w', 'alignment', 'x',
                   ['x1', 'x2', 'x3'])
        self.check(desc[4], 'm', 'alignment', 'g',
                   ['g1', 'g2', 'g3', 'g4', 'g5', 'g6'])
        self.check(desc[5], 'x', 'children', 'x',
                   ['x4', 'x5'])

        desc = list(descendants(self.xc4[0]['w']))
        self.assertEqual(len(desc), 1)
        self.check(desc[0], 'w', 'segmentation', 'w', ['w1'])

        desc = list(descendants(self.xc4[0]['w'], follow='all'))
        self.assertEqual(len(desc), 1)
        self.check(desc[0], 'w', 'segmentation', 'w', ['w1'])

        desc = list(descendants(self.xc5[0]['w']))
        self.assertEqual(len(desc), 1)
        self.check(desc[0], 'w', 'segmentation', 'w', ['w1', 'w2'])

        desc = list(descendants(self.xc5[0]['w'], follow='all'))
        self.assertEqual(len(desc), 1)
        self.check(desc[0], 'w', 'segmentation', 'w', ['w1', 'w2'])
