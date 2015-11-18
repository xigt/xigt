import unittest

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

class TestTokenizer(unittest.TestCase):
    def test_tokenize(self):
        t = xp.tokenize
        self.assertEqual(t(''), [])
        self.assertEqual(t('/'), ['/'])
        self.assertEqual(t('//'), ['//'])
        self.assertEqual(t('/one'), ['/', 'one'])
        self.assertEqual(t('//one'), ['//', 'one'])
        self.assertEqual(t('one'), ['one'])
        self.assertEqual(t('one/two'), ['one', '/', 'two'])
        self.assertEqual(t('one/@attr'), ['one', '/', '@', 'attr'])
        self.assertEqual(t('one[@attr="val"]'),
                         ['one', '[', '@', 'attr', '=', '"val"', ']'])
        self.assertEqual(t('one/text()'), ['one', '/', 'text()'])
        # self.assertEqual(t('one/referrents("alignment")'),
        #                  ['one', '/', 'referrents("alignment")'])
        self.assertEqual(t('one/>'), ['one', '/', '>'])
        self.assertEqual(t('one/>@alignment'),
                         ['one', '/', '>', '@', 'alignment'])
        self.assertEqual(
            t('one/(two | three)/four'),
            ['one', '/', '(', 'two', '|', 'three', ')', '/', 'four']
        )


class TestXigtPath(unittest.TestCase):
    def test_find_root(self):
        self.assertEqual(xp.find(xc1, '/.'), xc1)
        self.assertEqual(xp.find(xc1[0], '/.'), xc1)
        self.assertEqual(xp.find(xc1[0][0], '/.'), xc1)

    def test_find_node(self):
        self.assertEqual(xp.find(xc1, 'igt'), xc1[0])
        self.assertEqual(xp.find(xc1, 'tier'), None)
        self.assertEqual(xp.find(xc1[0], 'tier'), xc1[0][0])
        self.assertEqual(xp.find(xc1, 'item'), None)
        self.assertEqual(xp.find(xc1[0], 'item'), None)
        self.assertEqual(xp.find(xc1[0][0], 'item'), xc1[0][0][0])

    def test_find_relative(self):
        self.assertEqual(xp.find(xc1, '.'), xc1)
        self.assertEqual(xp.find(xc1[0], '.'), xc1[0])
        self.assertEqual(xp.find(xc1[0], '..'), xc1)
        self.assertEqual(xp.find(xc1[0], '../.'), xc1)

    def find_descendants(self):
        self.assertEqual(xp.find(xc1, '//item'), xc1[0][0][0])
        self.assertEqual(xp.find(xc1[0], './/item'), xc1[0][0][0])
        self.assertEqual(xp.find(xc1[0][1], './/item'), xc1[0][1][0])
        self.assertEqual(xp.find(xc1[0][1], '//item'), xc1[0][0][0])

    def test_find_simple_path(self):
        self.assertEqual(xp.find(xc1, '/igt'), xc1[0])
        self.assertEqual(xp.find(xc1, '/igt/tier'), xc1[0][0])
        self.assertEqual(xp.find(xc1, '/igt/tier/item'), xc1[0][0][0])
        self.assertEqual(xp.find(xc1, 'igt/tier/item'), xc1[0][0][0])
        self.assertEqual(xp.find(xc1, 'tier/item'), None)
        self.assertEqual(xp.find(xc1[0], 'tier/item'), xc1[0][0][0])

    def test_findall(self):
        self.assertEqual(xp.findall(xc1, '/.'), [xc1])
        self.assertEqual(xp.findall(xc1, 'igt'), [xc1[0]])
        self.assertEqual(xp.findall(xc1, 'tier'), [])
        self.assertEqual(xp.findall(xc1[0], 'tier'), xc1[0].tiers)
        self.assertEqual(xp.findall(xc1, 'igt/tier'), xc1[0].tiers)
        self.assertEqual(xp.findall(xc1, '//tier'), xc1[0].tiers)
        self.assertEqual(xp.findall(xc1, 'igt/tier/item'),
                         [xc1[0][0][0], xc1[0][1][0]])
        self.assertEqual(xp.findall(xc1, '//item'),
                         [xc1[0][0][0], xc1[0][1][0]])

    def test_predicate(self):
        self.assertEqual(xp.find(xc1, '//tier[@type="phrases"]'),
                         xc1[0][0])
        self.assertEqual(xp.find(xc1, '//tier[@type="translations"]'),
                         xc1[0][1])
        self.assertEqual(xp.find(xc1, '//tier[@type="phrases"]/item'),
                         xc1[0][0][0])
        self.assertEqual(xp.find(xc1, '//item[../@type="translations"]'),
                         xc1[0][1][0])
        self.assertEqual(xp.find(xc3, '//item[../@type="glosses"][value()="NOM"]'),
                         xc3[0][3][1])

    def test_text(self):
        self.assertEqual(xp.find(xc1, '//item/text()'),
                         'inu=ga san-biki hoe-ru')

    def test_value(self):
        self.assertEqual(xp.find(xc3, '//tier[@type="words"]/item/value()'),
                         'inu=ga')

    def test_find_metadata(self):
        self.assertEqual(xp.find(xc1m, 'igt/metadata'),
                         xc1m[0].metadata[0])
        self.assertEqual(xp.findall(xc1m, 'igt/metadata'),
                         [xc1m[0].metadata[0]])
        self.assertEqual(xp.find(xc1m, 'igt/metadata/meta'),
                         xc1m[0].metadata[0][0])
        self.assertEqual(xp.findall(xc1m, 'igt/metadata/meta'),
                         [xc1m[0].metadata[0][0]])
        self.assertEqual(xp.find(xc1m, 'igt/metadata/meta/*'),
                         xc1m[0].metadata[0][0][0])
        self.assertEqual(
            xp.findall(xc1m, 'igt/metadata/meta/*'),
            [xc1m[0].metadata[0][0][0], xc1m[0].metadata[0][0][1]]
        )
        self.assertEqual(
            xp.find(xc1m, 'igt/metadata/meta/dc:subject'),
            xc1m[0].metadata[0][0][0]
        )
        self.assertEqual(
            xp.find(xc1m, 'igt/metadata//dc:subject'),
            xc1m[0].metadata[0][0][0]
        )
        self.assertEqual(
            xp.find(xc1m, 'igt/metadata/meta/dc:subject/@olac:code'),
            'jpn'
        )
        self.assertEqual(
            xp.find(xc1m, 'igt/metadata/meta/dc:subject/text()'),
            'Japanese'
        )
        self.assertEqual(
            xp.findall(xc1m, 'igt/metadata/meta/dc:*/@olac:code'),
            ['jpn', 'eng']
        )

    def test_find_referent(self):
        self.assertEqual(xp.find(xc3, '//tier[@type="words"]/>'), xc3[0][0])
        self.assertEqual(
            xp.find(xc3, '//tier[@type="words"]/>@alignment'),
            None
        )
        self.assertEqual(
            xp.find(xc3, '//tier[@type="words"]/>@segmentation'),
            xc3[0][0]
        )
        self.assertEqual(
            xp.find(xc3, '//item[../@type="words"]/>'),
            xc3[0][0][0]
        )
        self.assertEqual(
            xp.findall(xc3, '//item[../@type="words"]/>'),
            [xc3[0][0][0], xc3[0][0][0], xc3[0][0][0]]
        )
        self.assertEqual(
            xp.findall(xc3, '//item[../@type="words"]/>@alignment'),
            []
        )
        self.assertEqual(
            xp.findall(xc3, '//item[../@type="words"]/>@segmentation'),
            [xc3[0][0][0], xc3[0][0][0], xc3[0][0][0]]
        )

    def test_find_referrer(self):
        self.assertEqual(xp.find(xc3, '//tier[@type="phrases"]/<'),
            xc3[0][5]  # because "alignment" comes before "segmentation"
        )
        self.assertEqual(
            xp.findall(xc3, '//tier[@type="phrases"]/<'),
            [xc3[0][5], xc3[0][1]]
        )
        self.assertEqual(
            xp.find(xc3, '//tier[@type="phrases"]/<@segmentation'),
            xc3[0][1]
        )
        self.assertEqual(
            xp.find(xc3, '//tier[@type="phrases"]/<@alignment'),
            xc3[0][5]
        )
        self.assertEqual(
            xp.find(xc3, '//item[../@type="phrases"]/<'),
            xc3[0][5][0]
        )
        self.assertEqual(
            xp.findall(xc3, '//item[../@type="phrases"]/<'),
            [xc3[0][5][0], xc3[0][1][0], xc3[0][1][1], xc3[0][1][2]]
        )
        self.assertEqual(
            xp.findall(xc3, '//item[../@type="phrases"]/<@alignment'),
            [xc3[0][5][0]]
        )
        self.assertEqual(
            xp.findall(xc3, '//item[../@type="words"]/<@segmentation'),
            [xc3[0][2][0], xc3[0][2][1], xc3[0][2][2],
             xc3[0][2][3], xc3[0][2][4], xc3[0][2][5]]
        )

    def test_disjunction(self):
        self.assertEqual(
            xp.find(xc1, '(/igt/tier[@type="phrases"] | /igt/tier[@type="translations"])'),
            xc1[0][0]
        )
        self.assertEqual(
            xp.findall(xc1, '(/igt/tier[@type="phrases"] | /igt/tier[@type="translations"])'),
            [xc1[0][0], xc1[0][1]]
        )
        self.assertEqual(
            xp.find(xc1, 'igt/(tier[@type="phrases"] | tier[@type="translations"])'),
            xc1[0][0]
        )
        self.assertEqual(
            xp.findall(xc1, 'igt/(tier[@type="phrases"] | tier[@type="translations"])'),
            [xc1[0][0], xc1[0][1]]
        )
        self.assertEqual(
            xp.findall(xc1, 'igt/(tier[@type="phrases"] | tier[@type="translations"])/item'),
            [xc1[0][0][0], xc1[0][1][0]]
        )
