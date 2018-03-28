# -*- coding: utf-8 -*-
__author__ = 'Paul'
import suds
import urllib2
import codecs
import xml.etree.ElementTree as ET

from zope.component import getMultiAdapter
from zope.interface import Interface
from zope.schema import Text, TextLine, Field
from zope.component import getMultiAdapter
from zExceptions import Forbidden
from suds.client import Client
from Products.Five.browser import BrowserView
from suds.xsd.doctor import ImportDoctor, Import
from suds.plugin import MessagePlugin
from Products.CMFPlone.utils import safe_unicode
from Products.CMFCore.utils import getToolByName
from arcas.content.coleccion import IColeccion
from Acquisition import aq_inner
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
from zope.security import checkPermission
from zc.relation.interfaces import ICatalog
from arcas.content.utils import ColeccionUtils
import json


class IListadoColeccion(Interface):
    """interfaz de la vista"""

class ListadoColeccion(BrowserView):
    """Vista del Listado de colecciones"""

    def __init__(self, context, request):
        self.context    =context
        self.request    =request

    def dameListaColecciones(self):
        """Devuelve una Lista con dicccionario de cada coleccion"""
        context = self.context.aq_inner
        catalogo=getToolByName(self.context,"portal_catalog")
        portal_state = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        portal=portal_state.portal()
        result=catalogo(object_provides=IColeccion.__identifier__)
        listados=[]
        for colec in result:
            miOb=context.unrestrictedTraverse(colec.getPath())
            listados.append({
                "titulo":colec.Title,
                "descri":colec.Description,
                "url":colec.getURL(),
                "img":miOb.imagenLista
            })
        return listados


class BuscarExhibiciones(BrowserView):
    """Una vista para mostrar exhibiciones de una determinada coleccion"""

    def __init__(self, context, request):
        self.context    =context
        self.request    =request
        self.idCol  =request.form["idCol"]
        self.portal_transforms = getToolByName(self.context, 'portal_transforms')
		
    def dameListaExhib(self):
        miColeBrain=self.dameColeccionById(self.idCol)

        if len(miColeBrain)>0:
            miColeBrain=miColeBrain[0]
        else:
            return []
        if miColeBrain:
            listados=[]
            miColObj=self.context.unrestrictedTraverse(miColeBrain.getPath())

            ppa=ColeccionUtils(miColObj)
            resulta=ppa.back_references(miColObj,'coleccionR')

            for exhi in resulta:
                listados.append({
                    "titulo"    :exhi.Title(),
                    "descri"    :exhi.Description(),
                    "url"       :exhi.absolute_url(),
                    "coors"     :ppa.getCoordinadores(),
                    "idColec"   :miColObj.id,
                    "urlFuente" :ppa.getUrlAFuente(),
                    "curador":  ppa.dameCurador()
                })
            return listados
        else:
            return result

    def dameNomColeccion(self):
        """Devuelve el título de la coleccion"""
        col=self.dameColeccionById(self.idCol)
        return col[0].Title

    def dameColeccionById(self,idCol):
        """Devuelve una coleccion"""

        catalogo=getToolByName(self.context,"portal_catalog")
        query={'getId':idCol,'portal_type':'arcas.coleccion'}
        result=catalogo(query)
        return result
        
class RedidectionView(BrowserView):
    """Una vista para saltear el root folder"""
    
    
    def __call__(self):        
        contextURL = self.context.absolute_url()                
        self.request.response.setHeader("Content-Type", "text/html")
        self.request.response.redirect(contextURL+"/portada")
        return ""
    
    def redirect(self):
        contextURL = self.context.absolute_url()                
        self.request.response.setHeader("Content-Type", "text/html")        
        return self.request.response.redirect(contextURL+"/portada")
        
        
class DocumentView(BrowserView):
    """Reemplazo del la vista original de DocumentView"""

    def __init__(self, context, request):
        self.context    =context
        self.request    =request

    def dameCuerpo(self):
		contenido=self.context.getText()
		return contenido
    def dameSeccion(self):
		return aq_parent(self.context)
		
    def dameSeccion(self):
		"""Devuelve el titulo Noticias si esta dentro de la secciòn noticias
		si no, el title del parent"""
		if "noticias" in self.context.getPhysicalPath():
			return "Noticias"
		else:
			padre=self.context.aq_parent
			return padre.title
		
		
    def dameImagenes(self):
		from lxml import etree
		from lxml.html import fromstring, tostring
		contenido=self.dameCuerpo()
		descri=self.context.Description()
		#data = self.portal_transforms.convertTo('text/html', text, mimetype='text/-x-web-intelligent')
		#html = data.getData()
		parseado=etree.HTML(contenido)
		listaEnlaces=[{"src":elem.get("src"),"width":elem.get("width"),"height":elem.get("height")} for elem in parseado.xpath("//img")]
		texto=""
		for element in parseado.iter("*"):
			if element.text!=None and element!="":
				if element.tag!="img":
					texto+=element.text.encode('latin1')
					
		return texto,listaEnlaces,descri
		
	