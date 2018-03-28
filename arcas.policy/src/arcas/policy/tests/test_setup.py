# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from arcas.policy.testing import ARCAS_POLICY_INTEGRATION_TESTING  # noqa

import unittest


class TestSetup(unittest.TestCase):
    """Test that arcas.policy is properly installed."""

    layer = ARCAS_POLICY_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if arcas.policy is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'arcas.policy'))

    def test_browserlayer(self):
        """Test that IArcasPolicyLayer is registered."""
        from arcas.policy.interfaces import (
            IArcasPolicyLayer)
        from plone.browserlayer import utils
        self.assertIn(
            IArcasPolicyLayer,
            utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = ARCAS_POLICY_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        roles_before = api.user.get(userid=TEST_USER_ID).getRoles()
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.installer.uninstallProducts(['arcas.policy'])
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if arcas.policy is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'arcas.policy'))

    def test_browserlayer_removed(self):
        """Test that IArcasPolicyLayer is removed."""
        from arcas.policy.interfaces import \
            IArcasPolicyLayer
        from plone.browserlayer import utils
        self.assertNotIn(
           IArcasPolicyLayer,
           utils.registered_layers())
