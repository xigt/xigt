from xigt.query import (ancestors, descendants)

from .example_corpora import (
    xc1, xc2, xc3, xc4, xc5
)


class TestQueries():

    def check(self, result, srcid, refattr, refid, refitemids):
        srctier, refattr_, reftier, refitems = result
        assert srctier.id == srcid
        assert refattr_ == refattr
        assert reftier.id == refid
        assert len(refitems) == len(refitemids)
        assert [i.id for i in refitems] == refitemids


    def test_ancestors(self):
        ancs = list(ancestors(xc1[0]['t']))
        assert ancs == []

        ancs = list(ancestors(xc2[0]['t']))
        assert len(ancs) == 1
        self.check(ancs[0], 't', 'alignment', 'p', ['p1'])

        ancs = list(ancestors(xc3[0]['m']))
        assert len(ancs) == 2
        self.check(ancs[0], 'm', 'segmentation', 'w', ['w1', 'w2', 'w3'])
        self.check(ancs[1], 'w', 'segmentation', 'p', ['p1'])

        ancs = list(ancestors(xc3[0]['m']['m1']))
        assert len(ancs) == 2
        self.check(ancs[0], 'm', 'segmentation', 'w', ['w1'])
        self.check(ancs[1], 'w', 'segmentation', 'p', ['p1'])

        ancs = list(ancestors(xc4[0]['w']['w1']))
        assert len(ancs) == 1
        self.check(ancs[0], 'w', 'segmentation', 'w', ['w1'])

        ancs = list(ancestors(xc5[0]['w']))
        assert len(ancs) == 1
        self.check(ancs[0], 'w', 'segmentation', 'w', ['w1', 'w2'])

    def test_descendants(self):
        desc = list(descendants(xc1[0]['p']))
        assert desc == []

        desc = list(descendants(xc2[0]['p']))
        assert len(desc) == 1
        self.check(desc[0], 'p', 'alignment', 't', ['t1'])

        desc = list(descendants(xc3[0]['p']))
        assert len(desc) == 3
        self.check(desc[0], 'p', 'segmentation', 'w', ['w1', 'w2', 'w3'])
        self.check(desc[1], 'w', 'segmentation', 'm',
                   ['m1', 'm2', 'm3', 'm4', 'm5', 'm6'])
        self.check(desc[2], 'm', 'alignment', 'g',
                   ['g1', 'g2', 'g3', 'g4', 'g5', 'g6'])

        desc = list(descendants(xc3[0]['w']['w1']))
        assert len(desc) == 2
        self.check(desc[0], 'w', 'segmentation', 'm', ['m1', 'm2'])
        self.check(desc[1], 'm', 'alignment', 'g', ['g1', 'g2'])

        desc = list(descendants(xc3[0]['p'], follow='all'))
        assert len(desc) == 5
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
        assert len(desc) == 6
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
        assert len(desc) == 1
        self.check(desc[0], 'w', 'segmentation', 'w', ['w1'])

        desc = list(descendants(xc4[0]['w'], follow='all'))
        assert len(desc) == 1
        self.check(desc[0], 'w', 'segmentation', 'w', ['w1'])

        desc = list(descendants(xc5[0]['w']))
        assert len(desc) == 1
        self.check(desc[0], 'w', 'segmentation', 'w', ['w1', 'w2'])

        desc = list(descendants(xc5[0]['w'], follow='all'))
        assert len(desc) == 1
        self.check(desc[0], 'w', 'segmentation', 'w', ['w1', 'w2'])
