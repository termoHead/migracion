# -*- coding: utf-8 -*-
__author__ = 'Paul'
from arcas.content import _
from plone.app.textfield import RichText
from zope import schema
from plone.dexterity.content import Container
from plone.app.textfield import RichText
from Products.CMFCore.utils import getToolByName
import z3c.form.field
from plone.namedfile.interfaces import IImageScaleTraversable
from plone.namedfile.field import NamedBlobImage
from plone.directives import form
from Products.validation.interfaces.IValidator import IValidator
from Products.validation import validation
from z3c.form import validator
from zope.interface import Invalid
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from plone.indexer import indexer
from plone.z3cform.textlines.textlines import TextLinesFieldWidget
tiposVocab = SimpleVocabulary(
    [SimpleTerm(value=u'articulo', title='Artículo'),
     SimpleTerm(value=u'ponencia', title='Ponencia'),
     SimpleTerm(value=u'libro', title='Libro'),
     SimpleTerm(value=u'compilacion', title='Compilación'),
     SimpleTerm(value=u'cap', title='Capítulo de libro'),
     SimpleTerm(value=u'tesis', title='Tesis'),
     SimpleTerm(value=u'resena', title='Reseña'),
     SimpleTerm(value=u'entrada', title='Entrada de Blog'),
     SimpleTerm(value=u'trad', title='Traducción'),
     SimpleTerm(value=u'audio', title='Audio'),
     SimpleTerm(value=u'video', title='Video')]
)



def isValidURL(value):
    if value.find("http://")==0 and value.find("https://")==0:
        return True
    else:
        raise Invalid(_(u"Por favor ingrese un una url que incluya HTTP o HTTPS"))

class ISugerencia(form.Schema):
    """
    Sugerencia de lectura que complementa una colección o una exhibición
    """
    title = schema.TextLine(
        title=u"Cita",        
        required=False,
    )
    
    form.omitted('description')
    description = schema.Text(
        title=u"Año de publicacion",        
        required=False,
    )
    
    tipoMedio = schema.Choice(
        title=u"Tipo de sugerencia",
        vocabulary=tiposVocab,
        required=True,
    )

    form.widget(autores=TextLinesFieldWidget)
    autores = schema.List(
        title=u"Autores o responsables",
        description=u"Cargar un autor por linea",
        required=False,
        default=[],
        value_type=schema.TextLine(),
    )

    urlRemoto= schema.TextLine(
        title=u"Enlace externo",
        description=u"Enlace. debe incluir el http://",
        required=False,
        constraint=isValidURL,
    )


@indexer(ISugerencia)
def remoteURLIndexer(context):
    return context.urlRemoto


from Acquisition import aq_inner
from plone.directives.dexterity import DisplayForm
from arcas.content.behaviors import IColecGroupName
from Acquisition import aq_parent, aq_inner
from Products.Five import BrowserView

class View(BrowserView):

    def dameIcon(self):
        """Devuelve un icono segun el tipo elegido"""
        if self.context.tipoMedio==u"imagen":
            return "imagen_icon.gif"
        elif self.context.tipoMedio==u"audio":
            return "audio_icon.gif"
        elif self.context.tipoMedio==u"texto":
            return "text_icon.gif"
        elif self.context.tipoMedio==u"video":
            return "video_icon.gif"
        elif self.context.tipoMedio==u"web":
            return "web_icon.gif"
        elif self.context.tipoMedio==u"resena":
            return "resena_icon.gif"
        elif self.context.tipoMedio==u"articulo":
            return "articulo_icon.gif"


    def colecNmbre(self):
        """Nombre de la coleccion"""
        parentO=aq_parent(aq_inner(self.context))
        if parentO.title=="Estudios":
            return aq_parent(parentO).title
        else:
            return parentO.title