# -*- coding: utf-8 -*-
from alpha.content.content.productimg import IProductimg  # NOQA E501
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


class ProductimgIntegrationTest(unittest.TestCase):

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

    def test_ct_productimg_schema(self):
        fti = queryUtility(IDexterityFTI, name='ProductImg')
        schema = fti.lookupSchema()
        self.assertEqual(IProductimg, schema)

    def test_ct_productimg_fti(self):
        fti = queryUtility(IDexterityFTI, name='ProductImg')
        self.assertTrue(fti)

    def test_ct_productimg_factory(self):
        fti = queryUtility(IDexterityFTI, name='ProductImg')
        factory = fti.factory
        obj = createObject(factory)

        self.assertTrue(
            IProductimg.providedBy(obj),
            u'IProductimg not provided by {0}!'.format(
                obj,
            ),
        )

    def test_ct_productimg_adding(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        obj = api.content.create(
            container=self.parent,
            type='ProductImg',
            id='productimg',
        )

        self.assertTrue(
            IProductimg.providedBy(obj),
            u'IProductimg not provided by {0}!'.format(
                obj.id,
            ),
        )
