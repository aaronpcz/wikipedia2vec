# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import unittest
import six
import six.moves.cPickle as pickle

from wikipedia2vec.dump_db import Paragraph, WikiLink

from . import get_dump_db

from nose.tools import *


class TestParagraph(unittest.TestCase):
    def test_text_property(self):
        paragraph = Paragraph('paragraph text', [])
        eq_('paragraph text', paragraph.text)

    def test_wiki_link_property(self):
        wiki_link = WikiLink('Title', 'link text', 0, 3)
        paragraph = Paragraph('paragraph text', [wiki_link])
        eq_([wiki_link], paragraph.wiki_links)

    def test_pickle(self):
        wiki_link = WikiLink('Title', 'link text', 0, 3)
        paragraph = Paragraph('paragraph text', [wiki_link])

        paragraph2 = pickle.loads(pickle.dumps(paragraph))
        eq_('paragraph text', paragraph2.text)
        eq_(wiki_link.title, paragraph2.wiki_links[0].title)
        eq_(wiki_link.text, paragraph2.wiki_links[0].text)
        eq_(wiki_link.span, paragraph2.wiki_links[0].span)

        eq_(pickle.dumps(paragraph), pickle.dumps(pickle.loads(pickle.dumps(paragraph))))


class TestWikiLink(unittest.TestCase):
    def test_title_property(self):
        wiki_link = WikiLink('WikiTitle', 'link text', 0, 3)
        eq_('WikiTitle', wiki_link.title)

    def test_text_property(self):
        wiki_link = WikiLink('WikiTitle', 'link text', 0, 3)
        eq_('link text', wiki_link.text)

    def test_start_property(self):
        wiki_link = WikiLink('WikiTitle', 'link text', 0, 3)
        eq_(0, wiki_link.start)

    def test_end_property(self):
        wiki_link = WikiLink('WikiTitle', 'link text', 0, 3)
        eq_(3, wiki_link.end)

    def test_span_property(self):
        wiki_link = WikiLink('WikiTitle', 'link text', 0, 3)
        eq_((0, 3), wiki_link.span)

    def test_pickle(self):
        wiki_link = WikiLink('WikiTitle', 'link text', 0, 3)
        wiki_link2 = pickle.loads(pickle.dumps(wiki_link))
        eq_(wiki_link.title, wiki_link2.title)
        eq_(wiki_link.text, wiki_link2.text)
        eq_(wiki_link.span, wiki_link2.span)

        eq_(pickle.dumps(wiki_link), pickle.dumps(pickle.loads(pickle.dumps(wiki_link))))


class TestDumpDB(unittest.TestCase):
    def setUp(self):
        self.db = get_dump_db()

    def test_id_property(self):
        ok_(isinstance(self.db.id, six.text_type))
        eq_(32, len(self.db.id))

    def test_dump_file_property(self):
        self.db.dump_file.endswith('enwiki-pages-articles-sample.xml.bz2')

    def test_language_property(self):
        eq_('en', self.db.language)

    def test_page_size(self):
        eq_(2, self.db.page_size())

    def test_titles_generator(self):
        eq_(['Accessibility', 'Computer accessibility'], list(self.db.titles()))

    def test_redirects_generator(self):
        eq_([('AccessibleComputing', 'Computer accessibility')], list(self.db.redirects()))

    def test_get_paragraphs(self):
        paragraphs = self.db.get_paragraphs('Computer accessibility')
        paragraph = paragraphs[0]

        ok_(paragraph.text.replace(' ', '').startswith('Inhuman–computerinteraction'))
        wiki_link = paragraph.wiki_links[0]
        eq_('Human–computer interaction', wiki_link.title)
        eq_('human–computer interaction', wiki_link.text)
        eq_((4, 30), wiki_link.span)

        for paragraph in paragraphs:
            ok_(isinstance(paragraph, Paragraph))

        for paragraph in paragraphs:
            for wiki_link in paragraph.wiki_links:
                ok_(isinstance(wiki_link, WikiLink))
                eq_(paragraph.text[wiki_link.start:wiki_link.end], wiki_link.text)

    @raises(KeyError)
    def test_get_paragraphs_with_invalid_key(self):
        self.db.get_paragraphs('foo')
