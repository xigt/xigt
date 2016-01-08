from xigt import (
    XigtCorpus, Igt, Tier, Item, Metadata, Meta,
    xigtpath as xp
)
# from xigt.errors import (
#     XigtError, XigtStructureError, XigtLookupError
# )

from .example_corpora import (
    xc1, xc1m, xc2, xc3, xc4, xc5
)

class TestTokenizer():
    def test_tokenize(self):
        t = xp.tokenize
        assert t('') == []
        assert t('/') == ['/']
        assert t('//') == ['//']
        assert t('/one') == ['/', 'one']
        assert t('//one') == ['//', 'one']
        assert t('one') == ['one']
        assert t('one/two') == ['one', '/', 'two']
        assert t('one/@attr') == ['one', '/', '@', 'attr']
        assert t('one[@attr="val"]') == ['one', '[', '@', 'attr', '=', '"val"', ']']
        assert t('one/text()') == ['one', '/', 'text', '(', ')']
        assert t('one/referent()') == ['one', '/', 'referent', '(', ')']
        assert t('one/referrer("alignment")') == ['one', '/', 'referrer', '(', '"alignment"', ')']
        assert t('one/(two | three)/four') == ['one', '/', '(', 'two', '|', 'three', ')', '/', 'four']
        # assert t('/ns:name') == ['/', 'ns', ':', 'name']
        # assert t('/following-sibling::name') == ['/', 'following-sibling', '::', 'name']
        # assert t('/following-sibling::ns:name') == ['/', 'following-sibling', '::', 'ns', ':', 'name']


class TestXigtPath():
    def test_find_root(self):
        assert xp.find(xc1, '/.') == xc1
        assert xp.find(xc1[0], '/.') == xc1
        assert xp.find(xc1[0][0], '/.') == xc1

    def test_find_node(self):
        assert xp.find(xc1, 'igt') == xc1[0]
        assert xp.find(xc1, 'tier') == None
        assert xp.find(xc1[0], 'tier') == xc1[0][0]
        assert xp.find(xc1, 'item') == None
        assert xp.find(xc1[0], 'item') == None
        assert xp.find(xc1[0][0], 'item') == xc1[0][0][0]

    def test_find_relative(self):
        assert xp.find(xc1, '.') == xc1
        assert xp.find(xc1[0], '.') == xc1[0]
        assert xp.find(xc1[0], '..') == xc1
        assert xp.find(xc1[0], '../.') == xc1

    def find_descendants(self):
        assert xp.find(xc1, '//item') == xc1[0][0][0]
        assert xp.find(xc1[0], './/item') == xc1[0][0][0]
        assert xp.find(xc1[0][1], './/item') == xc1[0][1][0]
        assert xp.find(xc1[0][1], '//item') == xc1[0][0][0]
        assert xp.find(xc1m, '//meta') == xc1m[0].metadata[0][0]

    def test_find_simple_path(self):
        assert xp.find(xc1, '/igt') == xc1[0]
        assert xp.find(xc1, '/igt/tier') == xc1[0][0]
        assert xp.find(xc1, '/igt/tier/item') == xc1[0][0][0]
        assert xp.find(xc1, 'igt/tier/item') == xc1[0][0][0]
        assert xp.find(xc1, 'tier/item') == None
        assert xp.find(xc1[0], 'tier/item') == xc1[0][0][0]

    def test_findall(self):
        assert xp.findall(xc1, '/.') == [xc1]
        assert xp.findall(xc1, 'igt') == [xc1[0]]
        assert xp.findall(xc1, 'tier') == []
        assert xp.findall(xc1[0], 'tier') == xc1[0].tiers
        assert xp.findall(xc1, 'igt/tier') == xc1[0].tiers
        assert xp.findall(xc1, '//tier') == xc1[0].tiers
        assert xp.findall(xc1, 'igt/tier/item') == [xc1[0][0][0], xc1[0][1][0]]
        assert xp.findall(xc1, '//item') == [xc1[0][0][0], xc1[0][1][0]]
        assert xp.findall(xc1m, '//meta') == list(xc1m[0].metadata[0])

    def test_star(self):
        assert xp.findall(xc1, '/*') == [xc1[0]]
        assert xp.findall(xc1, '/*/*') == [xc1[0][0], xc1[0][1]]
        assert xp.findall(xc1, '//tier/*') == [xc1[0][0][0], xc1[0][1][0]]
        # star includes metadata
        assert xp.findall(xc1m, '/igt/*') == list(xc1m[0].metadata) + [xc1m[0][0], xc1m[0][1]]


    def test_predicate(self):
        assert xp.find(xc1, '//tier[@type="phrases"]') == xc1[0][0]
        assert xp.find(xc1, '//tier[@type="translations"]') == xc1[0][1]
        assert xp.find(xc1, '//tier[@type="phrases"]/item') == xc1[0][0][0]
        assert xp.find(xc1, '//item[../@type="translations"]') == xc1[0][1][0]
        assert xp.find(xc3, '//item[../@type="glosses"][value()="NOM"]') == xc3[0][3][1]

    def test_text(self):
        assert xp.find(xc1, '//item/text()') == 'inu=ga san-biki hoe-ru'

    def test_value(self):
        assert xp.find(xc3, '//tier[@type="words"]/item/value()') == 'inu=ga'

    def test_find_metadata(self):
        assert xp.find(xc1m, 'igt/metadata') == xc1m[0].metadata[0]
        assert xp.findall(xc1m, 'igt/metadata') == [xc1m[0].metadata[0]]
        assert xp.find(xc1m, 'igt/metadata/meta') == xc1m[0].metadata[0][0]
        assert xp.findall(xc1m, 'igt/metadata/meta') == [xc1m[0].metadata[0][0]]
        assert xp.find(xc1m, 'igt/metadata/meta/*') == xc1m[0].metadata[0][0][0]
        assert xp.findall(xc1m, 'igt/metadata/meta/*') == [xc1m[0].metadata[0][0][0], xc1m[0].metadata[0][0][1]]
        assert xp.find(xc1m, 'igt/metadata/meta/dc:subject') == xc1m[0].metadata[0][0][0]
        assert xp.find(xc1m, 'igt/metadata//dc:subject') == xc1m[0].metadata[0][0][0]
        assert xp.find(xc1m, 'igt/metadata/meta/dc:subject/@olac:code') == 'jpn'
        assert xp.find(xc1m, 'igt/metadata/meta/dc:subject/text()') == 'Japanese'
        assert xp.findall(xc1m, 'igt/metadata/meta/dc:*/@olac:code') == ['jpn', 'eng']

    def test_find_referent(self):
        assert xp.find(xc3, '//tier[@type="words"]/referent()') == xc3[0][0]
        assert xp.find(xc3, '//tier[@type="words"]/referent("alignment")') == None
        assert xp.find(xc3, '//tier[@type="words"]/referent("segmentation")') == xc3[0][0]
        assert xp.find(xc3, '//item[../@type="words"]/referent()') == xc3[0][0][0]
        assert xp.findall(xc3, '//item[../@type="words"]/referent()') == [xc3[0][0][0], xc3[0][0][0], xc3[0][0][0]]
        assert xp.findall(xc3, '//item[../@type="words"]/referent("alignment")') == []
        assert xp.findall(xc3, '//item[../@type="words"]/referent("segmentation")') == [xc3[0][0][0], xc3[0][0][0], xc3[0][0][0]]

    def test_find_referrer(self):
        assert xp.find(xc3, '//tier[@type="phrases"]/referrer()') == xc3[0][5]  # because "alignment" comes before "segmentation"
        assert xp.findall(xc3, '//tier[@type="phrases"]/referrer()') == [xc3[0][5], xc3[0][1]]
        assert xp.find(xc3, '//tier[@type="phrases"]/referrer("segmentation")') == xc3[0][1]
        assert xp.find(xc3, '//tier[@type="phrases"]/referrer("alignment")') == xc3[0][5]
        assert xp.find(xc3, '//item[../@type="phrases"]/referrer()') == xc3[0][5][0]
        assert xp.findall(xc3, '//item[../@type="phrases"]/referrer()') == [xc3[0][5][0], xc3[0][1][0], xc3[0][1][1], xc3[0][1][2]]
        assert xp.findall(xc3, '//item[../@type="phrases"]/referrer("alignment")') == [xc3[0][5][0]]
        assert xp.findall(xc3, '//item[../@type="words"]/referrer("segmentation")') == [xc3[0][2][0], xc3[0][2][1], xc3[0][2][2], xc3[0][2][3], xc3[0][2][4], xc3[0][2][5]]

    def test_disjunction(self):
        assert xp.find(xc1, '(/igt/tier[@type="phrases"] | /igt/tier[@type="translations"])') == xc1[0][0]
        assert xp.findall(xc1, '(/igt/tier[@type="phrases"] | /igt/tier[@type="translations"])') == [xc1[0][0], xc1[0][1]]
        assert xp.find(xc1, 'igt/(tier[@type="phrases"] | tier[@type="translations"])') == xc1[0][0]
        assert xp.findall(xc1, 'igt/(tier[@type="phrases"] | tier[@type="translations"])') == [xc1[0][0], xc1[0][1]]
        assert xp.findall(xc1, 'igt/(tier[@type="phrases"] | tier[@type="translations"])/item') == [xc1[0][0][0], xc1[0][1][0]]

    # def test_axes(self):
    #     assert xp.find(xc1, '/igt') == xp.find(xc1, '/child::igt')
