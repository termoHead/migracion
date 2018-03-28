# -*- coding: utf-8 -*-
__author__ = 'Paul'
#from five import grok
from arcas.content import _
from arcas.content.config import URL_GREENSTON_DOC
from arcas.content.eventos import PREFIJO_COOR_GROUP
from arcas.content.behaviors import IColecGroupName
from plone.app.vocabularies.users import UsersSource
from plone.memoize.instance import memoize
from zope.i18n import translate
from zope.i18nmessageid import MessageFactory
from zope.interface import implements

from zope.schema.interfaces import IContextSourceBinder
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from Acquisition import aq_get
import unicodedata
from Products.CMFCore.utils import getToolByName
from arcas.content.exhibicion import IExhibicion
from arcas.content.categoria import ICategoria

#from  arcas.content.curador import ICurador

from Acquisition import aq_inner
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
from zope.security import checkPermission
from zc.relation.interfaces import ICatalog
from Products.CMFPlone.utils import safe_unicode
from plone.directives import form
try:
    from arcas.content.coleccion import IColeccion
except:
    IColeccion=form.Schema

class TextoUtils(object):
    """Herramientas para recortar o manipular textos"""

    def cortaTexto(self, texto, numcaracteres):
        sacar =("de","la","las","lo","los","para","por","y")
        if texto.find(".") > numcaracteres:                    
            tmpd= texto[:texto[:numcaracteres].rfind(" ")]
            laspalabra=tmpd[tmpd.rfind(" ")+1:]
            if laspalabra in sacar:
                tmpd=tmpd[:tmpd.rfind(" ")]
            textoNuevo=tmpd+"..."
        else:
            textoNuevo=texto[:texto.find(".")+1]
        return textoNuevo
        

class ColeccionesPorCategoria(object):
    ###Devuleve una lista de Categorias, con sus respectivas colecciones"""
    def __init__(self,contexto):
        self.context=contexto
        
    def __call__(self,context):
        return self._data(context)
    
    def _data(self,contexto):
        """devuleve los resultados de la base"""
        catalogo = getToolByName(contexto, 'portal_catalog', None)
        queryColecciones= dict(object_provides=IColeccion.__identifier__)
        queryCategorias = dict(object_provides=ICategoria.__identifier__)
        colecciones=catalogo(queryColecciones)
        colLista=[]
        results=[]
        for brain in colecciones:
            col=contexto.unrestrictedTraverse(brain.getPath())
            try: 
                pp=col.tipoColeccion
            except:
                pp="Autor"
                
            colLista.append({'titulo':brain.Title,'descri':brain.Description,'url':brain.getURL(),'tipoColeccion':pp,'id':col.id,"urlGS":col.GS_ID})
            
        
        catQes=catalogo(queryCategorias)
        for elem in catQes:
            cat=contexto.unrestrictedTraverse(elem.getPath())
            tmpR=filter(lambda col: col['tipoColeccion'] == self.elimina_tildes(elem.Title.decode('utf8')), colLista)
            if(len(tmpR)>0):                
                try:
                    imagen=cat.ilustra
                except:
                    imagen="catGenerica.jpg"                    
                results.append({"categoria":elem.Title,"color":cat.color,"ilustra":imagen,"url":elem.getPath(),"colecciones":tmpR})
        
        return results
    
    def elimina_tildes(self,s):
        return ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))

class CatColecVocabulary(object):
    implements(IVocabularyFactory)
    def __call__(self,context):
        items = []

        site = context
        return self._data(site)
    
    def _data(self,contexto):
        """devuleve los resultados de la base"""
        catalogo = getToolByName(contexto, 'portal_catalog', None)
        query = dict(object_provides=ICategoria.__identifier__)
        result=[]
        for cate in catalogo(query):                 
            cat=contexto.unrestrictedTraverse(cate.getPath())           
            tituC=self.elimina_tildes(cate.Title.decode('utf8'))     
            
            result.append(SimpleTerm(tituC,tituC))
        return SimpleVocabulary(result)
    
    
    def elimina_tildes(self,s):
        return ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))
    
CatColeccionesVocabFactory = CatColecVocabulary()

class CanalesVocabulary(object):
    implements(IVocabularyFactory)

    def __call__(self,context):
        items = []

        site = context
        return self._data(site)

    @memoize
    def _data(self,contexto):
        """devuleve los resultados de la base"""

        catalogo = getToolByName(contexto, 'portal_catalog', None)
        query = dict(object_provides=IExhibicion.__identifier__)
        result=[]
        for folder in catalogo(query):
            titulito=self.elimina_tildes(folder.Title.decode('utf8'))
            idcito=folder.id
            urlito=folder.getPath()
            result.append(SimpleTerm(urlito,idcito))
        return SimpleVocabulary(result)

    def elimina_tildes(self,s):
        return ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))

ExhibicionesVocabFactory = CanalesVocabulary()





class GroupMembers(object):
    """Context source binder to provide a vocabulary of users in a given
    group.
    """
    implements(IVocabularyFactory)

    def __init__(self, group_name):
        self.group_name = group_name

    def __call__(self, context):
        acl_users = getToolByName(context, 'acl_users')
        group = acl_users.getGroupById(self.group_name)
        terms = []

        if group is not None:
            for member_id in group.getMemberIds():
                user = acl_users.getUserById(member_id)
                if user is not None:
                    member_name = user.getProperty('fullname') or member_id
                    terms.append(SimpleVocabulary.createTerm(member_id, str(member_id), member_name))

        return SimpleVocabulary(terms)

GroupMembersVocabFactory = GroupMembers("Staff")
#CategoriasVocabFactory = CategoriasVocab()







class ExhibicionUtils(object):
    """utilidades para las exhibiciones"""

    def __init__(self,colec):        
        self.exhibicion=colec
        self.colecPosta=colec.coleccionR[0].to_object
        self.mt = getToolByName(colec, 'portal_membership')
        
    
    def dameCoordinadores(self):
        """Devuelve los coordinadores de la colección"""
        listResult=[]
        idsCoords=self.buscameEn(self.colecPosta,"coordinador")

        for idm in idsCoords:
            
            listResult.append({
                                'type' : 'user',
                                'id'   : idm["id"],
                                'nombre': idm["nombre"] or idm["id"],
                                'email': idm["email"],
                                'img'  : self.mt.getPersonalPortrait(id=idm['id']),
                             })
        return listResult
    
    def dameCuradores(self):
        """Devuelve los curadores de la Exhibivión"""
        listResult=self.buscameEn(self.exhibicion,"curador")
        return listResult
    
    def dameColaboradores(self):
        """Devuleve los integrantes de una exhibición"""        
        listResult=self.buscameEn(self.exhibicion,"integrantes")
        return listResult
    
    def buscameEn(self, obj, campo):
        listResult=[]
        idsCuras=getattr(obj,campo)
        for idm in idsCuras:
            chabon = self.mt.getMemberById(idm)
            listResult.append({'type' : 'user',
                             'id'   : chabon.id,
                             'nombre': chabon.getProperty('fullname', None) or chabon.id,
                             'email': chabon.getProperty('email'),
                             'img'  : self.mt.getPersonalPortrait(id=chabon.id),
                             })
        return listResult

class ColeccionUtils(object):

    def __init__(self,colec):
        self.coleccion=colec
        
        
        

    def getUrlAFuente(self):
        """devuelv la dirección a la fuente primaria"""
        coleccion=self.coleccion
        baseURL=URL_GREENSTON_DOC+coleccion.GS_ID+"/browse/CL1"
        return baseURL


    def getCoordinadores(self):
        """Devuelve los curadores de la coleción"""
        coleccion=self.coleccion       
        idsCoords=coleccion.coordinador        
        mt = getToolByName(self.coleccion, 'portal_membership')        
        infoCoor = []        
        for idm in idsCoords:
            coordina = mt.getMemberById(idm)
            infoCoor.append({'type' : 'user',
                             'id'   : coordina.id,
                             'title': coordina.getProperty('fullname', None) or coordina.id,
                             'email': coordina.getProperty('email'),
                             'img'  : mt.getPersonalPortrait(id=coordina.id),
                             })
        return infoCoor
        
        
        
        
        
        """
        idG=self.dameGrupo(coleccion).replace("_g",PREFIJO_COOR_GROUP)

        groups_tool = getToolByName(self.coleccion, 'portal_groups')
        mtool = getToolByName(self.coleccion, 'portal_membership')

        try:
            grupoObj=groups_tool.getGroupById(idG)
        except :
            print "La vista intenta buscar un grupo: %s, que no existe" %idG
            return None

        infoCoor = []
        userssource = UsersSource(grupoObj)

        for coordina in grupoObj.getGroupMembers():
            infoCoor.append({'type' : 'user',
                             'id'   : coordina.id,
                             'title': coordina.getProperty('fullname', None) or coordina.id,
                             'email': coordina.getProperty('email'),
                             'img'  : mtool.getPersonalPortrait(id=coordina.id),
                             })
        return infoCoor
        """
        
    def dameGrupo(self,colec):
        colec=self.coleccion
        ppa=IColecGroupName(colec)
        return ppa.groupName



    def dameCurador(self,idExhi):
        """devuelve el curador de una coleccion en lista"""

        coleccion=self.coleccion
        ls=[]
        catalogo=getToolByName(coleccion,"portal_catalog")
        membert=getToolByName(coleccion,"portal_membership")
        memberdat=getToolByName(coleccion,"portal_memberdata")

        try:
            brain=catalogo.searchResults({"id":idExhi})[0]
        except:
            return None

        miExhiOb=coleccion.unrestrictedTraverse(brain.getPath())
        curadores=miExhiOb.curador

        for curador in curadores:
            if curador:
                persona =membert.getMemberById(curador)
                portrait=memberdat._getPortrait(curador)
            else:
                return None

            dC={"nombre":persona.getProperty('fullname'),
                "mail":persona.getProperty('email'),
                "portrait":portrait}
            ls.append(dC)

        return ls

        #result  =catalogo(query)
        """
        for elem in result:
            try:
                miOb=coleccion.unrestrictedTraverse(elem.getPath())
                ls.append(miOb)
            except :
                print "error al buscar el curador"

        return ls
        """

    def dameIntegrantes(self):
        coleccion=self.coleccion
        idG=self.dameGrupo(coleccion)

        groups_tool = getToolByName(self.coleccion, 'portal_groups')
        mtool = getToolByName(self.coleccion, 'portal_membership')

        try:
            grupoObj=groups_tool.getGroupById(idG)
        except :
            print "La vista intenta buscar un grupo: %s, que no existe" %idG
            return None

        infoCoor = []
        userssource = UsersSource(grupoObj)

        for integrante in grupoObj.getGroupMembers():
            infoCoor.append({'type' : 'user',
                             'id'   : integrante.id,
                             'title': integrante.getProperty('fullname', None) or integrante.id,
                             'email': integrante.getProperty('email'),
                             'img'  : mtool.getPersonalPortrait(id=integrante.id),
                             })
        return infoCoor

    def dameExhibicionesR(self):
        try:
            ljo=self.back_references(self.coleccion,"coleccionR")
        except:
            return None
        return ljo

    def back_references(self,source_object, attribute_name):
        """ Return back references from source object on specified attribute_name """
        catalog = getUtility(ICatalog)
        intids = getUtility(IIntIds)
        result = []
        try:
            for rel in catalog.findRelations(
                dict(to_id=intids.getId(aq_inner(source_object)),
                    from_attribute=attribute_name)  ):

                obj = intids.queryObject(rel.from_id)
                if obj is not None and checkPermission('zope2.View', obj):
                    result.append(obj)
        except:
            print "no hay referencias cargadas"

        return result