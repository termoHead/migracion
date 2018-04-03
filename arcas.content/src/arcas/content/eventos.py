# -*- coding: utf-8 -*-
__author__ = 'Paul'
from arcas.content import _
from zope.lifecycleevent.interfaces import IObjectAddedEvent
from Products.CMFCore.utils import getToolByName
from plone.dexterity.utils import createContentInContainer
from Products.ATContentTypes.lib import constraintypes
from zope.container.interfaces import INameChooser
from Products.CMFCore.WorkflowCore import WorkflowException
from zope.component.hooks import getSite
from arcas.content.behaviors import IColecGroupName
import logging
from plone.app.vocabularies.users import UsersSource
from plone.app.vocabularies.groups import GroupsSource
from AccessControl.interfaces import IRoleManager
logger = logging.getLogger("Plone")
from Products.PluggableAuthService.interfaces.events import IPASEvent
from Products.CMFCore.permissions import setDefaultRoles
from Products.Archetypes.utils import shasattr # To avoid acquisition
PREFIJO_COOR_GROUP="_coor"
PREFIJO_COOR_POTENCIAL="_pot"

import transaction
carpetasDict=[
    {"id":"gale","titulo":"Galería","tipo":"Folder","constraint":["Image"],"descri":"Imágenes que se muestran como galeria de la colección"},
    {"id":"estudios","titulo":"Estudios","tipo":"Folder","constraint":["arcas.sugerencia"],"descri":"Toda la información complementaria a la colección"},
]
exhibiDict=[
    {"id":"enlace","titulo":"Enlaces","tipo":"Folder","constraint":["arcas.exhibicion","Document"],"descri":"Información complementaria"},
]
#HANDLER COLECCIONES
def onSetupColeccion(colectObj, event):
    """ """
    workflowTool = getToolByName(colectObj, "portal_workflow")
    flag=0
    if event.action == 'setUp':
        #event.object.setLayout('publish_view')
        for carpeta in carpetasDict:
            newId="%s_%s" %(colectObj.id,carpeta["id"])

            if not hasattr(colectObj,newId):
                oid=colectObj.invokeFactory(carpeta["tipo"], id=newId)
                transaction.savepoint(optimistic=True)
                new_obj = colectObj[oid]
                new_obj.setTitle(carpeta["titulo"])
                new_obj.setDescription(carpeta["titulo"])

                #
                # Habilita el filtrado de tipos de contenidos
                #
                ENABLED = 1
              

                try:
                    workflowTool.doActionFor(new_obj, "publish")
                    logger.info("Estado cambiado!")
                except WorkflowException:
                    # a workflow exception is risen if the state transition is not available
                    # (the sampleProperty content is in a workflow state which
                    # does not have a "submit" transition)
                    logger.info("Could not publish:" + str(new_obj.getId()) + " already published?")
                    pass
                    
                new_obj.reindexObject()
                
                if shasattr(new_obj, 'canSetConstrainTypes'):
                    new_obj.setConstrainTypesMode(constraintypes.ENABLED)
                    # Types for which we perform Unauthorized check
                    new_obj.setLocallyAllowedTypes(carpeta["constraint"])
                    # Add new... menu  listing
                    new_obj.setImmediatelyAddableTypes(carpeta["constraint"])
                else:
                    from Products.CMFPlone.interfaces import ISelectableConstrainTypes
                    constraints = ISelectableConstrainTypes(new_obj)
                    constraints.setConstrainTypesMode(ENABLED)
                    constraints.setLocallyAllowedTypes(carpeta["constraint"])
                    
                    
                flag=flag+1
            else:
                print "la carpeta estaba creada"
    else:
        print "la accion no es SetUp"


def onModificaColeccion(colectObj,event):
    """Listener para la modificación de una coleccion"""
    infoCoor = []
    infoInvest=[]
    groups_tool = getToolByName(colectObj, 'portal_groups')
    acl_users   = getToolByName(colectObj, 'acl_users')
    userssource = UsersSource(colectObj)
    
    if hasattr(colectObj, "coordinador"):
        coors=colectObj.coordinador
        for cor in coors:
            user=userssource.get(cor)
            user_id=cor
            infoCoor.append({'type': 'user',
                         'id': user_id,
                         'title': user.getProperty('fullname', None) or user.getId(),
                         'roles': ["Contributor",],
                         })
            

    if hasattr(colectObj, "integrantes"):
        integrantes=colectObj.integrantes
        for integrante in integrantes:
            user=userssource.get(integrante)
            user_id=integrante
            infoInvest.append({'type': 'user',
                             'id': user_id,
                             'title': user.getProperty('fullname', None) or user.getId(),
                             'roles': ["Contributor"],
                             })

    #asigna el rol de owner al grupo Coordinador con id del id deesta carpeta
    gruposVocab = GroupsSource(colectObj)
    grupIdCooR=dameGroupNameFrom(colectObj).replace("_g",PREFIJO_COOR_GROUP)
    grupIdPot =dameGroupNameFrom(colectObj).replace("_g",PREFIJO_COOR_POTENCIAL)
    groupIdInves=dameGroupNameFrom(colectObj)
    
    try:
        grupoObj=groups_tool.getGroupById(grupIdCooR)
    except :
        print "el grupo %s no existe" %grupIdCooR
        return

    try:
        grupoObjInvest=groups_tool.getGroupById(groupIdInves)
    except :
        print "el grupo %s no existe" %groupIdInves
        return


    #todos los usuarios asignados al grupo de coordinacion
    listUsers=grupoObj.getGroupMembers()
    listInvest=grupoObjInvest.getGroupMembers()

    
    #elimino todos de los grupos grupo
    for userO in listUsers:
        groups_tool.removePrincipalFromGroup(userO, grupIdCooR)
    for userI in listInvest:
        groups_tool.removePrincipalFromGroup(userI, groupIdInves)

        
    #Regenero los grupos con los usuarios actuales
    for userObj in infoCoor:
        groups_tool.addPrincipalToGroup(userObj["id"], grupIdCooR)
        
    for investObj in infoInvest:
        groups_tool.addPrincipalToGroup(investObj["id"], groupIdInves)


def onModificaExhibicion(exhiObj,event):
    """ajusta los roles de la carpeta a los usuarios determinados en Responsables"""
    
    yaSeteados=exhiObj.get_local_roles()
    
    """borro todos los roles menos el del OWNER"""
    for usO in yaSeteados:        
        if "Owner" not in usO[1]:
            exhiObj.manage_delLocalRoles([usO[0]])
        
    """seteo los curadores"""    
    for userid in exhiObj.curador:
        exhiObj.manage_setLocalRoles(userid, ["Manager","Curador"])
    
    """seteo los integrantes"""    
    for userid in exhiObj.integrantes:
        exhiObj.manage_setLocalRoles(userid, ["Contributor",])

def onCreaFolder(folder,evento):
    """Restringe los tipos de contenido dependiendo si objeto es hijo de Coleccion"""
    from Products.ATContentTypes.lib import constraintypes
    from Acquisition import aq_parent, aq_inner

    if aq_parent(folder).portal_type=="arcas.coleccion":
        # Enable contstraining
        folder.setConstrainTypesMode(constraintypes.ENABLED)

        # Types for which we perform Unauthorized check
        folder.setLocallyAllowedTypes(["arcas.sugerencia","Archive","Link","arcas.enlacegs"])

        # Add new... menu  listing
        folder.setImmediatelyAddableTypes(["arcas.sugerencia","Archive","Link","arcas.enlacegs"])


def agregaRolesAGrupo(contexto,groupid,listRoles):
    """Agrega un grupoid con los roles en listRoles a una carpeta"""
    for gs in contexto.aq_base.get_local_roles():
        if gs[0]==groupid:
            return

    if IRoleManager.providedBy(contexto):
        contexto.aq_base.manage_addLocalRoles(groupid, listRoles)

def onSaveColeccion(colecObj, event):
    """Cuando se guarda la coleccion dentro de un contenedor"""
    gst=getSite()
    groups_tool =getToolByName(colecObj,"portal_groups")
    nomGrupo=dameGroupNameFrom(colecObj)
    creaGrupos((nomGrupo,nomGrupo.replace("_g",PREFIJO_COOR_GROUP),nomGrupo.replace("_g",PREFIJO_COOR_POTENCIAL)),groups_tool,colecObj)

def onDelColeccion(obj,evento):
    """Cuando se borra una coleccion"""
    idG=dameGroupNameFrom(obj)
    idGcoor=idG.replace("_g",PREFIJO_COOR_GROUP)
    idGpot=idG.replace("_g",PREFIJO_COOR_POTENCIAL)
    groups_tool =getToolByName(obj,"portal_groups")

    # HAY QUE ELIMINAR de participaEn de cada usuario en el grupo potenciales
    grupoPot=groups_tool.getGroupById(idGpot)

    for idUser in grupoPot.getGroupMembers():
        valorInicial=idUser.getProperty("participaEn")
        nuevoValor=valorInicial.replace(obj.getId(),"")
        listaValores=nuevoValor.split(",")
        listaValores=filter(None,listaValores)
        idUser.setMemberProperties(mapping={"participaEn":''.join(listaValores)})

    groups_tool.removeGroup(idGpot)
    groups_tool.removeGroup(idGcoor)
    groups_tool.removeGroup(idG)


###Profiles Handlers
def onCreaPerfil(evento,obj):
    """nuevo perfil creado"""
    pass

def onModificaPerfil(evento,obj):
    """se paso a un evento en arcas.policy.adapter.on_save"""


    pass


#HANDLER EXHIBICIONES
def onSetupExhibicion(colectObj, event):
    """
    Se dispara cuando cambia el estado en el workflow
    """
    workflowTool = getToolByName(colectObj, "portal_workflow")
    flag=0

    if event.action == 'setUp':
        #event.object.setLayout('publish_view')
        for carpeta in exhibiDict:
            newId="%s_%s" %(colectObj.id,carpeta["id"])

            if not hasattr(colectObj,newId):
                oid=colectObj.invokeFactory(carpeta["tipo"], id=newId)
                transaction.savepoint(optimistic=True)
                new_obj = colectObj[oid]
                new_obj.setTitle(carpeta["titulo"])
                new_obj.setDescription(carpeta["titulo"])
                #
                # Habilita el filtrado de tipos de contenidos
                #
                new_obj.setConstrainTypesMode(constraintypes.ENABLED)
                # Types for which we perform Unauthorized check
                new_obj.setLocallyAllowedTypes(carpeta["constraint"])
                # Add new... menu  listing
                new_obj.setImmediatelyAddableTypes(carpeta["constraint"])

                try:
                    workflowTool.doActionFor(new_obj, "publish")
                    logger.info("Estado cambiado!")
                except WorkflowException:
                    # a workflow exception is risen if the state transition is not available
                    # (the sampleProperty content is in a workflow state which
                    # does not have a "submit" transition)
                    logger.info("Could not publish:" + str(new_obj.getId()) + " already published?")
                    pass
                new_obj.reindexObject()
                flag=flag+1
            else:
                print "la carpeta estaba creada"
    else:
        print "la accion no es SetUp"

###AUXILIARES
def creaGrupos(groupNames,groups_tool,colectObj):
    """Genera los grupos para las colecciones"""
    for groupName in groupNames:
        group_id = groupName
        if groupName=="sinNombre":
            return

        if not group_id in groups_tool.getGroupIds():
            groups_tool.addGroup(group_id)
            miGrupo=groups_tool.getGroupById(group_id)
            
            #asigna roles al grupo
            if group_id.find(PREFIJO_COOR_GROUP)!=-1:
                agregaRolesAGrupo(colectObj,group_id,['Owner',])
                
            if group_id.find("_g")!=-1:
                agregaRolesAGrupo(colectObj,group_id,['Contributor','Reader'])
                
            print "se creo el grupo: %s"%groupName
            
        else:
            
            print "el grupo %s ya existia" %groupName
            #agrego el rol de owner a los coordinadores

def actualizaGrupos(obj):
    """Actualiza usuarios del grupo local"""

def borraGrupos(groupName):
    """Elinima un grupo luego que se borra la carpeta"""
    pass
def dameGroupNameFrom(colecObj):
    """devuleve el campo groupName que esta en un behavior"""
    ppa=IColecGroupName(colecObj)
    return ppa.groupName
