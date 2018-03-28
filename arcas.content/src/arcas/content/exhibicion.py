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
from arcas.content.behaviors import IColecGroupName
from arcas.content.eventos import PREFIJO_COOR_GROUP


from z3c.relationfield.schema import RelationList, RelationChoice
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.formwidget.autocomplete import AutocompleteFieldWidget
from plone.formwidget.contenttree import ContentTreeFieldWidget
from plone.formwidget.contenttree import ObjPathSourceBinder

from AccessControl import getSecurityManager
from AccessControl import Unauthorized
from Products.CMFCore import permissions

from Acquisition import aq_inner
from plone.directives.dexterity import DisplayForm,EditForm

try:
    from arcas.content.coleccion import IColeccion
except:
    IColeccion=form.Schema

class IExhibicion(form.Schema):
    """A conference program. Programs can contain Sessions.
    """
    form.fieldset(
        'responsables',
        u"Responsables",
        fields=['curador','integrantes'],
    )
    cuerpo = RichText(
        title=_(u"Texto principal"),
        required=False,
    )
    bgCabezalHome=NamedBlobImage(
        title=_(u"Imagen Home"),
        description=u"Imagen de fondo que se utiliza en la home. Para componerla utilice los ejemplos del banco de imagenes",
        required=False,
    )
    bgCabezalVista=NamedBlobImage(
        title=_(u"Imagen de la vista"),
        description=u"Imagen de fondo que se utiliza en la pagina de la exhibición propiamente dicha. Si desea componer una nueva, utilice los ejemplos del banco de imagenes",
        required=False,
    )
    bgCabezalLista=NamedBlobImage(
        title=_(u"Imagen para el listado exhibiciones"),
        description=u"Imagen de fondo que se utiliza en el listado de exhibiciones. Si desea componer una nueva, utilice los ejemplos del banco de imagenes",
        required=False,
    )
    baner=NamedBlobImage(
        title=_(u"Imagen para baner"),
        description=u"Imagen completa del baner que se muestra en la vista de coleccion. Si desea componer uno nuevo, puede utilizar los ejemplos del banco de imágenes",
        required=False,
    )



    curador=schema.List(
        title=_(u"Curadores"),
        value_type=schema.Choice(source="arcas.ExhibicionMembersVocab",),
        required=False
    )
    
    integrantes=schema.List(
        title=_(u"Integrantes"),
        description=u"Listado de personas que colaboran con esta exhibición",
        value_type=schema.Choice(source="arcas.ExhibicionMembersVocab"),
        required=False
    )


    coleccionR = RelationList(
        title=u"Colección Relacionada",
        description=u"Colección a la que pertenece esta exhibicón",
        value_type=RelationChoice(
            source=ObjPathSourceBinder(portal_type='arcas.coleccion')
        ),
        required=False,
    )

class View(DisplayForm):
    
    def listadoDeImagenesGS3(self):
        """Trae todos los recursoGS3 en la carpeta enlacesgs"""
        catalog=getToolByName(self.context,"portal_catalog")
        ruta='/'.join(self.context.getPhysicalPath())
        result=catalog(portal_type='arcas.enlacegs', path={'query': ruta, 'depth': 1})

        return result

    def muestraImagenGS(self):
        """Tra una imagen de GS3"""
        pass
        
    def dameIdExhi(self):
        return self.context.id
    
    def dameObjectoColeccion(self):
        

        try:
            miColec=self.context.coleccionR[0].to_object
            if IColeccion.providedBy(miColec):
                return miColec
            else:
                return None
        except:
            print "no hay coleccion asignada"
        return None

    def dameCoordinador(self):
        """Devuelve los usuarios del grupo coor"""
        groups_tool = getToolByName(self.context, 'portal_groups')
        fUser=[]
        colecR=self.dameObjectoColeccion()        
        if colecR:
            ppa=IColecGroupName(colecR)
            group_id = ppa.groupName.replace("_g",PREFIJO_COOR_GROUP)
            grupo=groups_tool.getGroupById(group_id)

            for usuario in grupo.getGroupMembers():
            
                if usuario.getProperty('fullname')!="":
                    fUser.append(usuario.getProperty('fullname'))
                else:
                    fUser.append(usuario.getProperty('id'))
                    
            return fUser
        else:
            return None


    def dameCurador(self):
        """devuelve el curador de la coleccion"""
        usrTool = getToolByName(self.context, 'portal_membership')
        
        curadores=[]
        for userR in self.context.curador:
            userO=usrTool.getMemberById(userR)
            users={'nombre':userO.getProperty("fullname"),
               'email':userO.getProperty("email"),
               'img':usrTool.getPersonalPortrait(userO.id),
               'bio':userO.getProperty("bio"),
               'id':userO.id,
               'cv':'pdf profile'}
            curadores.append(users)
            
        return curadores
        
    def dameColaboradores(self):
        """Devulevle una lista de colaboradores de la exhibicion"""
        usrTool = getToolByName(self.context, 'portal_membership')
        colabs = self.context.integrantes
        result=[]

        for userO in colabs:
            userO=usrTool.getMemberById(userO)
            users={'nombre':userO.getProperty("fullname"),
               'email':userO.getProperty("email"),
               'img':usrTool.getPersonalPortrait(userO.id),
               'id':userO.id,
               'bio':userO.getProperty("bio"),
               'cv':'pdf profile'}
            result.append(users)
        return result
        
        
    def dameNombreColeccion(self):
        """devuelve el nombre del parent de esta coleccion"""
        result=""
        miColec=self.dameObjectoColeccion()
        if miColec:
            result=miColec.title
            return result
        return None

    def dameUriColeccion(self):
        miColec=self.dameObjectoColeccion()
        if miColec:
            return miColec.absolute_url()
        else:
            return self.context.absolute_url()

    def dameEnlaces(self):
        """devuelve el contenidos de los objetos que se encuentran dentro de la carpeta
        enlaces"""
        respuesta=[]
        try:
            catalog=getToolByName(self.context,"portal_catalog")
            idF=self.context.id+'_enlace'
            ruta='/'.join(self.context[idF].getPhysicalPath())
            result=catalog(review_state=('published','private'),path={'query': ruta, 'depth': 1},sort_on='getObjPositionInParent')            
            
            return result
        except:
            return None
            
    def puedeEditar(self):
        if not getSecurityManager().checkPermission(permissions.ModifyPortalContent, self.context):
            return False
        else:
            return True
    
    def dameSaftyDescri(self):
        """devuelve la descripcion de la exhibicion recortada"""
        str=self.context.cuerpo.output[:900]
        cierre=str.rfind("</p>")
        apertura=str.rfind("<p>")
        if cierre<apertura:
            str=str+" ...</p>"
        return str
        
    def dameDatosImgFull(self):
        """
            devuelve un diccionario con los datos de la primera hoja
            de la exhibiciòn:
            urlImg: full imagen
            ficha: url a la ficha en GS3
        """

        listImages=self.listadoDeImagenesGS3()
        if len(listImages)<1:
            return None
        recu=listImages[0]

        obj=self.context.unrestrictedTraverse(recu.getPath())
        if obj.tipoMedio=="imagen":
            urlT=obj.urlRemoto
            
            if obj.ficha and obj.ficha!=u'':
                ficha=obj.ficha
            else:
                ficha = None
            
            urlN=urlT.replace("_screen","")
            urlN=urlN.replace("jpeg","jpg")
            
            return {"urlImg":urlN,"ficha":ficha}
        else:
            urlT=obj.urlRemoto
            if obj.ficha and obj.ficha!=u'':
                ficha=obj.ficha
            else:
                ficha = None
            return {"urlImg":urlT,"ficha":ficha}
        

