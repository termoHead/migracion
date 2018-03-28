# -*- coding: utf-8 -*-
__author__ = 'Paul'
from arcas.content import _

from plone.app.textfield import RichText
from zope import schema
from plone.dexterity.content import Container
from plone.app.textfield import RichText

import z3c.form.field
from plone.namedfile.interfaces import IImageScaleTraversable
from plone.namedfile.field import NamedBlobImage
from plone.directives import form
from arcas.content.exhibicion import IExhibicion
from arcas.content.config import URL_GREENSTON_DOC
from arcas.content.behaviors import IColecGroupName
from arcas.content.eventos import PREFIJO_COOR_GROUP
from arcas.content.utils import ColeccionUtils




class IExhibicionesFolder(form.Schema):
    """Carpeta que guarda colecciones"""

    cuerpo = RichText(
        title=_(u"Texto principal"),
        required=False,
    )

from Acquisition import aq_inner
from plone.directives.dexterity   import DisplayForm
from plone.app.vocabularies.users import UsersSource
from Products.CMFCore.utils import getToolByName
from arcas.content.utils import ColeccionUtils

from Products.Five import BrowserView

class ExhibicionesFolderView(BrowserView):

    def dameListaExhi(self):
        """Devuelve una Lista con dicccionario de cada exhibicion"""
        contexto = self.context.aq_inner
        catalogo=getToolByName(contexto,"portal_catalog")
        result  =catalogo(object_provides=IExhibicion.__identifier__)
        listados=[]
        

        for exhi in result:

            miOb = contexto.unrestrictedTraverse(exhi.getPath())
            if miOb.coleccionR!=None:
                miCol= miOb.coleccionR[0].to_object
                ppa=ColeccionUtils(miCol)

                listados.append({
                    "id":exhi.id,
                    "titulo"    :exhi.Title,
                    "subTitulo" :miCol.Title(),
                    "descri"    :exhi.Description,
                    "url"       :exhi.getURL(),
                    "scales"    :miOb,
                    "coors"     :ppa.getCoordinadores(),
                    "idColec"   :miCol.id,
                    "urlFuente" :ppa.getUrlAFuente(),
                    "curador"   :ppa.dameCurador(exhi.id)
                })

        return listados

