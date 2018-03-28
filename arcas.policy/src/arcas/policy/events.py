# -*- coding: utf-8 -*-
__author__ = 'Paul'
#from plone.app.users.browser.personalpreferences import UserDataPanelAdapter
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter
#from plone.app.controlpanel.interfaces import IConfigurationChangedEvent
#from Products.CMFPlone.interfaces import IConfigurationChangedEvent
from Products.CMFPlone.interfaces import IConfigurationChangedEvent


try:
    from arcas.content.eventos import PREFIJO_COOR_POTENCIAL
except:
    PREFIJO_COOR_POTENCIAL=""



def on_save(event):
    """ cuando se cambia el perfil de usuario"""
    estaAsignadoPotencial=False

    
    if IConfigurationChangedEvent.providedBy(event):
        groups_tool=getToolByName(event.context,"portal_groups")
        member_tool=getToolByName(event.context,"portal_membership")
        miId=member_tool.getAuthenticatedMember().id

        if event.data.has_key("participaEn"):
            if event.data["participaEn"]:
                for nomColect in event.data["participaEn"]:
                    nGid=nomColect+PREFIJO_COOR_POTENCIAL
                    
                    try:
                        grupPotencial=groups_tool.getGroupById(nGid)                        
                    except:
                        print "El grupo: %s no existe" %nGid
                        return
                    try:
                        groups_tool.addPrincipalToGroup(miId, nGid)
                    except:
                        print "No pudo asignarse el usuario: %s al grupo: %s" %(miId, nGid)
                        return
        """Determian si està asignado a la colección que eligió"""




        print "particpa en "
