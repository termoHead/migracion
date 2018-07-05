# -*- coding: utf-8 -*-
__author__ = 'Paul'
"""Behaviours to assign tags (to ideas).

Includes a form field and a behaviour adapter that stores the data in the
standard Subject field.
"""

from rwproperty import getproperty, setproperty

from zope.interface import implements, alsoProvides
from zope.component import adapts
from zope import schema
from plone.directives import form
from arcas.content import _

try:
    from arcas.content.coleccion import IColeccion
except:
    IColeccion=form.Schema
    
from Acquisition import aq_inner, aq_base
from z3c.relationfield.schema import RelationChoice
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.app.textfield import RichText
from z3c.form import button
from plone.autoform.interfaces import IFormFieldProvider
from plone.namedfile.field import NamedBlobImage,NamedBlobFile

from zope.interface import provider
ID_SET=""

from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from z3c.form import action

tiposDeSeccion = SimpleVocabulary(
    [SimpleTerm(value=u'biografia', title=_(u'Biografía')),
     SimpleTerm(value=u'galeria', title=_(u'Galeria imágenes')),
     SimpleTerm(value=u'imagen', title=_(u'Una imagen')),
     SimpleTerm(value=u'texto', title=_(u'Texto')),
     SimpleTerm(value=u'video', title=_(u'Video')) ]
    )
    
class IColecGroupName(form.Schema):
    """Add tags to content
    """
    form.fieldset(
        'responsables',
        u"Responsables",
        fields=['groupName'],
    )
    groupName= schema.TextLine(
        title=_(u"Nombre del grupo"),
        description=_(u"La coleccion tiene asociado un grupo de usuarios, este campo define el nombre de dicho grupo"),
        required=False,
        default=u"sinNombre"
    )




class IColDerSeccion(form.Schema):
    """Campos para gestionar una sección"""
    form.fieldset('columnaDer', label=u"Col. derecha Sec1",
                  fields=['tipoSecc1','titulo1', 'textoSeccion1', 'ria1','picture1']
                  )
    form.fieldset('colDerecha', label=u"Col. derecha Sec2",
                  fields=['tipoSecc2','titulo2', 'textoSeccion2', 'ria2','picture2']
                  )
    
    tipoSecc1 = schema.Choice(
            title=_(u"Tipo de seccion"),
            description=_(u"Elija un tipo para esta sección"),
            vocabulary=tiposDeSeccion,
            required=False,
        )
    titulo1= schema.TextLine(
        title=_(u"Título de la sección 1"),
        description=_(u"Título que encabeza la sección de la columna derecha. Puede estar vacío y no se mostrará nada"),
        required=False,        
    )
    textoSeccion1 = RichText(
        title=_(u"Texto de las sección 1"),
        required=False,
    )
    ria1 = NamedBlobFile(
        title=_(u"Suba un video"),
        required=False,
    )
    picture1 = NamedBlobImage(
        title=_(u"Suba la imagen"),
        required=False,
    )
    tipoSecc2 = schema.Choice(
            title=_(u"Tipo de seccion"),
            description=_(u"Elija un tipo para esta sección"),
            vocabulary=tiposDeSeccion,
            required=False,
        )
    titulo2= schema.TextLine(
        title=_(u"Título de la sección 2"),
        description=_(u"Título que encabeza la sección de la columna derecha. Puede estar vacío y no se mostrará nada"),
        required=False,        
    )
    textoSeccion2 = RichText(
        title=_(u"Texto de las sección 2"),
        required=False,
    )
    ria2 =   NamedBlobFile(
        title=_(u"Suba un video"),
        required=False,
    )
    picture2 = NamedBlobImage(
        title=_(u"Suba la imagen"),
        required=False,
    )
    

        
        


#@form.default_value(field = IColecGroupName['groupName'],context=IColeccion)
#def excludeFromNavDefaultValue(data):
#    return data.groupName

alsoProvides(IColecGroupName, IFormFieldProvider)
alsoProvides(IColDerSeccion, IFormFieldProvider)
class ColecGroupName(object):
    """Store tags in the Dublin Core metadata Subject field. This makes
        tags easy to search for."""
    
    implements(IColecGroupName)
    adapts(IColeccion)
    
    def __init__(self, context):
        self.seteado=0
        self.context = context


    @getproperty
    def groupName(self):
            try:
                return self.context.aq_base.id+"_g"
            except :
                return "sinNombre"


    @setproperty
    def groupName(self, value):
        if value is None:
            value = ()
        self.context.groupName=value
