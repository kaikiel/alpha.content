# -*- coding: utf-8 -*-
from alpha.content.behaviors.map_category import IMapCategory
from alpha.content.testing import ALPHA_CONTENT_INTEGRATION_TESTING  # noqa
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.behavior.interfaces import IBehavior
from zope.component import getUtility

import unittest


class MapCategoryIntegrationTest(unittest.TestCase):

    layer = ALPHA_CONTENT_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_behavior_map_category(self):
        behavior = getUtility(IBehavior, 'alpha.content.map_category')
        self.assertEqual(
            behavior.marker,
            IMapCategory,
        )
        behavior_name = 'alpha.content.behaviors.map_category.IMapCategory'
        behavior = getUtility(IBehavior, behavior_name)
        self.assertEqual(
            behavior.marker,
            IMapCategory,
        )
