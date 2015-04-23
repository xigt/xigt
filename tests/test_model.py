import unittest
from xigt import XigtCorpus, Igt, Tier, Item, Metadata, Meta, MetaChild
from xigt.errors import XigtError, XigtStructureError

class TestMetadata(unittest.TestCase):

    def setUp(self):
        self.md1 = Metadata()

        self.md2 = Metadata(
            id='md2',
            type='basic',
            attributes={'attr':'val'},
            metas=[Meta(id='meta1', text='meta')]
        )

    def test_init(self):
        self.assertRaises(ValueError, Metadata, id='1')  # invalid id

    def test_id(self):
        self.assertIs(self.md1.id, None)

        self.assertIs(self.md2.id, 'md2')

    def test_type(self):
        self.assertIs(self.md1.type, None)

        self.assertEqual(self.md2.type, 'basic')

    def test_metas(self):
        self.assertEqual(self.md1.metas, [])

        self.assertEqual(len(self.md2.metas), 1)
        self.assertEqual(self.md2[0].text, 'meta')

    def test_attributes(self):
        self.assertEqual(self.md1.attributes, dict())

        self.assertEqual(self.md2.attributes, {'attr':'val'})

    def test_get(self):
        self.assertIs(self.md1.get(0), None)
        self.assertIs(self.md1.get('meta1'), None)
        self.assertEqual(self.md1.get('meta1', default=1), 1)

        self.assertEqual(self.md2.get(0).id, 'meta1')
        self.assertIs(self.md2.get(1), None)
        self.assertEqual(self.md2.get('meta1').id, 'meta1')
        self.assertEqual(
            self.md2.get('meta1', default=Meta(id='meta2')).id, 'meta1'
        )

    def test_append(self):
        md = Metadata()
        self.assertRaises(XigtStructureError, md.append, Item())
        self.assertRaises(XigtStructureError, md.append, Tier())
        self.assertRaises(XigtStructureError, md.append, Igt())
        self.assertRaises(XigtStructureError, md.append, XigtCorpus())
        self.assertRaises(XigtStructureError, md.append, Metadata())
        self.assertEqual(len(md), 0)
        md.append(Meta(id='meta1'))
        self.assertEqual(len(md), 1)
        self.assertRaises(XigtError, md.append, Meta(id='meta1'))
        md.append(Meta(id='meta2'))
        self.assertEqual(len(md), 2)
        self.assertEqual(md[0].id, 'meta1')
        self.assertEqual(md[1].id, 'meta2')

    def test_insert(self):
        md = Metadata()
        self.assertEqual(len(md), 0)
        md.insert(0, Meta(id='meta1'))
        self.assertEqual(len(md), 1)
        self.assertRaises(XigtError, md.insert, 0, Meta(id='meta1'))
        md.insert(0, Meta(id='meta2'))
        md.insert(100, Meta(id='meta3'))
        self.assertEqual(len(md), 3)
        self.assertEqual(md[0].id, 'meta2')
        self.assertEqual(md[1].id, 'meta1')
        self.assertEqual(md[2].id, 'meta3')

    def test_extend(self):
        md = Metadata()
        self.assertEqual(len(md), 0)
        md.extend([Meta(id='meta1')])
        self.assertEqual(len(md), 1)
        md.extend([])
        self.assertEqual(len(md), 1)
        md.extend([Meta(id='meta2'), Meta(id='meta3')])
        self.assertEqual(len(md), 3)
        self.assertEqual(md[0].id, 'meta1')
        self.assertEqual(md[1].id, 'meta2')
        self.assertEqual(md[2].id, 'meta3')

    def test_clear(self):
        md = Metadata()
        md.extend([Meta(id='meta1'), Meta(id='meta2'), Meta(id='meta3')])
        self.assertEqual(len(md), 3)
        md.clear()
        self.assertEqual(len(md), 0)
        self.assertIs(md.get(0), None)
        self.assertIs(md.get('meta1'), None)

    def test_get_attribute(self):
        md = Metadata(
            attributes={'one': 1, 'two': 2, '{http://namespace.org}three': 4},
            nsmap={'pre': 'http://namespace.org'}
        )
        igt = Igt(metadata=[md], attributes={'three': 3})
        self.assertEqual(md.get_attribute('one'), 1)
        self.assertEqual(md.get_attribute('two'), 2)
        self.assertIs(md.get_attribute('three'), None)
        self.assertEqual(
            md.get_attribute('three', namespace='http://namespace.org'), 4
        )
        self.assertEqual(
            md.get_attribute('three', namespace='pre'), 4
        )
        self.assertEqual(md.get_attribute('three', inherit=True), 3)
        self.assertEqual(
            md.get_attribute('three', namespace='pre', inherit=True), 4
        )
        self.assertEqual(md.get_attribute('three', default=5), 5)


class TestMeta(unittest.TestCase):

    def setUp(self):
        self.m1 = Meta()

        self.m2 = Meta(
            id='meta1',
            type='metatype',
            attributes={'one': 1},
            text='metatext',
            children=[MetaChild('child1'), MetaChild('child2')]
        )

    def test_init(self):
        self.assertRaises(ValueError, Meta, id='1')  # invalid id

    def test_id(self):
        self.assertIs(self.m1.id, None)

        self.assertEqual(self.m2.id, 'meta1')

    def test_type(self):
        self.assertIs(self.m1.type, None)

        self.assertEqual(self.m2.type, 'metatype')

    def test_attributes(self):
        self.assertEqual(self.m1.attributes, dict())

        self.assertEqual(self.m2.attributes, {'one': 1})

    def test_get_attribute(self):
        self.assertIs(self.m1.get_attribute('attr'), None)
        self.assertEqual(self.m1.get_attribute('attr', 1), 1)

        self.assertEqual(self.m2.get_attribute('one'), 1)
        self.assertIs(self.m2.get_attribute('two'), None)

        m = Meta(attributes={'one': 1})
        md = Metadata(
            attributes={'two': 2},
            metas=[m]
        )
        self.assertEqual(m.get_attribute('two', inherit=True), 2)

    def test_text(self):
        self.assertIs(self.m1.text, None)

        self.assertEqual(self.m2.text, 'metatext')

    def test_children(self):
        self.assertEqual(self.m1.children, [])

        self.assertEqual(len(self.m2.children), 2)
        self.assertEqual(self.m2.children[0].name, 'child1')
        self.assertEqual(self.m2.children[1].name, 'child2')


class TestMetaChild(unittest.TestCase):

    def setUp(self):
        self.mc1 = MetaChild('childname')

        self.mc2 = MetaChild(
            'childname',
            attributes={'id': 'mc2', 'type': 'childtype', 'one': 1},
            text='childtext',
            children=[MetaChild('grandchild1'), MetaChild('grandchild2')]
        )

    def test_init(self):
        # name (i.e. tag in XML) is mandatory
        self.assertRaises(TypeError, MetaChild)
        # invalid names
        self.assertRaises(ValueError, MetaChild, '1')
        self.assertRaises(ValueError, MetaChild, 'a:1')
        # id and type not allowed as parameters (they can be attributes)
        self.assertRaises(TypeError, MetaChild, 'mc0', id='mc1')
        self.assertRaises(TypeError, MetaChild, 'mc0', type='childtype')

    def test_name(self):
        self.assertEqual(self.mc1.name, 'childname')

        self.assertEqual(self.mc2.name, 'childname')

    def test_attributes(self):
        self.assertEqual(self.mc1.attributes, dict())

        self.assertEqual(self.mc2.attributes,
                         {'id': 'mc2', 'type': 'childtype', 'one': 1})

    def test_get_attribute(self):
        self.assertIs(self.mc1.get_attribute('id'), None)
        self.assertIs(self.mc1.get_attribute('attr'), None)
        self.assertEqual(self.mc1.get_attribute('attr', 1), 1)

        self.assertEqual(self.mc2.get_attribute('id'), 'mc2')
        self.assertEqual(self.mc2.get_attribute('type'), 'childtype')
        self.assertEqual(self.mc2.get_attribute('one'), 1)
        self.assertIs(self.mc2.get_attribute('two'), None)

        mc = MetaChild('childname', attributes={'one': 1})
        m = Meta(children=[mc])
        md = Metadata(
            attributes={'two': 2},
            metas=[m]
        )
        self.assertEqual(mc.get_attribute('two', inherit=True), 2)

    def test_text(self):
        self.assertIs(self.mc1.text, None)

        self.assertEqual(self.mc2.text, 'childtext')

    def test_children(self):
        self.assertEqual(self.mc1.children, [])

        self.assertEqual(len(self.mc2.children), 2)
        self.assertEqual(self.mc2.children[0].name, 'grandchild1')
        self.assertEqual(self.mc2.children[1].name, 'grandchild2')


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
        i = Item(id='i1')
        self.assertEqual(i.get_attribute('attr'), None)
        self.assertEqual(i.get_attribute('attr', 1), 1)
        i.attributes['attr'] = 'val'
        self.assertEqual(i.get_attribute('attr', 1), 'val')
        self.assertEqual(i.get_attribute('abc', inherit=True), None)
        t = Tier(id='t', items=[i], attributes={'abc': 'def'})
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
            items=[Item(id='t1'), Item(id='t2')]
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

    def test_items(self):
        self.assertEqual(len(self.t1._list), 0)
        self.assertEqual(self.t1.items, [])

        self.assertEqual(len(self.t2.items), 2)
        # contained Items should now have their tier specified
        for i in self.t2.items:
            self.assertIs(i.tier, self.t2)

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

    def test_get(self):
        self.assertIs(self.t1.get(0), None)
        self.assertIs(self.t1.get('t'), None)
        self.assertEqual(self.t1.get('t', default=1), 1)

        self.assertEqual(self.t2.get(0).id, 't1')
        self.assertIs(self.t2.get(2), None)
        self.assertEqual(self.t2.get('t1').id, 't1')
        self.assertEqual(
            self.t2.get('t1', default=Item(id='x')).id, 't1'
        )

    def test_append(self):
        t = Tier()
        self.assertRaises(XigtStructureError, t.append, Tier())
        self.assertRaises(XigtStructureError, t.append, Igt())
        self.assertRaises(XigtStructureError, t.append, XigtCorpus())
        self.assertRaises(XigtStructureError, t.append, Metadata())
        self.assertRaises(XigtStructureError, t.append, Meta())
        self.assertEqual(len(t), 0)
        t.append(Item(id='t1'))
        self.assertEqual(len(t), 1)
        self.assertRaises(XigtError, t.append, Item(id='t1'))
        t.append(Item(id='t2'))
        self.assertEqual(len(t), 2)
        self.assertEqual(t[0].id, 't1')
        self.assertEqual(t[1].id, 't2')

    def test_insert(self):
        t = Tier()
        self.assertEqual(len(t), 0)
        t.insert(0, Item(id='t1'))
        self.assertEqual(len(t), 1)
        self.assertRaises(XigtError, t.insert, 0, Item(id='t1'))
        t.insert(0, Item(id='t2'))
        t.insert(100, Item(id='t3'))
        self.assertEqual(len(t), 3)
        self.assertEqual(t[0].id, 't2')
        self.assertEqual(t[1].id, 't1')
        self.assertEqual(t[2].id, 't3')

    def test_extend(self):
        t = Tier()
        self.assertEqual(len(t), 0)
        t.extend([Item(id='t1')])
        self.assertEqual(len(t), 1)
        t.extend([])
        self.assertEqual(len(t), 1)
        t.extend([Item(id='t2'), Item(id='t3')])
        self.assertEqual(len(t), 3)
        self.assertEqual(t[0].id, 't1')
        self.assertEqual(t[1].id, 't2')
        self.assertEqual(t[2].id, 't3')

    def test_clear(self):
        t = Tier()
        t.extend([Item(id='t1'), Item(id='t2'), Item(id='t3')])
        self.assertEqual(len(t), 3)
        t.clear()
        self.assertEqual(len(t), 0)
        self.assertIs(t.get(0), None)
        self.assertIs(t.get('t1'), None)

    def test_get_attribute(self):
        t = Tier(id='t', attributes={'one': 1, 'two': 2})
        igt = Igt(tiers=[t], attributes={'three': 3})
        self.assertEqual(t.get_attribute('one'), 1)
        self.assertEqual(t.get_attribute('two'), 2)
        self.assertIs(t.get_attribute('three'), None)
        self.assertEqual(t.get_attribute('three', inherit=True), 3)
        self.assertEqual(t.get_attribute('three', default=4), 4)


class TestIgt(unittest.TestCase):
    def setUp(self):
        self.i1 = Igt()

        self.i2 = Igt(
            id='i1',
            type='basic',
            attributes={'attr':'val'},
            metadata=[Metadata(type='meta',
                               metas=[Meta(text='meta')])],
            tiers=[Tier(id='a', items=[Item(id='a1'), Item(id='a2')]),
                   Tier(id='b', items=[Item(id='b1'), Item(id='b2')])]
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

    def test_tiers(self):
        self.assertEqual(len(self.i1.tiers), 0)

        self.assertEqual(len(self.i2.tiers), 2)
        # contained Tiers should now have their igt specified
        for t in self.i2.tiers:
            self.assertIs(t.igt, self.i2)

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

    def test_get(self):
        self.assertIs(self.i1.get(0), None)
        self.assertIs(self.i1.get('t'), None)
        self.assertEqual(self.i1.get('t', default=1), 1)

        self.assertEqual(self.i2.get(0).id, 'a')
        self.assertIs(self.i2.get(3), None)
        self.assertEqual(self.i2.get('a').id, 'a')
        self.assertEqual(
            self.i2.get('a', default=Tier(id='x')).id, 'a'
        )

    def test_get_item(self):
        self.assertIs(self.i1.get_item('a'), None)
        self.assertIs(self.i1.get_item('a1'), None)

        self.assertIs(self.i2.get_item('a'), None)
        self.assertEqual(self.i2.get_item('a1').id, 'a1')
        self.assertEqual(self.i2.get_item('b2').id, 'b2')

    def test_get_any(self):
        self.assertIs(self.i1.get_any('a'), None)
        self.assertIs(self.i1.get_any('a1'), None)

        self.assertIs(self.i2.get_any('a').id, 'a')
        self.assertEqual(self.i2.get_any('a1').id, 'a1')
        self.assertEqual(self.i2.get_any('b2').id, 'b2')

    def test_append(self):
        igt = Igt()
        self.assertRaises(XigtStructureError, igt.append, Item())
        self.assertRaises(XigtStructureError, igt.append, Igt())
        self.assertRaises(XigtStructureError, igt.append, XigtCorpus())
        self.assertRaises(XigtStructureError, igt.append, Metadata())
        self.assertRaises(XigtStructureError, igt.append, Meta())
        self.assertEqual(len(igt), 0)
        igt.append(Tier(id='t'))
        self.assertEqual(len(igt), 1)
        self.assertRaises(XigtError, igt.append, Tier(id='t'))
        igt.append(Tier(id='x'))
        self.assertEqual(len(igt), 2)
        self.assertEqual(igt[0].id, 't')
        self.assertEqual(igt[1].id, 'x')

    def test_insert(self):
        igt = Igt()
        self.assertEqual(len(igt), 0)
        igt.insert(0, Tier(id='t'))
        self.assertEqual(len(igt), 1)
        self.assertRaises(XigtError, igt.insert, 0, Tier(id='t'))
        igt.insert(0, Tier(id='x'))
        igt.insert(100, Tier(id='y'))
        self.assertEqual(len(igt), 3)
        self.assertEqual(igt[0].id, 'x')
        self.assertEqual(igt[1].id, 't')
        self.assertEqual(igt[2].id, 'y')

    def test_extend(self):
        igt = Igt()
        self.assertEqual(len(igt), 0)
        igt.extend([Tier(id='t')])
        self.assertEqual(len(igt), 1)
        igt.extend([])
        self.assertEqual(len(igt), 1)
        igt.extend([Tier(id='x'), Tier(id='y')])
        self.assertEqual(len(igt), 3)
        self.assertEqual(igt[0].id, 't')
        self.assertEqual(igt[1].id, 'x')
        self.assertEqual(igt[2].id, 'y')

    def test_clear(self):
        igt = Igt()
        igt.extend([Tier(id='t'), Tier(id='x'), Tier(id='y')])
        self.assertEqual(len(igt), 3)
        igt.clear()
        self.assertEqual(len(igt), 0)
        self.assertIs(igt.get(0), None)
        self.assertIs(igt.get('t'), None)

    def test_get_attribute(self):
        igt = Igt(id='i1', attributes={'one': 1, 'two': 2})
        xc = XigtCorpus(igts=[igt], attributes={'three': 3})
        self.assertEqual(igt.get_attribute('one'), 1)
        self.assertEqual(igt.get_attribute('two'), 2)
        self.assertIs(igt.get_attribute('three'), None)
        self.assertEqual(igt.get_attribute('three', inherit=True), 3)
        self.assertEqual(igt.get_attribute('three', default=4), 4)


class TestXigtCorpus(unittest.TestCase):

    def setUp(self):
        self.c1 = XigtCorpus()

        self.c2 = XigtCorpus(
            id='xc1',
            type='basic',
            attributes={'attr':'val'},
            metadata=[Metadata(type='meta', metas=[Meta(text='meta')])],
            igts=[Igt(id='i1'), Igt(id='i2')]
        )

    def test_init(self):
        self.assertRaises(ValueError, XigtCorpus, id='1')  # invalid id

        # don't allow multiple igts with the same ID
        self.assertRaises(XigtError, XigtCorpus, igts=[Igt(id='i1'),
                                                       Igt(id='i1')])

    def test_id(self):
        self.assertIs(self.c1.id, None)

        self.assertEqual(self.c2.id, 'xc1')

    def test_type(self):
        self.assertIs(self.c1.type, None)

        self.assertIs(self.c2.type, 'basic')

    def test_igts(self):
        self.assertEqual(len(self.c1.igts), 0)

        self.assertEqual(len(self.c2.igts), 2)
        # contained Igts should now have their corpus specified
        for i in self.c2.igts:
            self.assertIs(i.corpus, self.c2)

    def test_attributes(self):
        self.assertEqual(self.c1.attributes, dict())

        self.assertEqual(self.c2.attributes, {'attr':'val'})

    def test_metadata(self):
        self.assertEqual(len(self.c1.metadata), 0)

        self.assertEqual(self.c2.metadata[0].type, 'meta')
        self.assertEqual(len(self.c2.metadata[0].metas), 1)
        self.assertEqual(self.c2.metadata[0][0].text, 'meta')

    def test_get(self):
        self.assertIs(self.c1.get(0), None)
        self.assertIs(self.c1.get('i1'), None)
        self.assertEqual(self.c1.get('i1', default=1), 1)

        self.assertEqual(self.c2.get(0).id, 'i1')
        self.assertIs(self.c2.get(3), None)
        self.assertEqual(self.c2.get('i1').id, 'i1')
        self.assertEqual(
            self.c2.get('i1', default=Igt(id='i3')).id, 'i1'
        )

    def test_append(self):
        xc = XigtCorpus()
        self.assertRaises(XigtStructureError, xc.append, Item())
        self.assertRaises(XigtStructureError, xc.append, Tier())
        self.assertRaises(XigtStructureError, xc.append, XigtCorpus())
        self.assertRaises(XigtStructureError, xc.append, Metadata())
        self.assertRaises(XigtStructureError, xc.append, Meta())
        self.assertEqual(len(xc), 0)
        xc.append(Igt(id='i1'))
        self.assertEqual(len(xc), 1)
        self.assertRaises(XigtError, xc.append, Igt(id='i1'))
        xc.append(Igt(id='i2'))
        self.assertEqual(len(xc), 2)
        self.assertEqual(xc[0].id, 'i1')
        self.assertEqual(xc[1].id, 'i2')

    def test_insert(self):
        xc = XigtCorpus()
        self.assertEqual(len(xc), 0)
        xc.insert(0, Igt(id='i1'))
        self.assertEqual(len(xc), 1)
        self.assertRaises(XigtError, xc.insert, 0, Igt(id='i1'))
        xc.insert(0, Igt(id='i2'))
        xc.insert(100, Igt(id='i3'))
        self.assertEqual(len(xc), 3)
        self.assertEqual(xc[0].id, 'i2')
        self.assertEqual(xc[1].id, 'i1')
        self.assertEqual(xc[2].id, 'i3')

    def test_extend(self):
        xc = XigtCorpus()
        self.assertEqual(len(xc), 0)
        xc.extend([Igt(id='i1')])
        self.assertEqual(len(xc), 1)
        xc.extend([])
        self.assertEqual(len(xc), 1)
        xc.extend([Igt(id='i2'), Igt(id='i3')])
        self.assertEqual(len(xc), 3)
        self.assertEqual(xc[0].id, 'i1')
        self.assertEqual(xc[1].id, 'i2')
        self.assertEqual(xc[2].id, 'i3')

    def test_clear(self):
        xc = XigtCorpus()
        xc.extend([Igt(id='i1'), Igt(id='i2'), Igt(id='i3')])
        self.assertEqual(len(xc), 3)
        xc.clear()
        self.assertEqual(len(xc), 0)
        self.assertIs(xc.get(0), None)
        self.assertIs(xc.get('i1'), None)

    def test_get_attribute(self):
        xc = XigtCorpus(attributes={'one': 1, 'two': 2})
        self.assertEqual(xc.get_attribute('one'), 1)
        self.assertEqual(xc.get_attribute('two'), 2)
        self.assertIs(xc.get_attribute('three'), None)
        self.assertEqual(xc.get_attribute('three', inherit=True), None)
