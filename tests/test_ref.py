import unittest
from xigt import (
    XigtCorpus, Igt, Tier, Item, Metadata, Meta, ref
)
from xigt.errors import XigtError, XigtStructureError


class TestStringFunctions(unittest.TestCase):

    def test_expand(self):
        self.assertEqual(ref.expand(''), '')
        self.assertEqual(ref.expand('a1'),
                                    'a1')
        self.assertEqual(ref.expand('a1[3:5]'),
                                    'a1[3:5]')
        self.assertEqual(ref.expand('a1[3:5+6:7]'),
                                    'a1[3:5]+a1[6:7]')
        self.assertEqual(ref.expand('a1[3:5,6:7]'),
                                    'a1[3:5],a1[6:7]')
        self.assertEqual(ref.expand('a1[3:5+6:7,7:8+8:9]'),
                                    'a1[3:5]+a1[6:7],a1[7:8]+a1[8:9]')
        self.assertEqual(ref.expand('a1[3:5]+a1[6:7]'),
                                    'a1[3:5]+a1[6:7]')
        self.assertEqual(ref.expand('a1 a2  a3'),
                                    'a1 a2  a3')
        self.assertEqual(ref.expand('a1[1:2] [2:3+3:4]'),
                                    'a1[1:2] [2:3+3:4]')

    def test_compress(self):
        self.assertEqual(ref.compress(''), '')
        self.assertEqual(ref.compress('a1'),
                                      'a1')
        self.assertEqual(ref.compress('a1[3:5]'),
                                      'a1[3:5]')
        self.assertEqual(ref.compress('a1[3:5+6:7]'),
                                      'a1[3:5+6:7]')
        self.assertEqual(ref.compress('a1[3:5]+a1[6:7]'),
                                      'a1[3:5+6:7]')
        self.assertEqual(ref.compress('a1[3:5]+a1'),
                                      'a1[3:5]+a1')
        self.assertEqual(ref.compress('a1+a1[6:7]'),
                                      'a1+a1[6:7]')
        self.assertEqual(ref.compress('a1[3:5]+a1[5:7]'),
                                      'a1[3:5+5:7]')
        self.assertEqual(ref.compress('a1[3:5]+a2[6:7]'),
                                      'a1[3:5]+a2[6:7]')
        self.assertEqual(ref.compress('a1[3:5]+a2[6:7]+a1[5:6]'),
                                      'a1[3:5]+a2[6:7]+a1[5:6]')
        self.assertEqual(ref.compress('a1[3:5]+a1[6:7],a1[1:2,2:3]'),
                                      'a1[3:5+6:7,1:2,2:3]')
        self.assertEqual(ref.compress('a1 a2  a3'),
                                      'a1 a2  a3')
        self.assertEqual(ref.compress('a1[1:2]+[2:3]'),
                                      'a1[1:2]+[2:3]')

    def test_selections(self):
        self.assertEqual(ref.selections(''), [])
        self.assertEqual(ref.selections('a1'),
                                       ['a1'])
        self.assertEqual(ref.selections('a1[3:5]'),
                                       ['a1[3:5]'])
        self.assertEqual(ref.selections('a1[3:5+6:7]'),
                                       ['a1[3:5+6:7]'])
        self.assertEqual(ref.selections('a1[3:5+6:7]+a2[1:4]'),
                                       ['a1[3:5+6:7]', '+', 'a2[1:4]'])
        self.assertEqual(ref.selections('a1 a2  a3'),
                                       ['a1', ' ', 'a2', '  ', 'a3'])
        self.assertEqual(ref.selections('a1 123 a2'),
                                       ['a1', ' 123 ', 'a2'])
        self.assertEqual(ref.selections('a1 [1:3]+a2'),
                                       ['a1', ' [1:3]+', 'a2'])
        self.assertEqual(ref.selections('a1+a2', keep_delimiters=False),
                                       ['a1', 'a2'])

    def test_spans(self):
        self.assertEqual(ref.spans(''), [])
        self.assertEqual(ref.spans('a1'),
                                  ['a1'])
        self.assertEqual(ref.spans('a1[3:5]'),
                                  ['a1[3:5]'])
        self.assertEqual(ref.spans('a1[3:5+6:7]'),
                                  ['a1[3:5]', '+', 'a1[6:7]'])
        self.assertEqual(ref.spans('a1[3:5+6:7]', keep_delimiters=False),
                                  ['a1[3:5]', 'a1[6:7]'])
        self.assertEqual(ref.spans('a1[3:5+6:7]+a2[1:4]'),
                                  ['a1[3:5]', '+', 'a1[6:7]', '+', 'a2[1:4]'])
        self.assertEqual(ref.spans('a1 a2  a3'),
                                  ['a1', ' ', 'a2', '  ', 'a3']
        )

    def test_ids(self):
        self.assertEqual(ref.ids(''), [])
        self.assertEqual(ref.ids('a1'),
                        ['a1'])
        self.assertEqual(ref.ids('a1[3:5]'),
                        ['a1'])
        self.assertEqual(ref.ids('a1[3:5+6:7]+a2[1:4]'),
                        ['a1', 'a2'])
        self.assertEqual(ref.ids('a1[3:5+6:7]+a1[1:4]+a1'),
                        ['a1', 'a1', 'a1'])
        self.assertEqual(ref.ids('a1 a2  a3'),
                        ['a1', 'a2', 'a3'])


class TestInterpretiveFunctions(unittest.TestCase):

    def setUp(self):
        pass
        # no alignments
        # basic alignment
        # multi-level alignments

    def test_resolve(self):
        pass

    def test_referents(self):
        pass

    def test_referrers(self):
        pass

    def test_dereference(self):
        pass

    def test_dereference_all(self):
        pass
