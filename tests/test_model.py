import unittest
from xigt import XigtCorpus, Igt, Tier, Item, Metadata, Meta
from xigt.errors import XigtError

class TestMetadata(unittest.TestCase):
    def test_empty(self):
        m = Metadata()
        self.assertEqual(m.type, None)
        self.assertEqual(m.attributes, dict())
        self.assertEqual(m.metas, [])

    def test_full(self):
        m = Metadata(type='basic',
                     attributes={'attr':'val'},
                     metas=[Meta(text='meta')])
        self.assertEqual(m.type, 'basic')
        self.assertEqual(m.attributes, {'attr':'val'})
        self.assertEqual(len(m.metas), 1)
        self.assertEqual(m[0].text, 'meta')


class TestItem(unittest.TestCase):
    def setUp(self):
        self.i1 = Item()

        self.i2 = Item(
            id='i2',
            type='basic',
            attributes={'attr':'val'},
            text='text'
        )

    def test_id(self):
        self.assertEqual(self.i1.id, None)

        self.assertEqual(self.i2.id, 'i2')

    def test_type(self):
        self.assertEqual(self.i1.type, None)

        self.assertEqual(self.i2.type, 'basic')

    def test_parents(self):
        self.assertEqual(self.i1.tier, None)
        self.assertEqual(self.i1.igt, None)
        self.assertEqual(self.i1.corpus, None)

        self.assertEqual(self.i2.tier, None)
        self.assertEqual(self.i2.igt, None)
        self.assertEqual(self.i2.corpus, None)

    def test_attributes(self):
        self.assertEqual(self.i1.attributes, dict())

        self.assertEqual(self.i2.attributes, {'attr':'val'})

    def test_reference_attributes(self):
        self.assertEqual(self.i1.alignment, None)
        self.assertEqual(self.i1.content, None)
        self.assertEqual(self.i1.segmentation, None)

        self.assertEqual(self.i2.alignment, None)
        self.assertEqual(self.i2.content, None)
        self.assertEqual(self.i2.segmentation, None)

    def test_text(self):
        self.assertEqual(self.i1.text, None)

        self.assertEqual(self.i2.text, 'text')

    def test_value(self):
        self.assertEqual(self.i1.value(), None)

        self.assertEqual(self.i2.value(), 'text')

    def test_span(self):
        # sub-spans of null content is also null content
        self.assertEqual(self.i1.span(0,1), None)

        self.assertEqual(self.i2.span(0,1), 't')


class TestTier(unittest.TestCase):
    def setUp(self):
        self.t1 = Tier()

        self.t2 = Tier(
            id='t',
            type='basic',
            attributes={'attr':'val'},
            metadata=[Metadata(type='meta', metas=[Meta(text='meta')])],
            items=[Item(), Item()]
        )

    def test_init(self):
        # don't allow multiple items with the same ID
        self.assertRaises(XigtError, Tier, items=[Item(id='i1'),
                                                  Item(id='i1')])

    def test_id(self):
        self.assertEqual(self.t1.id, None)

        self.assertEqual(self.t2.id, 't')

    def test_type(self):
        self.assertEqual(self.t1.type, None)

        self.assertEqual(self.t2.type, 'basic')

    def test_parents(self):
        self.assertEqual(self.t1.igt, None)
        self.assertEqual(self.t1.corpus, None)

        self.assertEqual(self.t2.igt, None)
        self.assertEqual(self.t2.corpus, None)

    def test_metadata(self):
        self.assertEqual(len(self.t1.metadata), 0)

        self.assertEqual(self.t2.metadata[0].type, 'meta')
        self.assertEqual(len(self.t2.metadata[0].metas), 1)
        self.assertEqual(self.t2.metadata[0][0].text, 'meta')

    def test_attributes(self):
        self.assertEqual(self.t1.attributes, dict())

        self.assertEqual(self.t2.attributes, {'attr':'val'})

    def test_reference_attributes(self):
        self.assertEqual(self.t1.alignment, None)
        self.assertEqual(self.t1.content, None)
        self.assertEqual(self.t1.segmentation, None)

        self.assertEqual(self.t2.alignment, None)
        self.assertEqual(self.t2.content, None)
        self.assertEqual(self.t2.segmentation, None)

    def test_items(self):
        self.assertEqual(len(self.t1._list), 0)
        self.assertEqual(self.t1.items, [])

        self.assertEqual(len(self.t2.items), 2)
        # contained Items should now have their tier specified
        for i in self.t2.items:
            self.assertEqual(i.tier, self.t2)


class TestIgt(unittest.TestCase):
    def setUp(self):
        self.i1 = Igt()

        self.i2 = Igt(
            id='i1',
            type='basic',
            attributes={'attr':'val'},
            metadata=[Metadata(type='meta',
                               metas=[Meta(text='meta')])],
            tiers=[Tier(id='a'),
                   Tier(id='b')]
        )

    def test_init(self):
        # don't allow multiple tiers with the same ID
        self.assertRaises(XigtError, Igt, tiers=[Tier(id='a'),
                                                 Tier(id='a')])

    def test_id(self):
        self.assertEqual(self.i1.id, None)

        self.assertEqual(self.i2.id, 'i1')

    def test_type(self):
        self.assertEqual(self.i1.type, None)

        self.assertEqual(self.i2.type, 'basic')

    def test_parents(self):
        self.assertEqual(self.i1.corpus, None)

        self.assertEqual(self.i2.corpus, None)

    def test_metadata(self):
        self.assertEqual(len(self.i1.metadata), 0)

        self.assertEqual(self.i2.metadata[0].type, 'meta')
        self.assertEqual(len(self.i2.metadata[0].metas), 1)
        self.assertEqual(self.i2.metadata[0][0].text, 'meta')

    def test_attributes(self):
        self.assertEqual(self.i1.attributes, dict())

        self.assertEqual(self.i2.attributes, {'attr':'val'})

    def test_tiers(self):
        self.assertEqual(len(self.i1.tiers), 0)

        self.assertEqual(len(self.i2.tiers), 2)
        # contained Tiers should now have their igt specified
        for t in self.i2.tiers:
            self.assertEqual(t.igt, self.i2)


class TestXigtCorpus(unittest.TestCase):
    def test_empty(self):
        c = XigtCorpus()
        self.assertEqual(c.id, None)
        self.assertEqual(c.attributes, dict())
        self.assertEqual(len(c.metadata), 0)
        self.assertEqual(len(c.igts), 0)

    def test_basic(self):
        c = XigtCorpus(id='xc1', attributes={'attr':'val'},
                       metadata=[Metadata(type='meta', metas=[Meta(text='meta')])],
                       igts=[Igt(id='i1'), Igt(id='i2')])
        self.assertEqual(c.id, 'xc1')
        self.assertEqual(c.attributes, {'attr':'val'})
        self.assertEqual(c.metadata[0].type, 'meta')
        self.assertEqual(len(c.metadata[0].metas), 1)
        self.assertEqual(c.metadata[0][0].text, 'meta')
        self.assertEqual(len(c.igts), 2)
        # contained Igts should now have their corpus specified
        for i in c.igts:
            self.assertEqual(i.corpus, c)
        # don't allow multiple igts with the same ID
        self.assertRaises(XigtError, XigtCorpus, igts=[Igt(id='i1'),
                                                       Igt(id='i1')])


class TestXigtMixin(unittest.TestCase):
    def test_iter(self):
        t = Tier(items=[Item(text='1'), Item(text='2')])
        self.assertEqual([i.text for i in t], ['1','2'])
        i = Igt(tiers=[Tier(id='a'), Tier(id='b')])
        self.assertEqual([t.id for t in i], ['a', 'b'])
        c = XigtCorpus(igts=[Igt(id='i1'), Igt(id='i2')])
        self.assertEqual([i.id for i in c], ['i1', 'i2'])

    def test_getitem(self):
        t = Tier(items=[Item(id='a1', text='1'),
                        Item(id='a2', text='2')])
        # dictionary key
        self.assertEqual(t['a1'].text, '1')
        self.assertEqual(t['a2'].text, '2')
        # list index
        self.assertEqual(t[0].text, '1')
        self.assertEqual(t[1].text, '2')
        # key error
        self.assertRaises(KeyError, t.__getitem__, 'a3')
        # index error
        self.assertRaises(IndexError, t.__getitem__, 2)

    def test_get(self):
        t = Tier(items=[Item(id='a1', text='1'),
                        Item(id='a2', text='2')])
        # dictionary key
        self.assertEqual(t.get('a1').text, '1')
        self.assertEqual(t.get('a2').text, '2')
        # list index
        self.assertEqual(t.get(0).text, '1')
        self.assertEqual(t.get(1).text, '2')
        # default value
        self.assertEqual(t.get('a3'), None)
        self.assertEqual(t.get('a3', 'z'), 'z')
        self.assertEqual(t.get(2), None)
        self.assertEqual(t.get(2, 'z'), 'z')
