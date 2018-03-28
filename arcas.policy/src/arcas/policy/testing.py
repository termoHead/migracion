# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import arcas.policy


class ArcasPolicyLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        self.loadZCML(package=arcas.policy)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'arcas.policy:default')


ARCAS_POLICY_FIXTURE = ArcasPolicyLayer()


ARCAS_POLICY_INTEGRATION_TESTING = IntegrationTesting(
    bases=(ARCAS_POLICY_FIXTURE,),
    name='ArcasPolicyLayer:IntegrationTesting'
)


ARCAS_POLICY_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(ARCAS_POLICY_FIXTURE,),
    name='ArcasPolicyLayer:FunctionalTesting'
)


ARCAS_POLICY_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        ARCAS_POLICY_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name='ArcasPolicyLayer:AcceptanceTesting'
)
