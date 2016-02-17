# -*- coding: utf-8 -*-
# ###
# Copyright (c) 2016, Rice University
# This software is subject to the provisions of the GNU Affero General
# Public License version 3 (AGPLv3).
# See LICENCE.txt for details.
# ###
import unittest

import cnxepub
from pyramid import testing as pyramid_testing

from .. import testing


class BaseTestCase(unittest.TestCase):
    fixture = testing.data_fixture

    @classmethod
    def setUpClass(cls):
        cls.settings = testing.integration_test_settings()
        # This is a read-only testcase, only setup once
        cls.fixture.setUp()

    def setUp(self):
        self.config = pyramid_testing.setUp(settings=self.settings)

    def tearDown(self):
        pyramid_testing.tearDown()

    @classmethod
    def tearDownClass(cls):
        cls.fixture.tearDown()


class MetadataGetterTestCase(BaseTestCase):

    @property
    def target(self):
        from cnxarchive.scripts.export_epub import get_metadata
        return get_metadata

    def assert_contains(self, l1, l2):
        """Check that ``l1`` contains ``l2``"""
        not_in = [i for i in l2 if i not in l1]
        if not_in:
            self.fail("Could not find {} in:\n {}"
                      .format(not_in, l1))

    def test_not_found(self):
        ident_hash = '31b37e2b-9abf-4923-b2fa-de004a3cb6cd'
        from cnxarchive.scripts.export_epub import NotFound
        try:
            doc = self.target(ident_hash)
        except NotFound:
            pass
        else:
            self.fail("this should not have found an entry")

    def test_get(self):
        id, version = ('f6024d8a-1868-44c7-ab65-45419ef54881', '3')
        ident_hash = '{}@{}'.format(id, version)
        metadata = self.target(ident_hash)

        metadata_keys = [
            'id', 'version',
            'title', 'language', 'created', 'revised', 
            'license_url', 'license_text',
            'summary', 'subjects', 'keywords',
            'cnx-archive-uri',
            # People keys
            'authors', 'editors', 'illustrators', 'publishers',
            'copyright_holders',
            # Print style
            'print_style',
            # Derivation keys
            'derived_from_uri', 'derived_from_title',
            ]
        required_keys = metadata_keys[:16]
        self.assert_contains(metadata, required_keys)

        self.assertEqual(metadata['id'], id)
        self.assertEqual(metadata['version'], version)

        self.assertEqual(metadata['title'], u"Atomic Masses")
        self.assertEqual(metadata['language'], u'en')
        self.assertEqual(metadata['created'], u'2013-07-31T19:07:25Z')
        self.assertEqual(metadata['revised'], u'2013-07-31T19:07:25Z')
        self.assertEqual(metadata['license_url'],
                         u'http://creativecommons.org/licenses/by/4.0/')
        self.assertEqual(metadata['license_text'],
                         u'Creative Commons Attribution License')
        self.assertEqual(metadata['summary'], None)  # FIXME Bad data
        self.assertEqual(metadata['subjects'], [u'Science and Technology'])
        self.assertEqual(metadata['keywords'], [])
        self.assertEqual(metadata['cnx-archive-uri'],
                         u'f6024d8a-1868-44c7-ab65-45419ef54881@3')

        roles = [
            {u'firstname': u'OpenStax College',
             u'fullname': u'OpenStax College',
             u'id': u'OpenStaxCollege',
             u'suffix': None,
             u'surname': None,
             u'title': None},
            {u'firstname': u'Rice',
             u'fullname': u'Rice University',
             u'id': u'OSCRiceUniversity',
             u'suffix': None,
             u'surname': u'University',
             u'title': None},
            {u'firstname': u'OpenStax College',
             u'fullname': u'OpenStax College',
             u'id': u'OpenStaxCollege',
             u'suffix': None,
             u'surname': None,
             u'title': None},
            {u'firstname': u'College',
             u'fullname': u'OSC Physics Maintainer',
             u'id': u'cnxcap',
             u'suffix': None,
             u'surname': u'Physics',
             u'title': None},
            ]
        self.assertEqual(metadata['authors'], [roles[0]])
        self.assertEqual(metadata['editors'], [])
        self.assertEqual(metadata['illustrators'], [])
        self.assertEqual(metadata['translators'], [])
        self.assertEqual(metadata['publishers'], roles[2:])
        self.assertEqual(metadata['copyright_holders'], [roles[1]])

        self.assertEqual(metadata['print_style'], None)
        self.assertEqual(metadata['derived_from_uri'], None)
        self.assertEqual(metadata['derived_from_title'], None)


class ContentGetterTestCase(BaseTestCase):

    @property
    def target(self):
        from cnxarchive.scripts.export_epub import get_content
        return get_content

    def test_get(self):
        ident_hash = 'f6024d8a-1868-44c7-ab65-45419ef54881@3'
        content = self.target(ident_hash)
        self.assertIn('<span class="title">Atomic Masses</span>', content)

    def test_not_found(self):
        ident_hash = 'f6024d8a-1868-44c7-ab65-45419ef54881@5'

        from cnxarchive.scripts.export_epub import ContentNotFound
        try:
            self.target(ident_hash)
        except ContentNotFound:
            pass
        else:
            self.fail("should not have found content")


class FileInfoGetterTestCase(BaseTestCase):

    @property
    def target(self):
        from cnxarchive.scripts.export_epub import get_file_info
        return get_file_info

    def test_get(self):
        hash = '075500ad9f71890a85fe3f7a4137ac08e2b7907c'
        filename = 'PhET_Icon.png'
        media_type = 'image/png'

        fn, mt = self.target(hash)
        self.assertEqual(fn, filename)
        self.assertEqual(mt, media_type)

    def test_with_context(self):
        hash = '075500ad9f71890a85fe3f7a4137ac08e2b7907c'
        ident_hash = 'd395b566-5fe3-4428-bcb2-19016e3aa3ce@4'
        filename = 'PhET_Icon.png'
        media_type = 'image/png'

        fn, mt = self.target(hash, context=ident_hash)
        self.assertEqual(fn, filename)
        self.assertEqual(mt, media_type)

    def test_not_found(self):
        hash = 'c7097b2e80ca7314a7f3ef58a09817f9da005570'

        from cnxarchive.scripts.export_epub import FileNotFound
        try:
            self.target(hash)
        except FileNotFound:
            pass
        else:
            self.fail("should not have found a file")


class FileGetterTestCase(BaseTestCase):

    @property
    def target(self):
        from cnxarchive.scripts.export_epub import get_file
        return get_file

    def test_get(self):
        hash = 'b7a943d679932431e674a174776397b824edc000'

        file = self.target(hash)
        self.assertEqual(file[400:414].tobytes(), 'name="license"')

    def test_not_found(self):
        hash = 'c7097b2e80ca7314a7f3ef58a09817f9da005570'

        from cnxarchive.scripts.export_epub import FileNotFound
        try:
            self.target(hash)
        except FileNotFound:
            pass
        else:
            self.fail("should not have found a file")


class ResourceFactoryTestCase(BaseTestCase):

    @property
    def target(self):
        from cnxarchive.scripts.export_epub import resource_factory
        return resource_factory

    def test_get(self):
        hash = 'ceb4a4476591cc245e6be735399a309a224c9b67'
        ident_hash = 'd395b566-5fe3-4428-bcb2-19016e3aa3ce@4'
        filename = 'index.cnxml'
        media_type = 'text/xml'

        resource = self.target(hash, context=ident_hash)

        self.assertEqual(resource.filename, filename)
        self.assertEqual(resource.media_type, media_type)
        with resource.open() as f:
            contents = f.read()
        self.assertIn('<?xml version="1.0"?>', contents)


class DocumentFactoryTestCase(BaseTestCase):

    @property
    def target(self):
        from cnxarchive.scripts.export_epub import document_factory
        return document_factory

    def test_not_found(self):
        ident_hash = '31b37e2b-9abf-4923-b2fa-de004a3cb6cd@4'
        from cnxarchive.scripts.export_epub import NotFound
        try:
            doc = self.target(ident_hash)
        except NotFound:
            pass
        else:
            self.fail("this should not have created a document")

    def test_assembly(self):
        ident_hash = 'd395b566-5fe3-4428-bcb2-19016e3aa3ce@4'
        doc = self.target(ident_hash)

        self.assertTrue(isinstance(doc, cnxepub.Document))

        # Briefly check for the existence of metadata.
        self.assertEqual(doc.metadata['title'], u'Physics: An Introduction')

        # Check for specific content.
        self.assertIn('<h1 class="title">Applications of Physics</h1>', doc.content)

        refs = [r.uri for r in doc.references if r.uri.startswith('/resources/')]
        # Simple check incase the data changes, otherwise not a needed test.
        self.assertEqual(len(refs), 15)
        # Check a reference for binding
        self.fail()
