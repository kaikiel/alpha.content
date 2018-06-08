# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from alpha.content.testing import ALPHA_CONTENT_INTEGRATION_TESTING  # noqa

import unittest


class TestSetup(unittest.TestCase):
    """Test that alpha.content is properly installed."""

    layer = ALPHA_CONTENT_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if alpha.content is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'alpha.content'))

    def test_browserlayer(self):
        """Test that IAlphaContentLayer is registered."""
        from alpha.content.interfaces import (
            IAlphaContentLayer)
        from plone.browserlayer import utils
        self.assertIn(
            IAlphaContentLayer,
            utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = ALPHA_CONTENT_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.installer.uninstallProducts(['alpha.content'])
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if alpha.content is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'alpha.content'))

    def test_browserlayer_removed(self):
        """Test that IAlphaContentLayer is removed."""
        from alpha.content.interfaces import \
            IAlphaContentLayer
        from plone.browserlayer import utils
        self.assertNotIn(
            IAlphaContentLayer,
            utils.registered_layers())
