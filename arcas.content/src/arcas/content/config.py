# -*- coding: utf-8 -*-
__author__ = 'Paul'
from arcas.content import _
#La constantea es la base para un documento de greenstone
#luego viene la colección elegida puig y la cadena fija "/document"
#URL_GREENSTON_DOC="http://g3:8383/greenstone3/library/collection/"
URL_GREENSTON_DOC="/greenstone3/library/collection/"

#------------------------
#Dirección de correo que figura como enviador de mails automáticos
#se usan en nuevoItemGs.py y editItem.py
#---------------------------
MAIL_ADMIN= u"admin@arcas.unlp.edu.ar"
#Dirección de correo a quien se envía copia de la edición y creación de 
#Registros Greenstone
MAIL_COORDINADOR= u"mariana@fahce.unlp.edu.ar"
#MAIL_COORDINADOR= u"termo_head@hotmail.com"






#--------------------------
#DATOS para el formulario de edicion y carga | nuevoItemGs.py y editItem.py
#---------------------------
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
TIPOS_COLECCION = SimpleVocabulary(
    [SimpleTerm(value=u'0', title=_(u'Autor')),
     SimpleTerm(value=u'1', title=_(u'Corpus Linguisticos'))]
    )

ISO_IDIOMAS=SimpleVocabulary([
    SimpleTerm(value=u'ay', title=(u'aimara')),
    SimpleTerm(value=u'de', title=(u'alemán')),
    SimpleTerm(value=u'es', title=(u'español (o castellano)')),
    SimpleTerm(value=u'fr', title=(u'francés')),
    SimpleTerm(value=u'el', title=(u'griego (moderno)')),
    SimpleTerm(value=u'gn', title=(u'guaraní')),
    SimpleTerm(value=u'en', title=(u'inglés')),
    SimpleTerm(value=u'it', title=(u'italiano')),
    SimpleTerm(value=u'la', title=(u'latín')),
    SimpleTerm(value=u'pt', title=(u'portugués')),
    SimpleTerm(value=u'qu', title=(u'quechua'))
    ])
 
serieTitle=[u'Titulo',u'Cobertura temporal',u'Extensión',u'Descripción física',u'Autor',u'Alcance',u'Idioma'] 
infoMetadatosSerie={'s_titulo':'ae.serietitulo',
    's_temporal':'ae.seriecoberturatemporal',
    's_extension':'ae.fileextension',
    's_caracteristicas':'ae.seriedescripcionfisica',
    's_autor':'ae.serieautor',
    's_alcance':'ae.seriealcance',
    's_lenguaiso':'ae.serielenguaiso'}

subSerieTitles=[u'Título',u'Alcance',u'Anotación']
infoMetadatoSubSerie={'sub_titulo':'ae.subserietitulo','sub_alcance' :'ae.subserieautor','sub_anotacion':'ae.subserieanotacion'}

itemTitles=[u'Titulo',u'Autor',u'Colaboradores',u'Edición',u'Fecha',u'Lugar',u'Descripción física',u'Dimensiones',u'Idioma',u'Naturaleza',u'Alcance',u'Anotación','Ruta Archivo']

infoMetaItem={ 
    'f_titulo':'ae.itemtitulo',
    'f_autor':'ae.itemautor',
    'f_colaborador':'ae.itemcolaborador',
    'f_edicion':'ae.itemedicion',
    'f_fechaCreacion':'ae.itemcoberturatemporal',
    'f_lugarCreacion':'bi.lugar',
    'f_descFisica':'ae.itemdescripcionfisica',
    'f_dimensiones':'ae.itemdimension',
    'f_idioma':'ae.itemlenguaiso',
    'f_naturaleza':'ae.itemnaturaleza',
    'f_alcance':'ae.itemalcance',
    'f_anotacion':'bi.anotacionitem',
    'f_ruta':'bi.ruta',
    }

agenteMetadatos={'f_agentetipo':"ae.agentepersonatipo",'f_agente':"ae.agentepersonanombre"}
#-----------------------------------------------
#Color de las categorias
COLOR_COLECCION = SimpleVocabulary(
    [SimpleTerm(value=u'7494bf', title=_(u'Celeste')),
     SimpleTerm(value=u'586d57', title=_(u'Verde')),
     SimpleTerm(value=u'c4777b', title=_(u'Rosa')),
     SimpleTerm(value=u'dca167', title=_(u'Naranja')),
     SimpleTerm(value=u'e4d68d', title=_(u'Amarillo')),
     SimpleTerm(value=u'97895e', title=_(u'Marron')),
     SimpleTerm(value=u'd5cfa4', title=_(u'Marron claro')),
     ]
    )