# -*- coding: utf-8 -*-
from alpha.content.content.productreview import IProductreview  # NOQA E501
from alpha.content.testing import ALPHA_CONTENT_INTEGRATION_TESTING  # noqa
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import createObject
from zope.component import queryUtility

import unittest


try:
    from plone.dexterity.schema import portalTypeToSchemaName
except ImportError:
    # Plone < 5
    from plone.dexterity.utils import portalTypeToSchemaName


class ProductreviewIntegrationTest(unittest.TestCase):

    layer = ALPHA_CONTENT_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        portal_types = self.portal.portal_types
        parent_id = portal_types.constructContent(
            'Product',
            self.portal,
            'parent_id',
            title='Parent container',
        )
        self.parent = self.portal[parent_id]

    def test_ct_productreview_schema(self):
        fti = queryUtility(IDexterityFTI, name='ProductReview')
        schema = fti.lookupSchema()
        self.assertEqual(IProductreview, schema)

    def test_ct_productreview_fti(self):
        fti = queryUtility(IDexterityFTI, name='ProductReview')
        self.assertTrue(fti)

    def test_ct_productreview_factory(self):
        fti = queryUtility(IDexterityFTI, name='ProductReview')
        factory = fti.factory
        obj = createObject(factory)

        self.assertTrue(
            IProductreview.providedBy(obj),
            u'IProductreview not provided by {0}!'.format(
                obj,
            ),
        )

    def test_ct_productreview_adding(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        obj = api.content.create(
            container=self.parent,
            type='ProductReview',
            id='productreview',
        )

        self.assertTrue(
            IProductreview.providedBy(obj),
            u'IProductreview not provided by {0}!'.format(
                obj.id,
            ),
        )
