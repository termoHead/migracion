# -*- coding: utf-8 -*-
import json
import pdb
import os
# Note that by default Add portal member permissions
# is only for the owner, so we need to by bass it here
from Products.CMFPlone.utils import _createObjectByType
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import queryUtility
from zope.dottedname.resolve import resolve
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Acquisition import aq_inner, aq_parent
#PLONE_CSRF_DISABLED=True
from plone import api
from plone.dexterity.utils import createContentInContainer
from plone.protect.auto import safeWrite
from plone.app.textfield.value import RichTextValue
from plone.namedfile.file import NamedBlobImage,NamedImage
import base64
from base64 import b64decode
import csv
from plone.namedfile.file import NamedBlobFile as FileValueType
from plone.namedfile.utils import get_contenttype
import transaction
from z3c.relationfield import RelationValue
from zope.intid.interfaces import IIntIds
from zope.component import getUtility

class RelationManager(object):
    
    _relbase=[]
    
    def __init__(self,contexto):
        self.contexto=contexto

    def setRealcion(self,idObjFuente,idObjDestino,nombreCampo):
        self._relbase.append((idObjFuente,idObjDestino,nombreCampo))

    def generate(self):
        
        cata= getToolByName(self.contexto, 'portal_catalog')
        
        for objR in self._relbase:
            fuente=cata(id=objR[0])
            destino=cata(id=objR[1])
            nomC=objR[2]
            
            if len(fuente)>0 and len(destino)>0:   
                fObject=fuente[0].getObject()
                dObject=destino[0].getObject()
                fUID=self.get_intid(fObject)
                dUID=self.get_intid(dObject)
                
                setattr(fObject,nomC,RelationValue(dUID))

            else:
                print "relacion rota"


    def get_intid(self,obj):
        """Return the intid of an object from the intid-catalog"""
        intids = queryUtility(IIntIds)
        if intids is None:
            return
        # check that the object has an intid, otherwise there's nothing to be done
        try:
            return intids.getId(obj)
        except KeyError:
            # The object has not been added to the ZODB yet
            return

    
class ImportJsonView(BrowserView):
    """Import/Export page."""

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.exportHeaders = None
        self.importHeaders = None
        self.existingPath = []
        self.files = {}
    
    
    
class JSONImport(BrowserView):
    flag=0



    def __call__(self):
        self.update()
        pretty  = json.dumps(self.logs)
        self.request.response.setHeader("Content-type", "application/json")
        self.request.response.setHeader('Access-Control-Allow-Origin', '*')
        return pretty

    def update(self):        
        self.contexto= aq_inner(self.context)
        self.RLM=RelationManager(self.context)
        
        self.logs=["inicio"]
        self.inicio()

    def inicio(self):
        self.logs.append("Iniciando")
        #self.importMember()
        archivos=("acerca_de_arcas.json","novedades.json","colecciones.json","exhibiciones.json")
        for ffile in archivos:
            self.logs.append("Leyendo archivo: %s" %ffile)
            parseado = self.dameObjetoDesdeArchivo(ffile)    
            
            #objP={'id':parseado['id'],'portal_type':parseado['portal_type'],'title':parseado['title'],'contenidos':parseado,'locallyAllowedTypes':True}
            self.cargandoDatosEnPlone(parseado,self.contexto)
            
            
        self.RLM.generate()
        
    def dameObjetoDesdeArchivo(self,filename):
        with open(filename) as json_data:
            cab   = json.load(json_data)
            jsonf = json.loads(cab)
        return jsonf    

    def cargandoDatosEnPlone(self,jsonObj,carpeta):
        bascicData=("id","portal_type","contenidos","locallyAllowedTypes","excludeFromNav","language","rights","modification_date","creation_date","effectiveDate","expirationDate","location","allowDiscussion","tableContents","creators","presentation","subject","content")
        esContenedor=False;
        self.logs.append("Inicio carga datos")
        
        idC=jsonObj['id'][1]
        portalType=jsonObj['portal_type'][1]
        titleC=jsonObj['title'][1]
        
        if "contenidos" in jsonObj.keys():
            self.logs.append("%s es una carpeta" %idC)
            esContenedor=True;
            

        if carpeta.get(idC):
            try:
                self.logs.append("El objeto %s existe en plone y se borrar" %idC) 
                carpeta.manage_delObjects([idC])
            except:
                self.logs.append( "problema borrando el objeto %s" %idC)

        self.logs.append("Creando %s" %idC)
        new_id = carpeta.invokeFactory(portalType, idC, title=titleC)
        #contenedor  = createContentInContainer(,, jsonObj['title'])
        
        contenedor=carpeta.get(new_id)
        
        fti = queryUtility(IDexterityFTI, name=contenedor.portal_type)        
        behaviors = list(fti.behaviors)
        behaviors.append(fti.schema)
        esquema={}
        
        for iface in behaviors:
            try:
                intrObject=resolve(iface)
                for nom,desc in intrObject.namesAndDescriptions():
                    esquema[nom]=desc
            except:
                print "error cargando esquema"
        
        #if portalType=="arcas.enlacegs":
            #pdb.set_trace()
            
        for atri in jsonObj.keys():

            if atri not in bascicData:
                tipoCampo=jsonObj[atri][0]
                valorCampo=jsonObj[atri][1]
                #try:
                    #if atri=="text" or atri=="cuerpo":
                if tipoCampo=="RichText":
                    #textoTMP=RichTextValue(valorCampo, 'text/html', 'text/html',encoding='utf-8')    
                    
                    textoTMP=RichTextValue(raw=valorCampo,mimeType='text/html',outputMimeType='text/x-html-safe')
                    setattr(contenedor,atri,textoTMP)
                    
                elif tipoCampo=="NamedBlobImage" or tipoCampo=="NamedBlobFile":
                    filename        = jsonObj[atri][2]
                    fileruta        = valorCampo
                    filecontenttype =str(jsonObj[atri][3])
                    
                    if filename!='' and tipoCampo=="NamedBlobImage":
                        fieldX=self.prep_image(filename,fileruta,filecontenttype)
                        #hay que convertir la imagen que cargo en fileruta a un NamedImage
                        """
                        if atri=='image':
                            contenedor.image=fieldX
                        else:
                            setattr(contenedor,atri,fieldX)
                        """
                    else:
                        fieldX=self.prep_file(filename,fileruta,filecontenttype)
                        
                        #hay que convertir la imagen que cargo en fileruta a un NamedImage
                        
                    setattr(contenedor,atri,fieldX)
                elif tipoCampo == "RelationList":
                        
                        if valorCampo!='':
                            self.RLM.setRealcion(contenedor.id,valorCampo,atri)
                            pdb.set_trace()
                        #newO[nom]=(campClass,getattr(intrObject(obj),nom)[0].to_object.id,'')
                else:
                    setattr(contenedor,atri,valorCampo)
                #except:
                #    print "no pude setear atributo %s a %s" %(contenedor.id,atri)

        if esContenedor:
            if len(jsonObj["contenidos"])>0:
                for subF in jsonObj["contenidos"]:
                    self.cargandoDatosEnPlone(subF,contenedor)


    def prep_image(self,imagename, ruta, content_type ):
        """ load image from FS and return data string """
        
        with open(ruta, 'rb') as f:
            blobx = f.read()
        
        nBI=NamedBlobImage(data=blobx,filename=imagename,contentType=content_type)
        
        transaction.commit()
        return nBI

    
    def prep_file(self,imagename, ruta, content_type ):
        """ load image from FS and return data string """
        with open(ruta, 'rb') as f:
            blobx = base64.b64encode(f.read())
        
        bF=FileValueType(data=b64decode(blobx),filename=imagename,contentType=content_type)
        
        return bF

    def importMember(self):
        mprop=("username","password","visible_ids","participaEn","last_login_time","language","enlaceCV","home_page","description","wysiwyg_editor","colecCoordina","location","error_log_update","colecAsignadas","listed","portal_skin","tipoUsuario","fullname","email","text_editor","login_time")
        mt = getToolByName(self.contexto, 'portal_membership')
        regtool = getToolByName(self.contexto, 'portal_registration')
        
        #for member in membership.listMembers():

        with open('members.csv', 'rb') as f:
            
            f.seek(0)
            reader = csv.reader(f)
            
            for row in reader:
                proper={}
                fl=0
                for mpr in mprop:
                    if mpr not in ("error_log_update","portal_skin","login_time","text_editor",):
                        proper[mpr]=row[fl]
                    fl+=1
                    
                
                #member = regtool.addMember(username, password, properties=properties)
                
                member = regtool.addMember(proper['username'], proper['password'], properties=proper)
                pdb.set_trace()
       

