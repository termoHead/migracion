# -*- coding: utf-8 -*-
__author__ = 'Paul'
from arcas.content import  _


from plone.app.textfield import RichText
from zope import schema
from plone.dexterity.content import Container
from plone.app.textfield import RichText

import z3c.form.field
from plone.namedfile.interfaces import IImageScaleTraversable
from plone.namedfile.field import NamedBlobImage
from plone.directives import form
from arcas.content.coleccion import IColeccion
from arcas.content.config import URL_GREENSTON_DOC
from arcas.content.utils import ColeccionUtils
import unicodedata

class IColeccionesFolder(form.Schema):
    """Carpeta que guarda colecciones"""

    cuerpo = RichText(
        title=_(u"Texto principal"),
        required=False,
    )


from Acquisition import aq_inner
from plone.directives.dexterity   import DisplayForm
from plone.app.vocabularies.users import UsersSource
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView

class ColeccionesView(BrowserView):
    #grok.context(IColeccionesFolder)
    #grok.require('zope2.View')
    #grok.name('view')
    #grok.template('templates/colecFolder.pt')
    def dameCuerpo(self):
        try:
            txt=self.context.cuerpo.output
        except:
            return None
        return txt
        
    def dameCategorias(self):
        """Devuelve un listado de categorias"""        
        self.contexto = self.context.aq_inner
        self.catalogo=getToolByName(self.contexto,"portal_catalog")
        brains=self.catalogo(path={ "query": "/arcas/categorias" }, sort_order="ascending")
        colecciones=self.dameListaColecciones()        
        ls=[]
        
        
        for brain in brains:
            
            if brain.id!="categorias":
                titCat=brain.Title
                micate={"categoria":titCat,"descri":brain.Description,"color":brain.getObject().color,"listado":[]}
                
                for coleccion in colecciones:                    
                    if self.elimina_tildes(coleccion["categoria"]) == self.elimina_tildes(titCat.decode('utf8')):
                        micate["listado"].append(coleccion)
                        
                ls.append(micate)
        return ls

    def elimina_tildes(self,s):
        return ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))
    
    def dameListaColecciones(self):
        """Devuelve una Lista con dicccionario de cada coleccion"""        
        result=self.catalogo(object_provides=IColeccion.__identifier__)

        listados=[]
        for colec in result:
            miOb=self.contexto.unrestrictedTraverse(colec.getPath())
            colUtils=ColeccionUtils(miOb)
            descrip=colec.Description
            if len(descrip)>280:
                descrip=descrip[:descrip[:280].rfind("</p>")]+"."
                
            listados.append({
                "titulo":colec.Title,
                "descri":descrip,
                "url":colec.getURL(),
                "scales":miOb,
                "coors":colUtils.getCoordinadores(),
                "idColec":miOb.GS_ID,
                "categoria":colec.getObject().tipoColeccion,
                "urlFuente":colUtils.getUrlAFuente(),
                "altFuente":miOb.altNavegarFuente,}
                )

        return listados


