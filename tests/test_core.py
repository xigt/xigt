import unittest
from xigt.core import XigtCorpus, Igt, Tier, Item, Metadata

class TestMetadata(unittest.TestCase):
    def test_empty(self):
        m = Metadata()
        self.assertEqual(m.type, None)
        self.assertEqual(m.attributes, dict())
        self.assertEqual(m.content, None)

    def test_full(self):
        m = Metadata(type='basic',
                     attributes={'attr':'val'},
                     content='content')
        self.assertEqual(m.type, 'basic')
        self.assertEqual(m.attributes, {'attr':'val'})
        self.assertEqual(m.content, 'content')

class TestItem(unittest.TestCase):
    def test_empty(self):
        i = Item()
        # empty members
        self.assertEqual(i.type, None)
        self.assertEqual(i.id, None)
        self.assertEqual(i.tier, None)
        self.assertEqual(i.igt, None)
        self.assertEqual(i.corpus, None)
        self.assertEqual(i.attributes, dict())
        self.assertEqual(i.content, None)
        # sub-spans of null content is also null content
        self.assertEqual(i.span(0,1), None)

    def test_basic(self):
        i = Item(id='i1', type='basic', attributes={'attr':'val'},
                 content='content')
        self.assertEqual(i.type, 'basic')
        self.assertEqual(i.id, 'i1')
        self.assertEqual(i.tier, None)
        self.assertEqual(i.igt, None)
        self.assertEqual(i.corpus, None)
        self.assertEqual(i.attributes, {'attr':'val'})
        self.assertEqual(i.content, 'content')
        # sub-spans of null content is also null content
        self.assertEqual(i.span(0,1), 'c')

    def test_linked(self):
        #t = Tier(id='t', items=[Item(id='t1',content='content')])
        pass

class TestTier(unittest.TestCase):
    def test_empty(self):
        t = Tier()
        # empty members
        self.assertEqual(t.type, None)
        self.assertEqual(t.id, None)
        self.assertEqual(t.igt, None)
        self.assertEqual(t.corpus, None)
        self.assertEqual(t.metadata, None)
        self.assertEqual(t.attributes, dict())
        self.assertEqual(len(t.items), 0)
        # empty properties
        self.assertEqual(t.items, [])

    def test_basic(self):
        t = Tier(id='t', type='basic',
                 attributes={'attr':'val'},
                 metadata=Metadata(type='meta', content='metacontent'),
                 items=[Item(), Item()])
        self.assertEqual(t.type, 'basic')
        self.assertEqual(t.id, 't')
        self.assertEqual(t.igt, None)
        self.assertEqual(t.corpus, None)
        self.assertEqual(t.metadata.type, 'meta')
        self.assertEqual(t.metadata.content, 'metacontent')
        self.assertEqual(t.attributes, {'attr':'val'})
        self.assertEqual(len(t.items), 2)
        # contained Items should now have their tier specified
        for i in t.items:
            self.assertEqual(i.tier, t)
        # don't allow multiple items with the same ID
        self.assertRaises(ValueError, Tier, items=[Item(id='i1'),
                                                   Item(id='i1')])

    def test_linked(self):
        pass

class TestIgt(unittest.TestCase):
    def test_empty(self):
        i = Igt()
        self.assertEqual(i.id, None)
        self.assertEqual(i.attributes, dict())
        self.assertEqual(i.corpus, None)
        self.assertEqual(i.metadata, None)
        self.assertEqual(len(i.tiers), 0)

    def test_basic(self):
        i = Igt(id='i1', type='basic', attributes={'attr':'val'},
                metadata=Metadata(type='meta', content='metacontent'),
                tiers=[Tier(id='a'), Tier(id='b')])
        self.assertEqual(i.id, 'i1')
        self.assertEqual(i.attributes, {'attr':'val'})
        self.assertEqual(i.corpus, None)
        self.assertEqual(i.metadata.type, 'meta')
        self.assertEqual(i.metadata.content, 'metacontent')
        self.assertEqual(len(i.tiers), 2)
        # contained Tiers should now have their igt specified
        for t in i.tiers:
            self.assertEqual(t.igt, i)
        # don't allow multiple tiers with the same ID
        self.assertRaises(ValueError, Igt, tiers=[Tier(id='a'),
                                                  Tier(id='a')])

    def test_linked(self):
        pass

class TestXigtCorpus(unittest.TestCase):
    def test_empty(self):
        c = XigtCorpus()
        self.assertEqual(c.id, None)
        self.assertEqual(c.attributes, dict())
        self.assertEqual(c.metadata, None)
        self.assertEqual(len(c.igts), 0)

    def test_basic(self):
        c = XigtCorpus(id='xc1', attributes={'attr':'val'},
                       metadata=Metadata(type='meta', content='metacontent'),
                       igts=[Igt(id='i1'), Igt(id='i2')])
        self.assertEqual(c.id, 'xc1')
        self.assertEqual(c.attributes, {'attr':'val'})
        self.assertEqual(c.metadata.type, 'meta')
        self.assertEqual(c.metadata.content, 'metacontent')
        self.assertEqual(len(c.igts), 2)
        # contained Igts should now have their corpus specified
        for i in c.igts:
            self.assertEqual(i.corpus, c)
        # don't allow multiple igts with the same ID
        self.assertRaises(ValueError, XigtCorpus, igts=[Igt(id='i1'),
                                                        Igt(id='i1')])

    def test_linked(self):
        pass

class TestXigtMixin(unittest.TestCase):
    def test_iter(self):
        t = Tier(items=[Item(content='1'), Item(content='2')])
        self.assertEqual([i.content for i in t], ['1','2'])
        i = Igt(tiers=[Tier(id='a'), Tier(id='b')])
        self.assertEqual([t.id for t in i], ['a', 'b'])
        c = XigtCorpus(igts=[Igt(id='i1'), Igt(id='i2')])
        self.assertEqual([i.id for i in c], ['i1', 'i2'])

    def test_getitem(self):
        t = Tier(items=[Item(id='a1', content='1'),
                        Item(id='a2', content='2')])
        # dictionary key
        self.assertEqual(t['a1'].content, '1')
        self.assertEqual(t['a2'].content, '2')
        # list index
        self.assertEqual(t[0].content, '1')
        self.assertEqual(t[1].content, '2')
        # key error
        self.assertRaises(KeyError, t.__getitem__, 'a3')
        # index error
        self.assertRaises(IndexError, t.__getitem__, 2)

    def test_get(self):
        t = Tier(items=[Item(id='a1', content='1'),
                        Item(id='a2', content='2')])
        # dictionary key
        self.assertEqual(t.get('a1').content, '1')
        self.assertEqual(t.get('a2').content, '2')
        # list index
        self.assertEqual(t.get(0).content, '1')
        self.assertEqual(t.get(1).content, '2')
        # default value
        self.assertEqual(t.get('a3'), None)
        self.assertEqual(t.get('a3', 'z'), 'z')
        self.assertEqual(t.get(2), None)
        self.assertEqual(t.get(2, 'z'), 'z')
