# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from arcas.content.testing import ARCAS_CONTENT_INTEGRATION_TESTING  # noqa

import unittest


class TestSetup(unittest.TestCase):
    """Test that arcas.content is properly installed."""

    layer = ARCAS_CONTENT_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if arcas.content is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'arcas.content'))

    def test_browserlayer(self):
        """Test that IArcasContentLayer is registered."""
        from arcas.content.interfaces import (
            IArcasContentLayer)
        from plone.browserlayer import utils
        self.assertIn(
            IArcasContentLayer,
            utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = ARCAS_CONTENT_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        roles_before = api.user.get(userid=TEST_USER_ID).getRoles()
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.installer.uninstallProducts(['arcas.content'])
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if arcas.content is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'arcas.content'))

    def test_browserlayer_removed(self):
        """Test that IArcasContentLayer is removed."""
        from arcas.content.interfaces import \
            IArcasContentLayer
        from plone.browserlayer import utils
        self.assertNotIn(
           IArcasContentLayer,
           utils.registered_layers())
