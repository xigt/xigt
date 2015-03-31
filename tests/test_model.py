import unittest
from xigt import XigtCorpus, Igt, Tier, Item, Metadata, Meta
from xigt.errors import XigtError, XigtStructureError

class TestMetadata(unittest.TestCase):
    def test_init(self):
        self.assertRaises(ValueError, Metadata, id='1')  # invalid id        

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
        # empty
        self.i1 = Item()

        # basic info
        self.i2 = Item(
            id='i2',
            type='basic',
            attributes={'attr':'val'},
            text='text'
        )

        # alignment and content refs
        self.i_ac = Item(
            id='i_ac',
            alignment='i2',
            content='i2[0:2]'
        )

        # segmentation ref
        self.i_s = Item(
            id='i_s',
            segmentation='i2[2:4]'
        )

        # override content ref with text
        self.i_t = Item(
            id='i_t',
            content='i2',
            text='something else'
        )

        # contextual structure
        self.t_a = Tier(id='t_a', items=[self.i2])
        self.t_b = Tier(id='t_b', items=[self.i_ac, self.i_t],
                        alignment='t_a', content='t_a')
        self.t_c = Tier(id='t_c', items=[self.i_s], segmentation='t_a')
        self.igt = Igt(tiers=[self.t_a, self.t_b, self.t_c])
        self.xc = XigtCorpus(igts=[self.igt])


    def test_init(self):
        self.assertRaises(ValueError, Item, id='1')  # invalid id

    def test_id(self):
        self.assertIs(self.i1.id, None)

        self.assertEqual(self.i2.id, 'i2')

        self.assertEqual(self.i_ac.id, 'i_ac')
        self.assertEqual(self.i_s.id, 'i_s')
        self.assertEqual(self.i_t.id, 'i_t')

    def test_type(self):
        self.assertIs(self.i1.type, None)

        self.assertEqual(self.i2.type, 'basic')

        self.assertIs(self.i_ac.type, None)
        self.assertIs(self.i_s.type, None)
        self.assertIs(self.i_t.type, None)

    def test_parents(self):
        self.assertIs(self.i1.tier, None)
        self.assertIs(self.i1.igt, None)
        self.assertIs(self.i1.corpus, None)

        self.assertIs(self.i2.tier, self.t_a)
        self.assertIs(self.i2.igt, self.igt)
        self.assertIs(self.i2.corpus, self.xc)

        self.assertEqual(self.i_ac.tier, self.t_b)
        self.assertEqual(self.i_ac.igt, self.igt)
        self.assertEqual(self.i_ac.corpus, self.xc)

        self.assertEqual(self.i_s.tier, self.t_c)
        self.assertEqual(self.i_s.igt, self.igt)
        self.assertEqual(self.i_s.corpus, self.xc)

        self.assertEqual(self.i_t.tier, self.t_b)
        self.assertEqual(self.i_t.igt, self.igt)
        self.assertEqual(self.i_t.corpus, self.xc)

    def test_attributes(self):
        self.assertEqual(self.i1.attributes, dict())

        self.assertEqual(self.i2.attributes, {'attr':'val'})

        self.assertEqual(self.i_ac.attributes,
                         {'alignment': 'i2', 'content': 'i2[0:2]'})
        self.assertEqual(self.i_s.attributes, {'segmentation': 'i2[2:4]'})
        self.assertEqual(self.i_t.attributes, {'content': 'i2'})

    def test_reference_attributes(self):
        # segmentation cannot co-occur with alignment or content
        self.assertRaises(XigtError, Item, alignment='a1', segmentation='b1')
        self.assertRaises(XigtError, Item, content='a1', segmentation='b1')

        self.assertIs(self.i1.alignment, None)
        self.assertIs(self.i1.content, None)
        self.assertIs(self.i1.segmentation, None)

        self.assertIs(self.i2.alignment, None)
        self.assertIs(self.i2.content, None)
        self.assertIs(self.i2.segmentation, None)

        self.assertEqual(self.i_ac.alignment, 'i2')
        self.assertEqual(self.i_ac.content, 'i2[0:2]')
        self.assertIs(self.i_ac.segmentation, None)

        self.assertIs(self.i_s.alignment, None)
        self.assertIs(self.i_s.content, None)
        self.assertEqual(self.i_s.segmentation, 'i2[2:4]')

        self.assertEqual(self.i_t.alignment, None)
        self.assertEqual(self.i_t.content, 'i2')
        self.assertEqual(self.i_t.segmentation, None)

    def test_text(self):
        self.assertIs(self.i1.text, None)

        self.assertEqual(self.i2.text, 'text')

        self.assertIs(self.i_ac.text, None)
        self.assertIs(self.i_s.text, None)
        self.assertEqual(self.i_t.text, 'something else')

    def test_value(self):
        self.assertIs(self.i1.value(), None)

        self.assertEqual(self.i2.value(), 'text')

        self.assertEqual(self.i_ac.value(), 'te')
        self.assertEqual(self.i_s.value(), 'xt')
        self.assertEqual(self.i_t.value(), 'something else')

    def test_resolve_ref(self):
        # item has no reference attribute
        b1 = Item(id='b1')
        self.assertRaises(KeyError, b1.resolve_ref, 'alignment')
        # has a reference attribute, but is not contained by a tier
        b1.alignment = 'a1'
        self.assertRaises(XigtStructureError, b1.resolve_ref, 'alignment')
        # item in tier, but tier has no reference attribute
        t_b = Tier(id='b', items=[b1])
        self.assertRaises(KeyError, b1.resolve_ref, 'alignment')
        # tier has reference attribute, but is not contained by an Igt
        t_b.alignment = 'a'
        self.assertRaises(XigtStructureError, b1.resolve_ref, 'alignment')
        # item in IGT, but referred tier doesn't exist
        igt = Igt(tiers=[t_b])
        self.assertRaises(XigtStructureError, b1.resolve_ref, 'alignment')
        # referred tier exists, but has no item referred by item's alignment
        t_a = Tier(id='a')
        igt.append(t_a)
        self.assertRaises(XigtStructureError, b1.resolve_ref, 'alignment')
        # referred item exists, but has no value (which resolves to '')
        a1 = Item(id='a1')
        t_a.append(a1)
        self.assertEqual(b1.resolve_ref('alignment'), '')
        # referred item has a value
        a1.text = 'text'
        self.assertEqual(b1.resolve_ref('alignment'), 'text')

        # stored item tests
        self.assertRaises(KeyError, self.i1.resolve_ref, 'alignment')

        self.assertRaises(KeyError, self.i2.resolve_ref, 'alignment')

        self.assertEqual(self.i_ac.resolve_ref('alignment'), 'text')
        self.assertEqual(self.i_ac.resolve_ref('content'), 'te')

        self.assertEqual(self.i_s.resolve_ref('segmentation'), 'xt')

        self.assertEqual(self.i_t.resolve_ref('content'), 'text')

    def test_span(self):
        # sub-spans of null content is also null content
        self.assertIs(self.i1.span(0,1), None)

        self.assertEqual(self.i2.span(0,1), 't')

        self.assertEqual(self.i_ac.span(1,2), 'e')
        self.assertEqual(self.i_s.span(1,2), 't')
        self.assertEqual(self.i_t.span(1,2), 'o')

    def test_get_attribute(self):
        i = Item()
        self.assertEqual(i.get_attribute('attr'), None)
        self.assertEqual(i.get_attribute('attr', 1), 1)
        i.attributes['attr'] = 'val'
        self.assertEqual(i.get_attribute('attr', 1), 'val')
        self.assertEqual(i.get_attribute('abc', inherit=True), None)
        t = Tier(items=[i], attributes={'abc': 'def'})
        self.assertEqual(i.get_attribute('abc', inherit=True), 'def')

        self.assertEqual(self.i1.get_attribute('attr'), None)
        self.assertEqual(self.i1.get_attribute('attr', 1), 1)

        self.assertEqual(self.i2.get_attribute('attr'), 'val')
        self.assertEqual(self.i2.get_attribute('attr', 1), 'val')

        self.assertEqual(self.i_ac.get_attribute('alignment'), 'i2')


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
        self.assertRaises(ValueError, Tier, id='1')  # invalid id
        # don't allow multiple items with the same ID
        self.assertRaises(XigtError, Tier, items=[Item(id='i1'),
                                                  Item(id='i1')])

    def test_id(self):
        self.assertIs(self.t1.id, None)

        self.assertEqual(self.t2.id, 't')

    def test_type(self):
        self.assertIs(self.t1.type, None)

        self.assertEqual(self.t2.type, 'basic')

    def test_parents(self):
        self.assertIs(self.t1.igt, None)
        self.assertIs(self.t1.corpus, None)

        self.assertIs(self.t2.igt, None)
        self.assertIs(self.t2.corpus, None)

    def test_metadata(self):
        self.assertEqual(len(self.t1.metadata), 0)

        self.assertEqual(self.t2.metadata[0].type, 'meta')
        self.assertEqual(len(self.t2.metadata[0].metas), 1)
        self.assertEqual(self.t2.metadata[0][0].text, 'meta')

    def test_attributes(self):
        self.assertEqual(self.t1.attributes, dict())

        self.assertEqual(self.t2.attributes, {'attr':'val'})

    def test_reference_attributes(self):
        # segmentation cannot co-occur with alignment or content
        self.assertRaises(XigtError, Tier, alignment='a1', segmentation='b1')
        self.assertRaises(XigtError, Tier, content='a1', segmentation='b1')

        self.assertIs(self.t1.alignment, None)
        self.assertIs(self.t1.content, None)
        self.assertIs(self.t1.segmentation, None)

        self.assertIs(self.t2.alignment, None)
        self.assertIs(self.t2.content, None)
        self.assertIs(self.t2.segmentation, None)

    def test_items(self):
        self.assertEqual(len(self.t1._list), 0)
        self.assertEqual(self.t1.items, [])

        self.assertEqual(len(self.t2.items), 2)
        # contained Items should now have their tier specified
        for i in self.t2.items:
            self.assertIs(i.tier, self.t2)


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
        self.assertRaises(ValueError, Igt, id='1')  # invalid id
        # don't allow multiple tiers with the same ID
        self.assertRaises(XigtError, Igt, tiers=[Tier(id='a'),
                                                 Tier(id='a')])

    def test_id(self):
        self.assertIs(self.i1.id, None)

        self.assertEqual(self.i2.id, 'i1')

    def test_type(self):
        self.assertIs(self.i1.type, None)

        self.assertEqual(self.i2.type, 'basic')

    def test_parents(self):
        self.assertIs(self.i1.corpus, None)

        self.assertIs(self.i2.corpus, None)

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
            self.assertIs(t.igt, self.i2)


class TestXigtCorpus(unittest.TestCase):

    def test_init(self):
        self.assertRaises(ValueError, XigtCorpus, id='1')  # invalid id

    def test_empty(self):
        c = XigtCorpus()
        self.assertIs(c.id, None)
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
            self.assertIs(i.corpus, c)
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
        self.assertIs(t.get('a3'), None)
        self.assertEqual(t.get('a3', 'z'), 'z')
        self.assertIs(t.get(2), None)
        self.assertEqual(t.get(2, 'z'), 'z')
