import pytest

from xigt import (
    XigtCorpus, Igt, Tier, Item, Metadata, Meta, ref
)
from xigt.errors import (
    XigtError, XigtStructureError, XigtLookupError
)


class TestStringFunctions():

    def test_expand(self):
        assert ref.expand('') == ''
        assert ref.expand('a1') == 'a1'
        assert ref.expand('a1[3:5]') == 'a1[3:5]'
        assert ref.expand('a1[3:5+6:7]') == 'a1[3:5]+a1[6:7]'
        assert ref.expand('a1[3:5,6:7]') == 'a1[3:5],a1[6:7]'
        assert ref.expand('a1[3:5+6:7,7:8+8:9]') == 'a1[3:5]+a1[6:7],a1[7:8]+a1[8:9]'
        assert ref.expand('a1[3:5]+a1[6:7]') == 'a1[3:5]+a1[6:7]'
        assert ref.expand('a1 a2  a3') == 'a1 a2  a3'
        assert ref.expand('a1[1:2] [2:3+3:4]') == 'a1[1:2] [2:3+3:4]'

    def test_compress(self):
        assert ref.compress('') == ''
        assert ref.compress('a1') == 'a1'
        assert ref.compress('a1[3:5]') == 'a1[3:5]'
        assert ref.compress('a1[3:5+6:7]') == 'a1[3:5+6:7]'
        assert ref.compress('a1[3:5]+a1[6:7]') == 'a1[3:5+6:7]'
        assert ref.compress('a1[3:5]+a1') == 'a1[3:5]+a1'
        assert ref.compress('a1+a1[6:7]') == 'a1+a1[6:7]'
        assert ref.compress('a1[3:5]+a1[5:7]') == 'a1[3:5+5:7]'
        assert ref.compress('a1[3:5]+a2[6:7]') == 'a1[3:5]+a2[6:7]'
        assert ref.compress('a1[3:5]+a2[6:7]+a1[5:6]') == 'a1[3:5]+a2[6:7]+a1[5:6]'
        assert ref.compress('a1[3:5]+a1[6:7],a1[1:2,2:3]') == 'a1[3:5+6:7,1:2,2:3]'
        assert ref.compress('a1 a2  a3') == 'a1 a2  a3'
        assert ref.compress('a1[1:2]+[2:3]') == 'a1[1:2]+[2:3]'

    def test_selections(self):
        assert ref.selections('') == []
        assert ref.selections('a1') == ['a1']
        assert ref.selections('a1[3:5]') == ['a1[3:5]']
        assert ref.selections('a1[3:5+6:7]') == ['a1[3:5+6:7]']
        assert ref.selections('a1[3:5+6:7]+a2[1:4]') == ['a1[3:5+6:7]', '+', 'a2[1:4]']
        assert ref.selections('a1 a2  a3') == ['a1', ' ', 'a2', '  ', 'a3']
        assert ref.selections('a1 123 a2') == ['a1', ' 123 ', 'a2']
        assert ref.selections('a1 [1:3]+a2') == ['a1', ' [1:3]+', 'a2']
        assert ref.selections('a1+a2', keep_delimiters=False) == ['a1', 'a2']

    def test_spans(self):
        assert ref.spans('') == []
        assert ref.spans('a1') == ['a1']
        assert ref.spans('a1[3:5]') == ['a1[3:5]']
        assert ref.spans('a1[3:5+6:7]') == ['a1[3:5]', '+', 'a1[6:7]']
        assert ref.spans('a1[3:5+6:7]', keep_delimiters=False) == ['a1[3:5]', 'a1[6:7]']
        assert ref.spans('a1[3:5+6:7]+a2[1:4]') == ['a1[3:5]', '+', 'a1[6:7]', '+', 'a2[1:4]']
        assert ref.spans('a1 a2  a3') == ['a1', ' ', 'a2', '  ', 'a3']

    def test_ids(self):
        assert ref.ids('') == []
        assert ref.ids('a1') == ['a1']
        assert ref.ids('a1[3:5]') == ['a1']
        assert ref.ids('a1[3:5+6:7]+a2[1:4]') == ['a1', 'a2']
        assert ref.ids('a1[3:5+6:7]+a1[1:4]+a1') == ['a1', 'a1', 'a1']
        assert ref.ids('a1 a2  a3') == ['a1', 'a2', 'a3']


class TestInterpretiveFunctions():

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

    def test_resolve(self):
        with pytest.raises(XigtError): ref.resolve(self.xc1, 'p1')
        with pytest.raises(XigtError): ref.resolve(self.xc1[0]['t'], 'p1')
        assert ref.resolve(self.xc1[0], 'p1') == 'inu=ga san-biki hoe-ru'
        assert ref.resolve(self.xc1[0]['p'], 'p1') == 'inu=ga san-biki hoe-ru'
        assert ref.resolve(self.xc1[0], 't1') == 'Three dogs bark.'
        assert ref.resolve(self.xc1[0], 'p1[0:6]') == 'inu=ga'
        assert ref.resolve(self.xc1[0], 'p1[0:6,7:15]') == 'inu=ga san-biki'

        assert ref.resolve(self.xc3[0], 'w1') == 'inu=ga'
        assert ref.resolve(self.xc3[0], 'm1') == 'inu'
        assert ref.resolve(self.xc3[0], 'g1') == 'dog'

    def test_referents(self):
        assert ref.referents(self.xc1[0], 't', refattrs=('alignment',)) == {'alignment': []}
        assert ref.referents(self.xc1[0], 't1', refattrs=('alignment',)) == {'alignment': []}

        assert ref.referents(self.xc2[0], 't', refattrs=('alignment',)) == {'alignment': ['p']}
        assert ref.referents(self.xc2[0], 't1', refattrs=('alignment',)) == {'alignment': ['p1']}

        assert ref.referents(self.xc3[0], 'w', refattrs=('alignment', 'segmentation')) == {'alignment': [], 'segmentation': ['p']}
        assert ref.referents(self.xc3[0], 'w') == {'alignment': [], 'segmentation': ['p'], 'content': []}
        assert ref.referents(self.xc3[0], 'm') == {'alignment': [], 'segmentation': ['w'], 'content': []}
        assert ref.referents(self.xc3[0], 'g') == {'alignment': ['m'], 'segmentation': [], 'content': []}
        assert ref.referents(self.xc3[0], 'x') == {'alignment': ['w'], 'segmentation': [], 'content': []}
        assert ref.referents(self.xc3[0], 'x', refattrs=('alignment', 'children')) == {'alignment': ['w'], 'children': ['x']}
        assert ref.referents(self.xc3[0], 'x1', refattrs=('alignment', 'children')) == {'alignment': ['w1'], 'children': []}
        assert ref.referents(self.xc3[0], 'x4', refattrs=('alignment', 'children')) == {'alignment': [], 'children': ['x1', 'x2']}

    def test_referrers(self):
        assert ref.referrers(self.xc1[0], 'p', refattrs=('alignment',)) == {'alignment': []}
        assert ref.referrers(self.xc1[0], 'p1', refattrs=('alignment',)) == {'alignment': []}

        assert ref.referrers(self.xc2[0], 'p', refattrs=('alignment',)) == {'alignment': ['t']}
        assert ref.referrers(self.xc2[0], 'p1', refattrs=('alignment',)) == {'alignment': ['t1']}

        assert ref.referrers(self.xc3[0], 'p', refattrs=('alignment', 'segmentation')) == {'alignment': ['t'], 'segmentation': ['w']}
        assert ref.referrers(self.xc3[0], 'p') == {'alignment': ['t'], 'segmentation': ['w'], 'content': []}
        assert ref.referrers(self.xc3[0], 'w') == {'alignment': ['x'], 'segmentation': ['m'], 'content': []}
        assert ref.referrers(self.xc3[0], 'm') == {'alignment': ['g'], 'segmentation': [], 'content': []}
        assert ref.referrers(self.xc3[0], 'x') == {'alignment': [], 'segmentation': [], 'content': []}
        assert ref.referrers(self.xc3[0], 'x', refattrs=('alignment', 'children')) == {'alignment': [], 'children': ['x']}
        assert ref.referrers(self.xc3[0], 'x1', refattrs=('alignment', 'children')) == {'alignment': [], 'children': ['x4']}

    def test_dereference(self):
        with pytest.raises(XigtLookupError): ref.dereference(self.xc1, 'alignment')
        with pytest.raises(XigtLookupError): ref.dereference(self.xc1[0], 'alignment')
        with pytest.raises(KeyError): ref.dereference(self.xc1[0]['p'], 'alignment')

        assert ref.dereference(self.xc2[0]['t'], 'alignment').id == 'p'

        assert ref.dereference(self.xc3[0]['g'], 'alignment').id == 'm'
        assert ref.dereference(self.xc3[0]['m'], 'segmentation').id == 'w'
        assert ref.dereference(self.xc3[0]['m']['m1'], 'segmentation').id == 'w1'
        assert ref.dereference(self.xc3[0]['x']['x4'], 'children').id == 'x1'

    def test_dereference_all(self):
        with pytest.raises(XigtLookupError): ref.dereference_all(self.xc1, 'alignment')
        with pytest.raises(XigtLookupError): ref.dereference_all(self.xc1[0], 'alignment')
        with pytest.raises(KeyError): ref.dereference_all(self.xc1[0]['p'], 'alignment')

        assert [x.id for x in ref.dereference_all(self.xc2[0]['t'], 'alignment')] == ['p']

        assert [x.id for x in ref.dereference_all(self.xc3[0]['g'], 'alignment')] == ['m']
        assert [x.id for x in ref.dereference_all(self.xc3[0]['m'], 'segmentation')] == ['w']
        assert [x.id for x in ref.dereference_all(self.xc3[0]['m']['m1'], 'segmentation')] == ['w1']
        assert [x.id for x in ref.dereference_all(self.xc3[0]['x']['x4'], 'children')] == ['x1', 'x2']
