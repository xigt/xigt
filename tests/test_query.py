import unittest

from xigt.query import (ancestors, descendants)

from .example_corpora import (
    xc1, xc2, xc3, xc4, xc5
)


class TestQueries(unittest.TestCase):

    def check(self, result, srcid, refattr, refid, refitemids):
        srctier, refattr_, reftier, refitems = result
        self.assertEqual(srctier.id, srcid)
        self.assertEqual(refattr_, refattr)
        self.assertEqual(reftier.id, refid)
        self.assertEqual(len(refitems), len(refitemids))
        self.assertEqual([i.id for i in refitems], refitemids)


    def test_ancestors(self):
        ancs = list(ancestors(xc1[0]['t']))
        self.assertEqual(ancs, [])

        ancs = list(ancestors(xc2[0]['t']))
        self.assertEqual(len(ancs), 1)
        self.check(ancs[0], 't', 'alignment', 'p', ['p1'])

        ancs = list(ancestors(xc3[0]['m']))
        self.assertEqual(len(ancs), 2)
        self.check(ancs[0], 'm', 'segmentation', 'w', ['w1', 'w2', 'w3'])
        self.check(ancs[1], 'w', 'segmentation', 'p', ['p1'])

        ancs = list(ancestors(xc3[0]['m']['m1']))
        self.assertEqual(len(ancs), 2)
        self.check(ancs[0], 'm', 'segmentation', 'w', ['w1'])
        self.check(ancs[1], 'w', 'segmentation', 'p', ['p1'])

        ancs = list(ancestors(xc4[0]['w']['w1']))
        self.assertEqual(len(ancs), 1)
        self.check(ancs[0], 'w', 'segmentation', 'w', ['w1'])

        ancs = list(ancestors(xc5[0]['w']))
        self.assertEqual(len(ancs), 1)
        self.check(ancs[0], 'w', 'segmentation', 'w', ['w1', 'w2'])

    def test_descendants(self):
        desc = list(descendants(xc1[0]['p']))
        self.assertEqual(desc, [])

        desc = list(descendants(xc2[0]['p']))
        self.assertEqual(len(desc), 1)
        self.check(desc[0], 'p', 'alignment', 't', ['t1'])

        desc = list(descendants(xc3[0]['p']))
        self.assertEqual(len(desc), 3)
        self.check(desc[0], 'p', 'segmentation', 'w', ['w1', 'w2', 'w3'])
        self.check(desc[1], 'w', 'segmentation', 'm',
                   ['m1', 'm2', 'm3', 'm4', 'm5', 'm6'])
        self.check(desc[2], 'm', 'alignment', 'g',
                   ['g1', 'g2', 'g3', 'g4', 'g5', 'g6'])

        desc = list(descendants(xc3[0]['w']['w1']))
        self.assertEqual(len(desc), 2)
        self.check(desc[0], 'w', 'segmentation', 'm', ['m1', 'm2'])
        self.check(desc[1], 'm', 'alignment', 'g', ['g1', 'g2'])

        desc = list(descendants(xc3[0]['p'], follow='all'))
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
            descendants(xc3[0]['p'],
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

        desc = list(descendants(xc4[0]['w']))
        self.assertEqual(len(desc), 1)
        self.check(desc[0], 'w', 'segmentation', 'w', ['w1'])

        desc = list(descendants(xc4[0]['w'], follow='all'))
        self.assertEqual(len(desc), 1)
        self.check(desc[0], 'w', 'segmentation', 'w', ['w1'])

        desc = list(descendants(xc5[0]['w']))
        self.assertEqual(len(desc), 1)
        self.check(desc[0], 'w', 'segmentation', 'w', ['w1', 'w2'])

        desc = list(descendants(xc5[0]['w'], follow='all'))
        self.assertEqual(len(desc), 1)
        self.check(desc[0], 'w', 'segmentation', 'w', ['w1', 'w2'])
