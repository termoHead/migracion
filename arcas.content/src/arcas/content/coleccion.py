# -*- coding: utf-8 -*-
__author__ = 'Paul'
from arcas.content import _
import z3c.form.field
from plone.app.vocabularies.users import UsersSource
from plone.app.textfield import RichText
from zope import schema

from plone.dexterity.content import Container
from plone.dexterity.browser import edit

from plone.namedfile.interfaces import IImageScaleTraversable
from plone.namedfile.field import NamedBlobImage


from plone.autoform import directives
from plone.directives import form

from plone.dexterity.browser.view import DefaultView

from z3c.relationfield.schema import RelationList, RelationChoice
import unicodedata
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from z3c.form.interfaces import HIDDEN_MODE, DISPLAY_MODE, INPUT_MODE

from Acquisition import aq_inner

from Products.CMFCore.utils import getToolByName
from arcas.content.config import URL_GREENSTON_DOC
from arcas.content.utils import ColeccionUtils

from Products.Five import BrowserView

class IColeccion(form.Schema):
    """Esquema básico de la colección. 
       En behaviors se implementan la customización de las columnas"""
    
    form.fieldset(
        'responsables',
        u"Responsables",
        fields=['coordinador','integrantes'],
    )
    form.fieldset(
        'imagenes',
        u"Ilustraciones",
        fields=['imagenCabecera','textoAltCabecera','imagenHome','imagenLista'],
    )

    
    tipoColeccion = schema.Choice(
            title=u"Categoría",
            description=u"Elija una categoría a la que responde esta Colección. Si la categoría no existe debe pedirle al administrador que genere una nueva.",
            source="arcas.Categorias",
        )
    cuerpo = RichText(
        title=_(u"Texto principal"),
        required=False,
    )

    directives.read_permission(coordinador='arcas.defineCurador')
    directives.write_permission(coordinador='arcas.defineCurador')
    coordinador=schema.List(
        title=_("Coordinador"),
        value_type=schema.Choice(source="arcas.CoorMembersVocab",),
        required=False,
    )
    integrantes=schema.List(
        title=_("Integrantes"),
        value_type=schema.Choice(source="arcas.InvestMembersVocab",),
        required=False,
    )
    imagenCabecera=NamedBlobImage(
        title=_(u"Imagen cabezal"),
        description=_(u"Esta imagen se usa como cabezal en la visualización de la coleccion"),
        required=False,
    )
    textoAltCabecera=schema.TextLine(
        title=u"ALT Imagen cebecera",
        description=_(u"Si la imagen de cabecera posee información de copyright, debe escribirse en este campo. Se desplegará la información al pasar el puntero sobre la imagen."),
        required=False,
    )
    imagenHome=NamedBlobImage(
        title=_(u"Imagen para la Portada"),
        description=_(u"Esta imagen se usa en la página principal"),
        required=False,
    )

    imagenLista=NamedBlobImage(
        title=_(u"Imagen listado"),
        description=_("Esta imagen se usa en el listado de colecciones"),
        required=False,
    )

    GS_ID= schema.TextLine(
        title=u"ID de la colección",
        description=_(u"Nombre de la colección en GS3. Se requiere para hacer las busquedas"),
        required=True,
    )
    altNavegarFuente=schema.Text(
        title=_(u"Navegar Fuente"),
        description=_(u"Escriba aquì una descripción para el botón Navegar Fuente, que permita al usuario comprender mejor como está organizada la colección."),
        required=False,
    )

#class View(DisplayForm):
class ColeccionView(BrowserView):

    
    video_template = ViewPageTemplateFile("viewlets/video_snipet.pt")
    texto_template = ViewPageTemplateFile("viewlets/texto_snipet.pt")
    imagen_template = ViewPageTemplateFile("viewlets/imagen_snipet.pt")
    galeria_template = ViewPageTemplateFile("viewlets/galeria_snipet.pt")
    bio_template = ViewPageTemplateFile("viewlets/bio_snipet.pt")
    flagSecActual=0

    def manageColDer(self):
        """Gestiona las secciones de la columan derecha"""
        return self.context.tipoSecc1

    def getCoordinadores(self):
        """Devuelve los curadores de la coleción"""        
        coords=self.context.coordinador
        homer=self.context.portal_url().split("/")[-1]

        if(len(coords)==0):
            return []          
        
        infoCoor=[]
        tt=getToolByName(self.context,"portal_membership")
        
        for idusr in coords:            
            coordina=tt.getMemberById(idusr)
            ur='/%s/Members/%s' %(homer,idusr)
            
            infoCoor.append({'type' : 'user',
                                 'id'   : coordina.id,
                                 'title': coordina.getProperty('fullname', None) or coordina.id,
                                 'email': coordina.getProperty('email'),
                                 'img'  : tt.getPersonalPortrait(id=coordina.id),
                                 'cv':coordina.getProperty('home_page')
                                 })
        
        #colec=ColeccionUtils(self.context)
        #infoCoor=colec.getCoordinadores()        
        return infoCoor

    def getUrlAFuente(self):
        """devuelv la dirección a la fuente primaria"""
        baseURL=URL_GREENSTON_DOC+self.context.GS_ID+"/browse/CL1"
        return baseURL

    def dameCurador(self):
        """devuelve un listado con los curadores de la coleccion"""
        rs=ColeccionUtils(self.context)
        rt=rs.dameCurador()
        return rt

    def dameDicRecomendados(self):
        """
            devuelve un listado de las carpetas y sus contenidos como recomendados
        """
        listFold=[]
        excludList=(self.context.id+"_estudios",self.context.id+"_gale")
        catalog=getToolByName(self.context,"portal_catalog")
        colection_path = '/'.join(aq_inner(self.context).getPhysicalPath())
        idRec=excludList[0]
        if hasattr(self.context,idRec):
            recomFolder=aq_inner(self.context[idRec])
            desta_path = '/'.join(recomFolder.getPhysicalPath())
            recomContent=catalog.searchResults(path={'query':desta_path , 'depth': 1})
            objRaiz={}
            objRaiz["titulo"]="Estudios"
            objRaiz["content"]=self.dameContenido(recomFolder)
            objRaiz["url"]=self.context.absolute_url
            listFold.append(objRaiz)
        else:
            print "la coleccion no tiene carpeta Recomendados"
            return None

        otrosF=catalog.searchResults(path={'query':colection_path , 'depth': 1})
        for elem in otrosF:
            if elem.id not in excludList:
                elemObj=self.context.unrestrictedTraverse(elem.getPath())

                if elem.portal_type=="Folder":
                    obj={}
                    obj["titulo"]   =elem.Title
                    obj["content"]  =self.dameContenido(elemObj)
                    obj["url"]  =elem.getURL()
                    listFold.append(obj)
        return listFold

    def dameContenido(self,folder):
        """Devuelve una lista con los objetos del contenedor"""
        resultado=[]
        catalog=getToolByName(folder,"portal_catalog")
        desta_path = '/'.join(folder.getPhysicalPath())
        cataloDest=catalog.searchResults(path={'query':desta_path , 'depth': 1},sort_on='getObjPositionInParent')

        for elem in cataloDest:
            if elem.portal_type!="Folder":
                elemObj = folder.unrestrictedTraverse(elem.getPath())
                urlE    = elem.getURL()
                if elem.portal_type=="Link":
                    urlE=elemObj.getRemoteUrl()

                if elem.portal_type=="arcas.sugerencia":
                    urlE=elemObj.urlRemoto
                tipoMedio=False
                listAutores=[]
                if hasattr(elemObj,"tipoMedio"):
                    tipoMedio=getattr(elemObj,"tipoMedio")
                    if tipoMedio=='resena':
                        tipoMedio='reseña'
                if hasattr(elemObj,"autores"):
                    listAutores=getattr(elemObj,"autores")
                objRaiz={'titulo':elem.Title,
                         'url':urlE,
                         'descri':elem.Description,
                         'tipo':tipoMedio,
                         'autores':listAutores,
                         }
                resultado.append(objRaiz)
        return resultado


    def getImagenes(self):
        """Devuelve todas las img de la galeria"""
        context = aq_inner(self.context)
        catalogo=getToolByName(context,"portal_catalog")
        tmpX=[]

        if hasattr(context,context.id+"_gale"):
            galeFold=getattr(context,context.id+"_gale")
            galePath="/".join(galeFold.getPhysicalPath())
            result=catalogo(path=galePath,portal_type="Image",sort_on='getObjPositionInParent')
             
            for re in result:
                if re.Title == "Un Puig":
                    import pdb
                    pdb.set_trace()
                foto=context.unrestrictedTraverse(re.getPath())

                altoSugerido=80
                if hasattr(foto,"height"):
                    iniH=foto.height
                else:
                    iniH=foto.image._height

                if hasattr(foto,"height"):
                    fw=foto.width
                else:
                    fw=foto.image._width
                    
                relH=((altoSugerido*100)/iniH)
                widthH=(fw*relH)/100
                tmpX.append({"width":widthH,"brain":re})
        else:
            return None

        return tmpX
        
    def getCv(self,ruta):
        """busca un tipo de document File en la carpeta personal del coordinador"""
        cvr=False
        catalog = getToolByName(self.context, 'portal_catalog')
        capetaU=catalog(path=dict(query=ruta, depth=1))		        
        for elem in capetaU:
            if elem.Title=="cv" or elem.Title=="CV":
                cvr=elem.getPath()

        return cvr
        
        
        
    def getBioList(self):
        """Devuelve un listado de biografías que ese encuentra dentro de de la colección"""
        listBio=[]
        contexto=aq_inner(self.context)
        catalog=getToolByName(contexto,"portal_catalog")
        desta_path = '/'.join(contexto.getPhysicalPath())
        cataloDest=catalog.searchResults(path={'query':desta_path , 'depth': 1})

        for bio in cataloDest:
            if bio.portal_type=="arcas.biografia":
                listObj=contexto.unrestrictedTraverse(bio.getPath())
                listBio.append({
                    "nombre":bio.Title,
                    "descri":bio.Description,
                    "url":bio.getURL(),
                    "listado":listObj.produccion.output,
                })
        return  listBio

    def dameBanners(self):
        """Devuleve los banners a las exhibiciones relacionadas a la coleccion"""
        utilidad= ColeccionUtils(self.context)
        result=[]
        dameE=utilidad.dameExhibicionesR()
        if dameE:
            for exhi in dameE:
                sinBaner=dameE[0].baner==None
                obj={'url':exhi.absolute_url(),'titulo':exhi.title,"vacio":sinBaner }
                result.append(obj)

        return  result
    
    def dameSeccionActual(self):
        return self.flagSecActual
        

    def getSecc1(self):
        """ Render summary box
        @return: Resulting HTML code as Python string
        """
        self.flagSecActual=1
        tsec=self.context.tipoSecc1

        if tsec == "biografia":            
            return self.bio_template()
        elif tsec == "texto":
            return self.texto_template()        
        elif tsec== "imagen":
            return self.imagen_template()
        elif tsec == "galeria":
            return self.galeria_template()
        elif tsec== "video":
            return self.video_template()
        
        
        
    def getSecc2(self):
        """ Render summary box
        @return: Resulting HTML code as Python string
        """
        self.flagSecActual=2
        tsec=self.context.tipoSecc2        
        if tsec == "biografia":            
            return self.bio_template()        
        elif tsec == "texto":
            return self.texto_template()        
        elif tsec== "imagen":
            return self.imagen_template()
        elif tsec == "galeria":
            return self.galeria_template()
        elif tsec== "video":
            return self.video_template()
        
        
class EditForm(edit.DefaultEditForm):    
    
    def update(self):
        super(EditForm, self).update()        
        
