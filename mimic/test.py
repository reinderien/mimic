from unittest import TestCase
from . import all_hgs, hg_index


class TestDataset(TestCase):

    def test_ascii_range(self):
        self.assertEqual(len(all_hgs), ord('~') - ord(' ') + 1)
        for i in xrange(len(all_hgs)):
            self.assertIsInstance(all_hgs[i].ascii, str)
            self.assertEqual(all_hgs[i].ascii, chr(i + ord(' ')))

    def test_unicode_range(self):
        for hgs in all_hgs:
            self.assertIsInstance(hgs.fwd, unicode)
            self.assertIsInstance(hgs.rev, unicode)
            for c in hgs.rev + hgs.fwd:
                self.assertTrue(ord(c) > ord('~'))

    def test_unique(self):
        charset = set()
        for hgs in all_hgs:
            all_chars = hgs.ascii + hgs.fwd + hgs.rev
            self.assertEqual(len(all_chars), len(set(all_chars)),
                             '%c has dupes' % hgs.ascii)
            for c in all_chars:
                self.assertFalse(c in charset)
                charset.add(c)
        self.assertEqual(charset, set(hg_index.iterkeys()))