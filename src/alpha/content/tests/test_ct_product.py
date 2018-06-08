# -*- coding: utf-8 -*-
from alpha.content.content.product import IProduct  # NOQA E501
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


class ProductIntegrationTest(unittest.TestCase):

    layer = ALPHA_CONTENT_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_ct_product_schema(self):
        fti = queryUtility(IDexterityFTI, name='Product')
        schema = fti.lookupSchema()
        self.assertEqual(IProduct, schema)

    def test_ct_product_fti(self):
        fti = queryUtility(IDexterityFTI, name='Product')
        self.assertTrue(fti)

    def test_ct_product_factory(self):
        fti = queryUtility(IDexterityFTI, name='Product')
        factory = fti.factory
        obj = createObject(factory)

        self.assertTrue(
            IProduct.providedBy(obj),
            u'IProduct not provided by {0}!'.format(
                obj,
            ),
        )

    def test_ct_product_adding(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        obj = api.content.create(
            container=self.portal,
            type='Product',
            id='product',
        )

        self.assertTrue(
            IProduct.providedBy(obj),
            u'IProduct not provided by {0}!'.format(
                obj.id,
            ),
        )
