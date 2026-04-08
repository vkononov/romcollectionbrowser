# -*- coding: utf-8 -*-
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib'))

import util


class TestPlotFormat(unittest.TestCase):

    def test_html_plot_to_kodi_em_and_p(self):
        raw = '<p><em>Waterworld</em> is an adaptation.</p><p>Second paragraph.</p>'
        out = util.html_plot_to_kodi_labels(raw)
        self.assertIn('[I]', out)
        self.assertIn('Waterworld', out)
        self.assertIn('[CR][CR]', out)
        self.assertNotIn('<p>', out)
        self.assertNotIn('<em>', out)
        self.assertFalse(out.startswith('[CR]'))
        idx = out.find('Second paragraph')
        self.assertGreater(idx, 0)
        self.assertIn('[CR][CR]', out[:idx])

    def test_plain_plot_no_leading_break(self):
        out = util.html_plot_to_kodi_labels('Plain description without HTML.')
        self.assertEqual(out, 'Plain description without HTML.')
        self.assertFalse(out.startswith('[CR]'))

    def test_html_plot_to_kodi_link_strips_to_label(self):
        raw = 'See <a href="https://example.com/x">the page</a> for more.'
        out = util.html_plot_to_kodi_labels(raw)
        self.assertIn('the page', out)
        self.assertNotIn('href', out)
        self.assertNotIn('<a', out)

    def test_strip_html_plot_plain(self):
        raw = '<p><em>Hi</em> there</p><p>Line two</p>'
        out = util.strip_html_plot(raw)
        self.assertIn('Hi', out)
        self.assertIn('there', out)
        self.assertNotIn('<', out)

    def test_format_override_strip(self):
        raw = '<b>Bold</b> text'
        plain = util.format_game_plot_for_display(raw, strip_html_override=True)
        rich = util.format_game_plot_for_display(raw, strip_html_override=False)
        self.assertNotIn('[B]', plain)
        self.assertNotIn('<', plain)
        self.assertIn('[B]', rich)


if __name__ == '__main__':
    unittest.main()
