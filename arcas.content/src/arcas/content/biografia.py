# -*- coding: utf-8 -*-
__author__ = 'Paul'
from arcas.content import _
from plone.app.textfield import RichText
from plone.namedfile.field import NamedBlobImage
from plone.directives import form
from Acquisition import aq_parent
from plone.directives.dexterity import DisplayForm

class IBiografia(form.Schema):
    """Biografía de un personaje
    """

    cuerpo = RichText(
        title=_(u"Texto principal"),
        required=True,
    )
    produccion = RichText(
        title=_(u"Obras o datos relevante"),
        description=_(u"Listar las obras/acciones/hitos más relevantes del artista"),
        required=True,
    )

class View(DisplayForm):
    
    def dameColeccionNombre(self):
        padre=aq_parent(self.context)

        return padre.Title()