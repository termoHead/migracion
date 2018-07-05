# -*- coding: utf-8 -*-
__author__ = 'Paul'
from arcas.content import _
from plone.app.textfield import RichText
from five import grok
from zope import schema
from plone.directives import form
from plone.supermodel import model
from plone.formwidget.contenttree import ContentTreeFieldWidget
from arcas.content.exhibicion import IExhibicion
from Products.CMFCore.utils import getToolByName
from z3c.relationfield.schema import RelationList, RelationChoice
from arcas.content.coleccionesFolder import IColeccionesFolder
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.app.layout.navigation.interfaces import INavigationRoot
     
from plone.dexterity.content import Container
from arcas.content.utils import ColeccionUtils,ColeccionesPorCategoria,ExhibicionUtils
from arcas.content.config import URL_GREENSTON_DOC
from arcas.content.utils import TextoUtils
import DateTime
from Acquisition import aq_inner
from plone.directives.dexterity import DisplayForm
from plone.dexterity.utils import createContentInContainer
from arcas.content.exhibicionesFolder import IExhibicionesFolder
from arcas.content.coleccion import IColeccion
from plone.autoform import directives
from plone.formwidget.autocomplete import AutocompleteFieldWidget
from plone.formwidget.contenttree import MultiContentTreeFieldWidget
from plone.formwidget.contenttree import PathSourceBinder
from plone.formwidget.contenttree import ObjPathSourceBinder
from z3c.relationfield.relation import RelationValue
from zope.intid.interfaces import IIntIds
from zope.component import getUtility

class IRootFolder(model.Schema):
    """Una carpeta principal para documentos publicos
    """
    cuerpo = RichText(
        title=_(u"Texto principal"),
        required=True,
    )
    directives.widget(exhiDestacada=AutocompleteFieldWidget)
    exhiDestacada = RelationChoice(
        title=u"Selecciones una Exhibicion",
        description=u"Seleccione la exhibicion a destacar",
        source=ObjPathSourceBinder(object_provides=IExhibicion.__identifier__),
        required=False,
    )

from Products.Five import BrowserView
from plone.dexterity.browser.view import DefaultView
class RootView(DefaultView):
    
    def getExhiDestacado(self):
        ##recreaFolder= self.getContainer(folder.encode('utf8'))
        ##cuando busca documento hace referencia al campo "documento" que es el destacado del directorio

        if isinstance(self.context.exhiDestacada,RelationValue):
            intids = getUtility(IIntIds)
            idTo=self.context.exhiDestacada.to_id
            destacado=intids.getObject(idTo)
            colecTRId=destacado.coleccionR.to_id
            colecTRelated = intids.getObject(colecTRId)
            exhibUtils = ExhibicionUtils(destacado)  
            

            
            #mcura=exhibUtils.dameCuradores()
            #minte=exhibUtils.dameCoordinadores()
            mcura=[]
            minte=[]

            descrD=destacado.description
            
            if len(descrD)>250:
                descrD=descrD[0:descrD[:250].rfind(" ")]+" ..."
            
            resp={
                'titulo'   : destacado.title,
                'tituloColec': colecTRelated.title,
                'descri' : descrD,
                'exhiurl': destacado.absolute_url(),
                'curador': mcura,
                'integrantes': minte
            }

            if len(resp)>0:
                return resp
        else:
            if self.context.exhiDestacada!=None:
                if len(self.context.exhiDestacada)==0:
                    print "no hay exhibiciones asiganadas al portlet"
                    return None

                destacado     = self.context.exhiDestacada[0].to_object
                colecTRelated = destacado.coleccionR[0].to_object                                
                exhibUtils    = ExhibicionUtils(destacado)  

                mcura=exhibUtils.dameCuradores()
                minte=exhibUtils.dameCoordinadores()

                descrD=destacado.description

                if len(descrD)>250:
                    descrD=descrD[0:descrD[:250].rfind(" ")]+" ..."

                resp={
                    'titulo'   : destacado.title,
                    'tituloColec': colecTRelated.title,
                    'descri' : descrD,
                    'exhiurl': destacado.absolute_url(),
                    'curador': mcura,
                    'integrantes': minte
                }

                if len(resp)>0:
                    return resp

        print "no hay exhibiciones asiganadas al portlet"
        return None

    def listExhiUrl(self):
        """Devuelve la url al listado de exhibiciones"""
        
        catalog=getToolByName(self.context,"portal_catalog")
        exlis=catalog(object_provides=IExhibicionesFolder.__identifier__)
        if len(exlis)>0:
            return exlis[0].getURL()
        else:
            return None


    def getCategoriasColec(self):
        ##recupera las categorias y las colecciones de cada una
        resuList=[]
        listado=ColeccionesPorCategoria(self.context)

        
        txu=TextoUtils()
        for elem in listado(self.context):            
            miCat={"titulo":elem["categoria"],"color":elem["color"],"colecciones":[],"ilustra":elem["ilustra"],"url":elem["url"]}
            for elC in elem["colecciones"]:
                extraFUrl="%s/%s#estudios" %(elC["url"],elC["id"])
                extraFT="Estudios"
                extraFUrlF="%s%s/browse/CL1" %(URL_GREENSTON_DOC,elC["urlGS"])
                elC["extraFolderUrl"]       =extraFUrl
                elC["extraFolderTitulo"]    =extraFT
                elC["extraFolderFuenteUrl"] =extraFUrlF                
                desc=elC["descri"]

                elC["descri"]=txu.cortaTexto(desc,87)
                miCat["colecciones"].append(elC)
            resuList.append(miCat)

        
        if len(resuList)==0:
            print "no hay categorias encontradas"
            return None
        
        return resuList
        
    
    def getColecciones(self):
        ##recreaFolder= self.getContainer(folder.encode('utf8'))
        ##cuando busca documento hace referencia al campo "documento" que es el destacado del directorio

        
        catalog=getToolByName(self.context,"portal_catalog")
        
        colList=catalog.searchResults(object_provides=IColeccion.__identifier__)
        #colList=catalog.searchResults(portal_type='arcas.coleccion',review_state='Publicado')
        resuList=[]
        extraFUrl=""
        extraFT=""
        try:
            for elem in colList:
                destacado=self.context.unrestrictedTraverse(elem.getPath())
                desta_path = '/'.join(destacado.getPhysicalPath())
                cataloDest=catalog.searchResults(path={'query':desta_path , 'depth': 1})

                """
                for carpeta in cataloDest:
                    if carpeta.portal_type=="Folder" and carpeta.Title!="Galería":
                        extraFUrl=carpeta.getURL()
                        extraFT=carpeta.Title
                        break
                """
                extraFUrl="%s/%s_estudios" %(elem.getURL(),elem.id)
                extraFT="Estudios"
                descrD=elem.Description
                if len(descrD)>350:
                    descrD=descrD[0:descrD[:350].rfind(" ")]+" ..."



                resuList.append({
                    "titulo":elem.Title,
                    "id":elem.id,
                    "url":elem.getURL(),
                    "description":descrD,
                    "extraFolderUrl":extraFUrl,
                    "extraFolderTitulo":extraFT
                } )
            if len(resulist)>0:
                return resuList

            
        except :
            print "no hay colecciones asiganadas al portlet"
            pass
        
        return False
    
    
    def listColeccUrl(self):
        """Devuelve la url al listado de colecciones"""
        catalog= getToolByName(self.context,"portal_catalog")
        exlis  = catalog(object_provides=IColeccionesFolder.__identifier__)
        if len(exlis)>0:
            return exlis[0].getURL()
        else:
            return False

    def dameNoticias(self):
        """devuelve las noticias"""


        catalog= getToolByName(self.context,"portal_catalog")

        cexto=aq_inner(self.context)

        if hasattr(cexto,"novedades"):
            folder_path = '/'.join(cexto.novedades.getPhysicalPath())
            results = catalog.searchResults(path=folder_path,sort_on='effective',sort_order='reverse')
            return results
        else:
            return []

    def dameNotiUrl(self):
        """URL a la carpeta de noticias"""
        cexto=aq_inner(self.context)

        if not hasattr(cexto,"novedades"):
            try:
                createContentInContainer(cexto,"Folder",title="Novedades",description="Toda la información referente a ARCAS")
                
            except:
                return None
     
        return cexto.novedades.absolute_url()

    def dameProyectoUrl(self):
        """URL al documento del proyecto"""
        strT="acerca_de_arcas"
        cexto=aq_inner(self.context)
        if not hasattr(cexto,strT):
            return ""
            cexto.invokeFactory("Folder",strT)
            print "Se creo la carpeta Acerca de "
            cexto.acerca_de_arcas.title="Acerca de Arcas"
            cexto.acerca_de_arcas.description="Información sobre el proyecto"
            cexto.acerca_de_arcas.invokeFactory("Document","el_proyecto_arcas")
            cexto.acerca_de_arcas.el_proyecto_arcas.title="El proyecto ARCAS"


        return cexto.acerca_de_arcas.el_proyecto_arcas.absolute_url()

    def dameTextoDescri(self):
        """Texto de destacado"""
        caracteresCorte=950
        idObject="el_proyecto_arcas"
        catalog=getToolByName(self.context,"portal_catalog")
        brain=catalog(id=idObject)
        if len(brain)==0:
            return "<p>Descripción del proyecto ARCAS</p>"
        
        texto=brain[0].getObject().text.output
        
        if texto>caracteresCorte:
            corteTexto=texto[:texto[:caracteresCorte].rfind(" ")]+" ..."
            apertura= corteTexto.rfind("<p>")
            cierre  = corteTexto.rfind("</p>")
            if cierre<apertura:
                corteTexto=corteTexto+"</p>"

        return "<p>%s</p>%s" %(brain[0].Description,corteTexto)