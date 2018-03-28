# -*- coding: utf-8 -*-
__author__ = 'Paul'
from arcas.content import _
from zope import schema
from plone.app.textfield import RichText
from plone.directives import form
from plone.namedfile.field import NamedBlobImage


from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from arcas.content.config import COLOR_COLECCION



class ICategoria(form.Schema):
    """A conference program. Programs can contain Sessions."""
    color = schema.Choice(
        title=u"Color",
        description=u"El color que identifica esta categoría.",
        vocabulary=COLOR_COLECCION,
    )

    #ilustra=NamedBlobImage(
    #    title=_(u"Imagen"),
    #    description=_(u"Una imagen que ilustra la categoria en la home"),
    #    required=False,
    #)
