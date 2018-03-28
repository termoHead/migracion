# -*- coding: utf-8 -*-
__author__ = 'Paul'

from five import grok
from zope.i18n import translate
from zope.i18nmessageid import MessageFactory
from zope.interface import implements
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from zope.site.hooks import getSite
from Acquisition import aq_get
from Products.CMFCore.utils import getToolByName
from plone.app.vocabularies.users import UsersSource
from plone.app.vocabularies.groups import GroupsSource
from arcas.content.eventos import PREFIJO_COOR_POTENCIAL
_ = MessageFactory('plone')
from arcas.content.behaviors import IColecGroupName


class GroupMembers(object):
    """Context source binder to provide a vocabulary of users in a given group.
    """
    
    implements(IVocabularyFactory)
    def __init__(self, group_name):
        self.group_name = group_name


    def __call__(self, context):
        acl_users = getToolByName(context, 'acl_users')
        group = acl_users.getGroupById(self.group_name)
        userssource = UsersSource(context)

        terms = []
        roles = context.get_local_roles()

        if group is not None:
            for member_id in group.getMemberIds():
                user = acl_users.getUserById(member_id)
                if user is not None:
                    member_name = user.getProperty('fullname') or member_id
                    terms.append(SimpleVocabulary.createTerm(member_id, str(member_id), member_name))


        return SimpleVocabulary(terms)

class GroupPotenciales(object):
    """Genera un vocabulario con los potenciales investigadores para esa carpeta"""
    implements(IVocabularyFactory)

    def __call__(self, context):
        acl_users = getToolByName(context, 'acl_users')
        try:
            idGAsign=IColecGroupName(context).groupName
        except:
            print "No se puedo asignar IColectGroupName"
            return SimpleVocabulary([SimpleVocabulary.createTerm("", str(""), "")])
        idGPot=idGAsign.replace("_g",PREFIJO_COOR_POTENCIAL)

        grupoPot= acl_users.getGroupById(idGPot)
        grupoAsignado=acl_users.getGroupById(idGAsign)

        terms = []
        listIds=[]
        
        
        if grupoPot is not None:
            for member_id in grupoPot.getMemberIds()+grupoAsignado.getMemberIds():
                if member_id not in listIds:
                    user = acl_users.getUserById(member_id)
                    if user is not None:
                        member_name = user.getProperty('fullname') or member_id
                        listIds.append(member_id)
                        terms.append(SimpleVocabulary.createTerm(member_id, str(member_id), member_name))

            return SimpleVocabulary(terms)
        #devulve un registro vacio
        return SimpleVocabulary([SimpleVocabulary.createTerm("", str(""), "")])

class GroupPotencialesExhi(object):
    """Genera un vocabulario con los potenciales investigadores para esa carpeta"""
    implements(IVocabularyFactory)

    def __call__(self, context):
        acl_users = getToolByName(context, 'acl_users')
        try:
            miColeccion=context.coleccionR[0].to_object
            idGAsign=IColecGroupName(miColeccion).groupName
        except:
            print "No se puedo asignar IColectGroupName"
            return SimpleVocabulary([SimpleVocabulary.createTerm("", str(""), "")])
        idGPot=idGAsign.replace("_g",PREFIJO_COOR_POTENCIAL)

        grupoPot= acl_users.getGroupById(idGPot)
        grupoAsignado=acl_users.getGroupById(idGAsign)

        terms = []
        listIds=[]
        if grupoPot is not None:
            for member_id in grupoPot.getMemberIds()+grupoAsignado.getMemberIds():
                if member_id not in listIds:
                    user = acl_users.getUserById(member_id)
                    if user is not None:
                        member_name = user.getProperty('fullname') or member_id
                        listIds.append(member_id)
                        terms.append(SimpleVocabulary.createTerm(member_id, str(member_id), member_name))

            return SimpleVocabulary(terms)
            
        #devulve un registro vacio
        return SimpleVocabulary([SimpleVocabulary.createTerm("", str(""), "")])



GroupMembersVocabFactory = GroupMembers("listaCords")
InvestigadoresVocabFactory = GroupPotenciales()
CuradoresVocabFactory = GroupPotencialesExhi()
