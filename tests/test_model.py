import pytest

from xigt import XigtCorpus, Igt, Tier, Item, Metadata, Meta, MetaChild
from xigt.errors import XigtError, XigtStructureError

class TestMetadata():

    md1 = Metadata()

    m1 = Meta(id='meta1', text='meta')
    md2 = Metadata(
        id='md2',
        type='basic',
        attributes={'attr':'val'},
        metas=[m1]
    )

    def test_init(self):
        with pytest.raises(ValueError): Metadata(id='1')  # invalid id

    def test_id(self):
        assert self.md1.id is None

        assert self.md2.id is 'md2'

    def test_type(self):
        assert self.md1.type is None

        assert self.md2.type == 'basic'

    def test_metas(self):
        assert self.md1.metas == []

        assert len(self.md2.metas) == 1
        assert self.md2[0].text == 'meta'

    def test_attributes(self):
        assert self.md1.attributes == dict()

        assert self.md2.attributes == {'attr':'val'}

    def test_eq(self):
        assert self.md1 == self.md1
        assert self.md2 == self.md2
        assert self.md1 != self.md2

    def test_getitem(self):
        assert self.md2[0] == self.m1
        assert self.md2['meta1'] == self.m1
        assert self.md2['0'] == self.m1
        with pytest.raises(IndexError): self.md2[1]
        with pytest.raises(IndexError): self.md2['1']
        with pytest.raises(KeyError): self.md2['m2']

    def test_setitem(self):
        md = Metadata(metas=[Meta(id='meta1'), Meta(id='meta2')])
        md[0] = Meta(id='meta3')
        assert len(md) == 2
        assert md[0].id == 'meta3'
        with pytest.raises(KeyError): md['meta1']
        with pytest.raises(ValueError): md['meta2'] = Meta(id='meta2')

    def test_delitem(self):
        md = Metadata(metas=[Meta(id='meta1'), Meta(id='meta2')])
        assert len(md) == 2
        del md[0]
        assert len(md) == 1
        assert md[0].id == 'meta2'
        with pytest.raises(KeyError): md['meta1']
        del md['meta2']
        assert len(md) == 0
        with pytest.raises(KeyError): md['meta2']

    def test_get(self):
        assert self.md1.get(0) is None
        assert self.md1.get('meta1') is None
        assert self.md1.get('meta1', default=1) == 1

        assert self.md2.get(0).id == 'meta1'
        assert self.md2.get(1) is None
        assert self.md2.get('meta1').id == 'meta1'
        assert self.md2.get('meta1', default=Meta(id='meta2')).id == 'meta1'

    def test_append(self):
        md = Metadata()
        with pytest.raises(XigtStructureError): md.append(Item())
        with pytest.raises(XigtStructureError): md.append(Tier())
        with pytest.raises(XigtStructureError): md.append(Igt())
        with pytest.raises(XigtStructureError): md.append(XigtCorpus())
        with pytest.raises(XigtStructureError): md.append(Metadata())
        assert len(md) == 0
        md.append(Meta(id='meta1'))
        assert len(md) == 1
        with pytest.raises(XigtError): md.append(Meta(id='meta1'))
        md.append(Meta(id='meta2'))
        assert len(md) == 2
        assert md[0].id == 'meta1'
        assert md[1].id == 'meta2'

    def test_insert(self):
        md = Metadata()
        assert len(md) == 0
        md.insert(0, Meta(id='meta1'))
        assert len(md) == 1
        with pytest.raises(XigtError): md.insert(0, Meta(id='meta1'))
        md.insert(0, Meta(id='meta2'))
        md.insert(100, Meta(id='meta3'))
        assert len(md) == 3
        assert md[0].id == 'meta2'
        assert md[1].id == 'meta1'
        assert md[2].id == 'meta3'

    def test_extend(self):
        md = Metadata()
        assert len(md) == 0
        md.extend([Meta(id='meta1')])
        assert len(md) == 1
        md.extend([])
        assert len(md) == 1
        md.extend([Meta(id='meta2'), Meta(id='meta3')])
        assert len(md) == 3
        assert md[0].id == 'meta1'
        assert md[1].id == 'meta2'
        assert md[2].id == 'meta3'

    def test_remove(self):
        md = Metadata(metas=[Meta(id='m1'), Meta(id='m2')])
        assert len(md) == 2
        md.remove(md[0])
        assert len(md) == 1
        assert md[0].id == 'm2'
        with pytest.raises(KeyError): md['m1']

    def test_clear(self):
        md = Metadata()
        md.extend([Meta(id='meta1'), Meta(id='meta2'), Meta(id='meta3')])
        assert len(md) == 3
        md.clear()
        assert len(md) == 0
        assert md.get(0) is None
        assert md.get('meta1') is None

    def test_get_attribute(self):
        md = Metadata(
            attributes={'one': 1, 'two': 2, '{http://namespace.org}three': 4},
            nsmap={'pre': 'http://namespace.org'}
        )
        igt = Igt(metadata=[md], attributes={'three': 3})
        assert md.get_attribute('one') == 1
        assert md.get_attribute('two') == 2
        assert md.get_attribute('three') is None
        assert md.get_attribute('three', namespace='http://namespace.org') == 4
        assert md.get_attribute('three', namespace='pre') == 4
        assert md.get_attribute('three', inherit=True) == 3
        assert md.get_attribute('three', namespace='pre', inherit=True) == 4
        assert md.get_attribute('three', default=5) == 5


class TestMeta():

    m1 = Meta()

    m2 = Meta(
        id='meta1',
        type='metatype',
        attributes={'one': 1},
        text='metatext',
        children=[MetaChild('child1'), MetaChild('child2')]
    )

    def test_init(self):
        with pytest.raises(ValueError): Meta(id='1')  # invalid id

    def test_id(self):
        assert self.m1.id is None

        assert self.m2.id == 'meta1'

    def test_type(self):
        assert self.m1.type is None

        assert self.m2.type == 'metatype'

    def test_attributes(self):
        assert self.m1.attributes == dict()

        assert self.m2.attributes == {'one': 1}

    def test_get_attribute(self):
        assert self.m1.get_attribute('attr') is None
        assert self.m1.get_attribute('attr', 1) == 1

        assert self.m2.get_attribute('one') == 1
        assert self.m2.get_attribute('two') is None

        m = Meta(attributes={'one': 1})
        md = Metadata(
            attributes={'two': 2},
            metas=[m]
        )
        assert m.get_attribute('two', inherit=True) == 2

    def test_eq(self):
        assert self.m1 == self.m1
        assert self.m2 == self.m2
        assert self.m1 != self.m2

    def test_text(self):
        assert self.m1.text is None

        assert self.m2.text == 'metatext'

    def test_children(self):
        assert self.m1.children == []

        assert len(self.m2.children) == 2
        assert self.m2.children[0].name == 'child1'
        assert self.m2.children[1].name == 'child2'


class TestMetaChild():

    mc1 = MetaChild('childname')

    mc2 = MetaChild(
        'childname',
        attributes={'id': 'mc2', 'type': 'childtype', 'one': 1},
        text='childtext',
        children=[MetaChild('grandchild1'), MetaChild('grandchild2')]
    )

    def test_init(self):
        # name (i.e. tag in XML) is mandatory
        with pytest.raises(TypeError): MetaChild()
        # invalid names
        with pytest.raises(ValueError): MetaChild('1')
        with pytest.raises(ValueError): MetaChild('a:1')
        # id and type not allowed as parameters (they can be attributes)
        with pytest.raises(TypeError): MetaChild('mc0', id='mc1')
        with pytest.raises(TypeError): MetaChild('mc0', type='childtype')

    def test_name(self):
        assert self.mc1.name == 'childname'

        assert self.mc2.name == 'childname'

    def test_attributes(self):
        assert self.mc1.attributes == dict()

        assert self.mc2.attributes == {'id': 'mc2', 'type': 'childtype', 'one': 1}

    def test_get_attribute(self):
        assert self.mc1.get_attribute('id') is None
        assert self.mc1.get_attribute('attr') is None
        assert self.mc1.get_attribute('attr', 1) == 1

        assert self.mc2.get_attribute('id') == 'mc2'
        assert self.mc2.get_attribute('type') == 'childtype'
        assert self.mc2.get_attribute('one') == 1
        assert self.mc2.get_attribute('two') is None

        mc = MetaChild('childname', attributes={'one': 1})
        m = Meta(children=[mc])
        md = Metadata(
            attributes={'two': 2},
            metas=[m]
        )
        assert mc.get_attribute('two', inherit=True) == 2

    def test_eq(self):
        assert self.mc1 == self.mc1
        assert self.mc2 == self.mc2
        assert self.mc1 != self.mc2

    def test_text(self):
        assert self.mc1.text is None

        assert self.mc2.text == 'childtext'

    def test_children(self):
        assert self.mc1.children == []

        assert len(self.mc2.children) == 2
        assert self.mc2.children[0].name == 'grandchild1'
        assert self.mc2.children[1].name == 'grandchild2'


class TestItem():
    # empty
    i1 = Item()

    # basic info
    i2 = Item(
        id='i2',
        type='basic',
        attributes={'attr':'val'},
        text='text'
    )

    # alignment and content refs
    i_ac = Item(
        id='i_ac',
        alignment='i2',
        content='i2[0:2]'
    )

    # segmentation ref
    i_s = Item(
        id='i_s',
        segmentation='i2[2:4]'
    )

    # override content ref with text
    i_t = Item(
        id='i_t',
        content='i2',
        text='something else'
    )

    # contextual structure
    t_a = Tier(id='t_a', items=[i2])
    t_b = Tier(id='t_b', items=[i_ac, i_t],
                    alignment='t_a', content='t_a')
    t_c = Tier(id='t_c', items=[i_s], segmentation='t_a')
    igt = Igt(tiers=[t_a, t_b, t_c])
    xc = XigtCorpus(igts=[igt])


    def test_init(self):
        with pytest.raises(ValueError): Item(id='1')  # invalid id

    def test_id(self):
        assert self.i1.id is None

        assert self.i2.id == 'i2'

        assert self.i_ac.id == 'i_ac'
        assert self.i_s.id == 'i_s'
        assert self.i_t.id == 'i_t'

    def test_type(self):
        assert self.i1.type is None

        assert self.i2.type == 'basic'

        assert self.i_ac.type is None
        assert self.i_s.type is None
        assert self.i_t.type is None

    def test_parents(self):
        assert self.i1.tier is None
        assert self.i1.igt is None
        assert self.i1.corpus is None

        assert self.i2.tier is self.t_a
        assert self.i2.igt is self.igt
        assert self.i2.corpus is self.xc

        assert self.i_ac.tier == self.t_b
        assert self.i_ac.igt == self.igt
        assert self.i_ac.corpus == self.xc

        assert self.i_s.tier == self.t_c
        assert self.i_s.igt == self.igt
        assert self.i_s.corpus == self.xc

        assert self.i_t.tier == self.t_b
        assert self.i_t.igt == self.igt
        assert self.i_t.corpus == self.xc

    def test_eq(self):
        assert self.i1 == self.i1
        assert self.i2 == self.i2
        assert self.i1 != self.i2

    def test_attributes(self):
        assert self.i1.attributes == dict()

        assert self.i2.attributes == {'attr':'val'}

        assert self.i_ac.attributes == {'alignment': 'i2', 'content': 'i2[0:2]'}
        assert self.i_s.attributes == {'segmentation': 'i2[2:4]'}
        assert self.i_t.attributes == {'content': 'i2'}

    def test_reference_attributes(self):
        # segmentation cannot co-occur with alignment or content
        with pytest.raises(XigtError): Item(alignment='a1', segmentation='b1')
        with pytest.raises(XigtError): Item(content='a1', segmentation='b1')

        assert self.i1.alignment is None
        assert self.i1.content is None
        assert self.i1.segmentation is None

        assert self.i2.alignment is None
        assert self.i2.content is None
        assert self.i2.segmentation is None

        assert self.i_ac.alignment == 'i2'
        assert self.i_ac.content == 'i2[0:2]'
        assert self.i_ac.segmentation is None

        assert self.i_s.alignment is None
        assert self.i_s.content is None
        assert self.i_s.segmentation == 'i2[2:4]'

        assert self.i_t.alignment == None
        assert self.i_t.content == 'i2'
        assert self.i_t.segmentation == None

    def test_text(self):
        assert self.i1.text is None

        assert self.i2.text == 'text'

        assert self.i_ac.text is None
        assert self.i_s.text is None
        assert self.i_t.text == 'something else'

    def test_value(self):
        assert self.i1.value() is None

        assert self.i2.value() == 'text'

        assert self.i_ac.value() == 'te'
        assert self.i_s.value() == 'xt'
        assert self.i_t.value() == 'something else'

    def test_resolve_ref(self):
        # item has no reference attribute
        b1 = Item(id='b1')
        with pytest.raises(KeyError): b1.resolve_ref('alignment')
        # has a reference attribute, but is not contained by a tier
        b1.alignment = 'a1'
        with pytest.raises(XigtStructureError): b1.resolve_ref('alignment')
        # item in tier, but tier has no reference attribute
        t_b = Tier(id='b', items=[b1])
        with pytest.raises(KeyError): b1.resolve_ref('alignment')
        # tier has reference attribute, but is not contained by an Igt
        t_b.alignment = 'a'
        with pytest.raises(XigtStructureError): b1.resolve_ref('alignment')
        # item in IGT, but referred tier doesn't exist
        igt = Igt(tiers=[t_b])
        with pytest.raises(XigtStructureError): b1.resolve_ref('alignment')
        # referred tier exists, but has no item referred by item's alignment
        t_a = Tier(id='a')
        igt.append(t_a)
        with pytest.raises(XigtStructureError): b1.resolve_ref('alignment')
        # referred item exists, but has no value (which resolves to '')
        a1 = Item(id='a1')
        t_a.append(a1)
        assert b1.resolve_ref('alignment') == ''
        # referred item has a value
        a1.text = 'text'
        assert b1.resolve_ref('alignment') == 'text'

        # stored item tests
        with pytest.raises(KeyError): self.i1.resolve_ref('alignment')

        with pytest.raises(KeyError): self.i2.resolve_ref('alignment')

        assert self.i_ac.resolve_ref('alignment') == 'text'
        assert self.i_ac.resolve_ref('content') == 'te'

        assert self.i_s.resolve_ref('segmentation') == 'xt'

        assert self.i_t.resolve_ref('content') == 'text'

    def test_span(self):
        # sub-spans of null content is also null content
        assert self.i1.span(0,1) is None

        assert self.i2.span(0,1) == 't'

        assert self.i_ac.span(1,2) == 'e'
        assert self.i_s.span(1,2) == 't'
        assert self.i_t.span(1,2) == 'o'

    def test_get_attribute(self):
        i = Item(id='i1')
        assert i.get_attribute('attr') == None
        assert i.get_attribute('attr', 1) == 1
        i.attributes['attr'] = 'val'
        assert i.get_attribute('attr', 1) == 'val'
        assert i.get_attribute('abc', inherit=True) == None
        t = Tier(id='t', items=[i], attributes={'abc': 'def'})
        assert i.get_attribute('abc', inherit=True) == 'def'

        assert self.i1.get_attribute('attr') == None
        assert self.i1.get_attribute('attr', 1) == 1

        assert self.i2.get_attribute('attr') == 'val'
        assert self.i2.get_attribute('attr', 1) == 'val'

        assert self.i_ac.get_attribute('alignment') == 'i2'


class TestTier():
    t1 = Tier()

    i1 = Item(id='t1')
    i2 = Item(id='t2')
    t2 = Tier(
        id='t',
        type='basic',
        attributes={'attr':'val'},
        metadata=[Metadata(type='meta', metas=[Meta(text='meta')])],
        items=[i1, i2]
    )

    def test_init(self):
        with pytest.raises(ValueError): Tier(id='1')  # invalid id
        # don't allow multiple items with the same ID
        with pytest.raises(XigtError): Tier(items=[Item(id='i1'),
                                                   Item(id='i1')])

    def test_id(self):
        assert self.t1.id is None

        assert self.t2.id == 't'

    def test_type(self):
        assert self.t1.type is None

        assert self.t2.type == 'basic'

    def test_items(self):
        assert len(self.t1.items) == 0
        assert self.t1.items == []

        assert len(self.t2.items) == 2
        # contained Items should now have their tier specified
        for i in self.t2.items:
            assert i.tier is self.t2

    def test_parents(self):
        assert self.t1.igt is None
        assert self.t1.corpus is None

        assert self.t2.igt is None
        assert self.t2.corpus is None

    def test_metadata(self):
        assert len(self.t1.metadata) == 0

        assert self.t2.metadata[0].type == 'meta'
        assert len(self.t2.metadata[0].metas) == 1
        assert self.t2.metadata[0][0].text == 'meta'

    def test_attributes(self):
        assert self.t1.attributes == dict()

        assert self.t2.attributes == {'attr':'val'}

    def test_reference_attributes(self):
        # segmentation cannot co-occur with alignment or content
        with pytest.raises(XigtError): Tier(alignment='a1', segmentation='b1')
        with pytest.raises(XigtError): Tier(content='a1', segmentation='b1')

        assert self.t1.alignment is None
        assert self.t1.content is None
        assert self.t1.segmentation is None

        assert self.t2.alignment is None
        assert self.t2.content is None
        assert self.t2.segmentation is None

    def test_eq(self):
        assert self.t1 == self.t1
        assert self.t2 == self.t2
        assert self.t1 != self.t2

    def test_getitem(self):
        assert self.t2[0] == self.i1
        assert self.t2['t1'] == self.i1
        assert self.t2['0'] == self.i1
        assert self.t2[1] == self.i2
        with pytest.raises(IndexError): self.t2[2]
        with pytest.raises(IndexError): self.t2['2']
        with pytest.raises(KeyError): self.t2['t3']

    def test_setitem(self):
        t = Tier(items=[Item(id='a1'), Item(id='a2')])
        t[0] = Item(id='a3')
        assert len(t) == 2
        assert t[0].id == 'a3'
        with pytest.raises(KeyError): t['a1']
        with pytest.raises(ValueError): t['a2'] = Item(id='a3')

    def test_delitem(self):
        t = Tier(items=[Item(id='a1'), Item(id='a2')])
        assert len(t) == 2
        del t[0]
        assert len(t) == 1
        assert t[0].id == 'a2'
        with pytest.raises(KeyError): t['a1']
        del t['a2']
        assert len(t) == 0
        with pytest.raises(KeyError): t['a2']

    def test_get(self):
        assert self.t1.get(0) is None
        assert self.t1.get('t') is None
        assert self.t1.get('t', default=1) == 1

        assert self.t2.get(0).id == 't1'
        assert self.t2.get(2) is None
        assert self.t2.get('t1').id == 't1'
        assert self.t2.get('t1', default=Item(id='x')).id == 't1'

    def test_append(self):
        t = Tier()
        with pytest.raises(XigtStructureError): t.append(Tier())
        with pytest.raises(XigtStructureError): t.append(Igt())
        with pytest.raises(XigtStructureError): t.append(XigtCorpus())
        with pytest.raises(XigtStructureError): t.append(Metadata())
        with pytest.raises(XigtStructureError): t.append(Meta())
        assert len(t) == 0
        t.append(Item(id='t1'))
        assert len(t) == 1
        with pytest.raises(XigtError): t.append(Item(id='t1'))
        t.append(Item(id='t2'))
        assert len(t) == 2
        assert t[0].id == 't1'
        assert t[1].id == 't2'

    def test_insert(self):
        t = Tier()
        assert len(t) == 0
        t.insert(0, Item(id='t1'))
        assert len(t) == 1
        with pytest.raises(XigtError): t.insert(0, Item(id='t1'))
        t.insert(0, Item(id='t2'))
        t.insert(100, Item(id='t3'))
        assert len(t) == 3
        assert t[0].id == 't2'
        assert t[1].id == 't1'
        assert t[2].id == 't3'

    def test_extend(self):
        t = Tier()
        assert len(t) == 0
        t.extend([Item(id='t1')])
        assert len(t) == 1
        t.extend([])
        assert len(t) == 1
        t.extend([Item(id='t2'), Item(id='t3')])
        assert len(t) == 3
        assert t[0].id == 't1'
        assert t[1].id == 't2'
        assert t[2].id == 't3'

    def test_remove(self):
        t = Tier(items=[Item(id='i1'), Item(id='i2')])
        assert len(t) == 2
        t.remove(t[0])
        assert len(t) == 1
        assert t[0].id == 'i2'
        with pytest.raises(KeyError): t['i1']

    def test_clear(self):
        t = Tier()
        t.extend([Item(id='t1'), Item(id='t2'), Item(id='t3')])
        assert len(t) == 3
        t.clear()
        assert len(t) == 0
        assert t.get(0) is None
        assert t.get('t1') is None

    def test_get_attribute(self):
        t = Tier(id='t', attributes={'one': 1, 'two': 2})
        igt = Igt(tiers=[t], attributes={'three': 3})
        assert t.get_attribute('one') == 1
        assert t.get_attribute('two') == 2
        assert t.get_attribute('three') is None
        assert t.get_attribute('three', inherit=True) == 3
        assert t.get_attribute('three', default=4) == 4


class TestIgt():
    i1 = Igt()

    t1 = Tier(id='a', items=[Item(id='a1'), Item(id='a2')])
    t2 = Tier(id='b', items=[Item(id='b1'), Item(id='b2')])
    i2 = Igt(
        id='i1',
        type='basic',
        attributes={'attr':'val'},
        metadata=[Metadata(type='meta',
                           metas=[Meta(text='meta')])],
        tiers=[t1, t2]
    )

    def test_init(self):
        with pytest.raises(ValueError): Igt(id='1')  # invalid id
        # don't allow multiple tiers with the same ID
        with pytest.raises(XigtError): Igt(tiers=[Tier(id='a'), Tier(id='a')])

    def test_id(self):
        assert self.i1.id is None

        assert self.i2.id == 'i1'

    def test_type(self):
        assert self.i1.type is None

        assert self.i2.type == 'basic'

    def test_tiers(self):
        assert len(self.i1.tiers) == 0

        assert len(self.i2.tiers) == 2
        # contained Tiers should now have their igt specified
        for t in self.i2.tiers:
            assert t.igt is self.i2

    def test_parents(self):
        assert self.i1.corpus is None

        assert self.i2.corpus is None

    def test_metadata(self):
        assert len(self.i1.metadata) == 0

        assert self.i2.metadata[0].type == 'meta'
        assert len(self.i2.metadata[0].metas) == 1
        assert self.i2.metadata[0][0].text == 'meta'

    def test_attributes(self):
        assert self.i1.attributes == dict()

        assert self.i2.attributes == {'attr':'val'}

    def test_eq(self):
        assert self.i1 == self.i1
        assert self.i2 == self.i2
        assert self.i1 != self.i2

    def test_getitem(self):
        assert self.i2[0] == self.t1
        assert self.i2['a'] == self.t1
        assert self.i2['0'] == self.t1
        assert self.i2[1] == self.t2
        with pytest.raises(IndexError): self.i2[2]
        with pytest.raises(IndexError): self.i2['2']
        with pytest.raises(KeyError): self.i2['c']

    def test_setitem(self):
        igt = Igt(tiers=[Tier(id='a'), Tier(id='b')])
        igt[0] = Tier(id='c')
        assert len(igt) == 2
        assert igt[0].id == 'c'
        with pytest.raises(KeyError): igt['a']
        with pytest.raises(ValueError): igt['b'] = Tier(id='d')

    def test_delitem(self):
        igt = Igt(tiers=[Tier(id='a'), Tier(id='b')])
        assert len(igt) == 2
        del igt[0]
        assert len(igt) == 1
        assert igt[0].id == 'b'
        with pytest.raises(KeyError): igt['a']
        del igt['b']
        assert len(igt) == 0
        with pytest.raises(KeyError): igt['b']

    def test_get(self):
        assert self.i1.get(0) is None
        assert self.i1.get('t') is None
        assert self.i1.get('t', default=1) == 1

        assert self.i2.get(0).id == 'a'
        assert self.i2.get(3) is None
        assert self.i2.get('a').id == 'a'
        assert self.i2.get('a', default=Tier(id='x')).id == 'a'

    def test_get_item(self):
        assert self.i1.get_item('a') is None
        assert self.i1.get_item('a1') is None

        assert self.i2.get_item('a') is None
        assert self.i2.get_item('a1').id == 'a1'
        assert self.i2.get_item('b2').id == 'b2'

    def test_get_any(self):
        assert self.i1.get_any('a') is None
        assert self.i1.get_any('a1') is None

        assert self.i2.get_any('a').id is 'a'
        assert self.i2.get_any('a1').id == 'a1'
        assert self.i2.get_any('b2').id == 'b2'

    def test_append(self):
        igt = Igt()
        with pytest.raises(XigtStructureError): igt.append(Item())
        with pytest.raises(XigtStructureError): igt.append(Igt())
        with pytest.raises(XigtStructureError): igt.append(XigtCorpus())
        with pytest.raises(XigtStructureError): igt.append(Metadata())
        with pytest.raises(XigtStructureError): igt.append(Meta())
        assert len(igt) == 0
        igt.append(Tier(id='t'))
        assert len(igt) == 1
        with pytest.raises(XigtError): igt.append(Tier(id='t'))
        igt.append(Tier(id='x'))
        assert len(igt) == 2
        assert igt[0].id == 't'
        assert igt[1].id == 'x'

    def test_insert(self):
        igt = Igt()
        assert len(igt) == 0
        igt.insert(0, Tier(id='t'))
        assert len(igt) == 1
        with pytest.raises(XigtError): igt.insert(0, Tier(id='t'))
        igt.insert(0, Tier(id='x'))
        igt.insert(100, Tier(id='y'))
        assert len(igt) == 3
        assert igt[0].id == 'x'
        assert igt[1].id == 't'
        assert igt[2].id == 'y'

    def test_extend(self):
        igt = Igt()
        assert len(igt) == 0
        igt.extend([Tier(id='t')])
        assert len(igt) == 1
        igt.extend([])
        assert len(igt) == 1
        igt.extend([Tier(id='x'), Tier(id='y')])
        assert len(igt) == 3
        assert igt[0].id == 't'
        assert igt[1].id == 'x'
        assert igt[2].id == 'y'

    def test_remove(self):
        igt = Igt(tiers=[Tier(id='a'), Tier(id='b')])
        assert len(igt) == 2
        igt.remove(igt[0])
        assert len(igt) == 1
        assert igt[0].id == 'b'
        with pytest.raises(KeyError): igt['a']

    def test_clear(self):
        igt = Igt()
        igt.extend([Tier(id='t'), Tier(id='x'), Tier(id='y')])
        assert len(igt) == 3
        igt.clear()
        assert len(igt) == 0
        assert igt.get(0) is None
        assert igt.get('t') is None

    def test_get_attribute(self):
        igt = Igt(id='i1', attributes={'one': 1, 'two': 2})
        xc = XigtCorpus(igts=[igt], attributes={'three': 3})
        assert igt.get_attribute('one') == 1
        assert igt.get_attribute('two') == 2
        assert igt.get_attribute('three') is None
        assert igt.get_attribute('three', inherit=True) == 3
        assert igt.get_attribute('three', default=4) == 4


class TestXigtCorpus():

    c1 = XigtCorpus()

    i1 = Igt(id='i1')
    i2 = Igt(id='i2')
    c2 = XigtCorpus(
        id='xc1',
        type='basic',
        attributes={'attr':'val'},
        metadata=[Metadata(type='meta', metas=[Meta(text='meta')])],
        igts=[i1, i2]
    )

    def test_init(self):
        with pytest.raises(ValueError): XigtCorpus(id='1')  # invalid id

        # don't allow multiple igts with the same ID
        with pytest.raises(XigtError): XigtCorpus(igts=[Igt(id='i1'),
                                                        Igt(id='i1')])

    def test_id(self):
        assert self.c1.id is None

        assert self.c2.id == 'xc1'

    def test_type(self):
        assert self.c1.type is None

        assert self.c2.type is 'basic'

    def test_igts(self):
        assert len(self.c1.igts) == 0

        assert len(self.c2.igts) == 2
        # contained Igts should now have their corpus specified
        for i in self.c2.igts:
            assert i.corpus is self.c2

    def test_attributes(self):
        assert self.c1.attributes == dict()

        assert self.c2.attributes == {'attr':'val'}

    def test_metadata(self):
        assert len(self.c1.metadata) == 0

        assert self.c2.metadata[0].type == 'meta'
        assert len(self.c2.metadata[0].metas) == 1
        assert self.c2.metadata[0][0].text == 'meta'

    def test_eq(self):
        assert self.c1 == self.c1
        assert self.c2 == self.c2
        assert self.c1 != self.c2

    def test_getitem(self):
        assert self.c2[0] == self.i1
        assert self.c2['i1'] == self.i1
        assert self.c2['0'] == self.i1
        assert self.c2[1] == self.i2
        with pytest.raises(IndexError): self.c2[2]
        with pytest.raises(IndexError): self.c2['2']
        with pytest.raises(KeyError): self.c2['i3']

    def test_setitem(self):
        xc = XigtCorpus(igts=[Igt(id='i1'), Igt(id='i2')])
        xc[0] = Igt(id='i3')
        assert len(xc) == 2
        assert xc[0].id == 'i3'
        with pytest.raises(KeyError): xc['i1']
        with pytest.raises(ValueError): xc['i2'] = Igt(id='i3')

    def test_delitem(self):
        xc = XigtCorpus(igts=[Igt(id='i1'), Igt(id='i2')])
        assert len(xc) == 2
        del xc[0]
        assert len(xc) == 1
        assert xc[0].id == 'i2'
        with pytest.raises(KeyError): xc['i1']
        del xc['i2']
        assert len(xc) == 0
        with pytest.raises(KeyError): xc['i2']

    def test_get(self):
        assert self.c1.get(0) is None
        assert self.c1.get('i1') is None
        assert self.c1.get('i1', default=1) == 1

        assert self.c2.get(0).id == 'i1'
        assert self.c2.get(3) is None
        assert self.c2.get('i1').id == 'i1'
        assert self.c2.get('i1', default=Igt(id='i3')).id == 'i1'

    def test_append(self):
        xc = XigtCorpus()
        with pytest.raises(XigtStructureError): xc.append(Item())
        with pytest.raises(XigtStructureError): xc.append(Tier())
        with pytest.raises(XigtStructureError): xc.append(XigtCorpus())
        with pytest.raises(XigtStructureError): xc.append(Metadata())
        with pytest.raises(XigtStructureError): xc.append(Meta())
        assert len(xc) == 0
        xc.append(Igt(id='i1'))
        assert len(xc) == 1
        with pytest.raises(XigtError): xc.append(Igt(id='i1'))
        xc.append(Igt(id='i2'))
        assert len(xc) == 2
        assert xc[0].id == 'i1'
        assert xc[1].id == 'i2'

    def test_insert(self):
        xc = XigtCorpus()
        assert len(xc) == 0
        xc.insert(0, Igt(id='i1'))
        assert len(xc) == 1
        with pytest.raises(XigtError): xc.insert(0, Igt(id='i1'))
        xc.insert(0, Igt(id='i2'))
        xc.insert(100, Igt(id='i3'))
        assert len(xc) == 3
        assert xc[0].id == 'i2'
        assert xc[1].id == 'i1'
        assert xc[2].id == 'i3'

    def test_extend(self):
        xc = XigtCorpus()
        assert len(xc) == 0
        xc.extend([Igt(id='i1')])
        assert len(xc) == 1
        xc.extend([])
        assert len(xc) == 1
        xc.extend([Igt(id='i2'), Igt(id='i3')])
        assert len(xc) == 3
        assert xc[0].id == 'i1'
        assert xc[1].id == 'i2'
        assert xc[2].id == 'i3'

    def test_remove(self):
        xc = XigtCorpus(igts=[Igt(id='i1'), Igt(id='i2')])
        assert len(xc) == 2
        xc.remove(xc[0])
        assert len(xc) == 1
        assert xc[0].id == 'i2'
        with pytest.raises(KeyError): xc['i1']

    def test_clear(self):
        xc = XigtCorpus()
        xc.extend([Igt(id='i1'), Igt(id='i2'), Igt(id='i3')])
        assert len(xc) == 3
        xc.clear()
        assert len(xc) == 0
        assert xc.get(0) is None
        assert xc.get('i1') is None

    def test_get_attribute(self):
        xc = XigtCorpus(attributes={'one': 1, 'two': 2})
        assert xc.get_attribute('one') == 1
        assert xc.get_attribute('two') == 2
        assert xc.get_attribute('three') is None
        assert xc.get_attribute('three', inherit=True) == None
