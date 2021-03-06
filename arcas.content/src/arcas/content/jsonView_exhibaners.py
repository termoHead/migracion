from Products.Five.browser import BrowserView

from Products.CMFCore.interfaces import ISiteRoot
from zope.interface import Interface
from Acquisition import aq_inner, aq_parent
from plone.app.layout.navigation.interfaces import INavigationRoot
from Products.CMFCore.utils import getToolByName
from arcas.content.utils import ColeccionUtils
import json

import socket
import urllib
import urllib2
from urllib2 import HTTPError
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


class JSONExhibicionesList(BrowserView):
    """
        Devuelve una JSON con los valores para poner un banner de una exhibicion
        espera el paramtreo colecid=nombrecolecicon
    """
    def update(self,idColeccion="puig"):    
        self.contexto= aq_inner(self.context)        
        if self.request.form.has_key("colecid"):
            idColeccion=self.request.form["colecid"]

        self.idColeccion=idColeccion

    def __call__(self):
        
        listing = self.datos_contexto()
        pretty  = json.dumps(listing)
        self.request.response.setHeader("Content-type", "application/json")
        self.request.response.setHeader('Access-Control-Allow-Origin', '*')
        return pretty

    def datos_contexto(self):
        self.update()
        catalogo=getToolByName(self.contexto,"portal_catalog")
        colecFolder=catalogo.searchResults(portal_type="arcas.coleccionesFolder")

        if len(colecFolder)<1:
            return self.emptyData()

        miColeccion=""

        colectFolder=self.context.unrestrictedTraverse(colecFolder[0].getPath())
        desta_path = '/'.join(colectFolder.getPhysicalPath())
        cataloDest=catalogo.searchResults(path={'query':desta_path , 'depth': 1})

        for coleccion in cataloDest:
            colecObj=self.context.unrestrictedTraverse(coleccion.getPath())
            if colecObj.GS_ID==self.idColeccion:
                miColeccion=colecObj
                break

        if miColeccion=="":
            return self.emptyData()

        utilidad= ColeccionUtils(miColeccion)
        result=[]

        for exhi in utilidad.dameExhibicionesR():
            data={'url':exhi.absolute_url()+'/images/baner','titulo':exhi.title,'remoteURL':exhi.absolute_url()}
            result.append(data)
            
        return result

    def emptyData(self):
        data = dict(
            title="",
            url="",
            text="",
            available=False,
        )
        return data




