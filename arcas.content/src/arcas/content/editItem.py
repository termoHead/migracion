# -*- coding: utf-8 -*-
__author__ = 'Paul'
import os
from arcas.content.coleccion import IColeccion
from plone.autoform import directives
from arcas.content.rootFolder import IRootFolder
from Products.CMFPlone.utils import safe_unicode

#from five import grok
#from plone.directives import form

from zope import schema
from z3c.form import button
from z3c.form.interfaces import HIDDEN_MODE, DISPLAY_MODE, INPUT_MODE
from Products.CMFCore.interfaces import ISiteRoot
from Products.statusmessages.interfaces import IStatusMessage
from plone.app.textfield import RichText
from plone.app.textfield.value import RichTextValue
from plone.supermodel import model

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from Products.CMFCore.utils import getToolByName

from arcas.content.editGS import IGsMetaItem,IGsSubSerie,IGsMetaSerie,iso_idiomas,serie_vocab,coleccionesVocab,item_vocab,subserie_vocab

from arcas.content.FSManager import FSManager
from plone.namedfile.field import NamedFile
from z3c.form import field, group
from arcas.content.config import infoMetaItem,infoMetadatoSubSerie,infoMetadatosSerie
from arcas.content.cartero import Cartero

   
class IEditItem(form.Schema, IGsMetaSerie , IGsSubSerie,IGsMetaItem ):
    """Campos del formulario de edición de un documento Greenston3 en el 
import!   """ 
    model.fieldset('Selección de ítem Serie ',
        label=(u"Elija una serie para editar"),
        fields=["coleccion","serie","subserie","obra","obraTmp","tituColec"]
        
    )    

    form.widget('coleccion', klass='recargaForm')
    directives.mode(coleccion='hidden')
    coleccion= schema.TextLine(
        title=u"Colección",        
        required=True,
    )

    directives.mode(serie='hidden')
    serie = schema.TextLine(
        title=u"Serie",
        required=False,
    )
    directives.mode(subserie='hidden')
    subserie= schema.TextLine(
        title=u"Sub Serie",
        description=u"Elija una sub serie para editar",
        required=False,
    )
    directives.mode(obra='hidden')
    obra = schema.TextLine(
        title=u"Obra",
        required=False,
    )

    directives.mode(obraTmp='hidden')
    obraTmp= schema.TextLine(
        title=u"obraTmp",
        description=u"una pavada",
        required=False,
    )

    directives.mode(tituColec='hidden')
    tituColec= schema.TextLine(
        title=u"Título",
        description=u"título de la colección que está siendo editada",
        required=False,
    )

class EditItem(form.SchemaForm):
    """
       Edita un documento de Greenstone3 desde el import!Pablo Musa
    """
    xmlFileBase  ='/usr/local/Greenstone3/web/sites/localsite/collect/'
    xmlFileResto ='/import/co.1/se.1/su.1/ar.1/it.1/'
    xmlFileName='metadata.xml'
    
    grok.name('editItem')
    grok.require('zope2.View')
    #grok.require('cmf.ListFolderContents')
    #grok.require('arcas.addExhibicion')
    grok.context(IRootFolder)
    schema = IEditItem
    
    ignoreContext = True    
    label       = u"Formulario para edición de datos descriptivos de las fuentes primarias"
    description = u'<div class="formuDescri">Los datos que usted va a editar se actualizarán una vez hayan sido revisados y aceptados\
                    para su inclusión/modificación por el equipo técnico de ARCAS. Recibirá un mail con la modificación \
                    por Usted realizada y cuando haya sido actualizado en el Portal público.<br \/>\
                    En todos los casos, el formulario mostrará para editar la versión pública. Si necesita modificar \
                    una versión generada por usted aún no publicada, utilice la información recibida por mail para \
                    recuperar los datos de las versiones intermedias.</div>\
                    '
    fsmanager   = ""
    coleccion   = "cordemia"
    serie       = ""
    obra        = ""
    saveFlag    = 0
    msjForm     = ""
    
    
    #lsw=["f_fechaCreacion","f_lugarCreacion","f_descFisica","f_dimensiones","f_idioma","f_naturaleza","f_alcance","f_anotacion","f_ruta"]
    editOk=False

    def update(self):
        global COLECCION
        global SERIE
        global SUBSERIE
        
        super(EditItem, self).update()
        
        if 'HTTP_REFERER' in self.request.keys():
            self.vengoDe=self.request.HTTP_REFERER

        dictForm= self.request.form
        if 'cancel' in dictForm.keys():
            self.status="Los cambios fueron cancelados"
            return
        if 'formOk' in dictForm.keys():
            self.status=dictForm['formOk']
            return
            
        if 'obra' in dictForm.keys():
            tituloC=self.dameTituloDeColeccionPorID_GS(dictForm["coleccion"])
            self.label=u'Editando la obra %s, de la colección: %s' %(dictForm["obra"],tituloC)

        COLECCION=SERIE=SUBSERIE=""        

        if "biruta" in dictForm:
            biruta=dictForm["biruta"]
            print biruta
            self.groups[0].widgets["f_ruta"].value=biruta
        else:
            #biruta=dictForm["form.widgets.f_ruta"]
            biruta=None

        if not biruta:
            return
        if "colec" in dictForm:
            colecId=dictForm["colec"]
        else:
            colecId=None

        if "coleccion" in dictForm:
            COLECCION=dictForm["coleccion"]
            self.groups[3].widgets["coleccion"].value=COLECCION
            self.groups[3].widgets["coleccion"].update()
            self.groups[3].widgets["obra"].value=dictForm["obra"]
            self.groups[3].widgets["obra"].update()
        else:
            COLECCION=None

        if "serie" in dictForm:
            SERIE=dictForm["serie"]
            self.groups[3].widgets["serie"].value=SERIE
            self.groups[3].widgets["serie"].update()
            #self.groups[3].widgets["serie"].value=SERIE
        else:
            SERIE=None

        if "subserie" in dictForm:
            SUBSERIE=dictForm["subserie"]
            self.groups[3].widgets["subserie"].value=SUBSERIE
            self.groups[3].widgets["subserie"].update() 
            #self.groups[3].widgets["subserie"].value=SUBSERIE
        else:
            SUBSERIE=None

        rutaItem = biruta

        #averigua si tiene subserie 
        if len(biruta.split("/")[3:])>=4:
            subSerieOk=True
        else:
            subSerieOk=False

        
        if subSerieOk:
            arTmp = rutaItem.split("/")
            del arTmp[-2]
            del arTmp[-2]
            rutaSerie = "/".join(arTmp)
            arTmp = rutaItem.split("/")
            del arTmp[-2]
            rutaSubSerie = "/".join(arTmp)
        else:
            arTmp = rutaItem.split("/")
            del arTmp[-2]
            rutaSerie = "/".join(arTmp)

        fsmanager=FSManager()
        itemLoaded=fsmanager.parseXmlFileMetadata(COLECCION,biruta)
        itemSerieLoaded=fsmanager.parseXmlFileMetadata(COLECCION,rutaSerie)

        if subSerieOk:
            itemSubSerieLoaded=fsmanager.parseXmlFileMetadata(COLECCION,rutaSubSerie)
        
        
        if isinstance(itemLoaded,str) or isinstance(itemSerieLoaded,str) or isinstance(itemSubSerieLoaded,str):
            miurltmp=self.context.REQUEST.URL
            miurl   ="/".join(miurltmp.split("/")[:-2])
            self.context.REQUEST.RESPONSE.redirect(miurl+"/formsCancel_view?mensaje=Error al leer el xml orginal&titulo=Error en la edic&oacute;n")
            return 
            
            
            
        for tupla in itemLoaded.items():            
            try:
                widgetNumber=infoMetaItem.values().index(tupla[0])
                nombreW=  infoMetaItem.keys()[widgetNumber]
                valor=tupla[1]
                
                if isinstance(tupla[1],list):                    
                    valor = ""
                    for bloqtext in tupla[1]:
                        valor += bloqtext+"\itemSubSerieLoadedr"
                self.groups[0].widgets[nombreW].value=valor
                self.groups[0].widgets[nombreW].update()
            except:
                pass
                #print u"el elemento no está"

        for tupla in itemSerieLoaded.items():
            try:
                widgetNumber=infoMetadatosSerie.values().index(tupla[0])
                nombreW=infoMetadatosSerie.keys()[widgetNumber]
                self.groups[2].widgets[nombreW].value=tupla[1]
                self.groups[2].widgets[nombreW].update()
            except:
                pass
                #print u"el elemento no está"

        if subSerieOk:

            for tupla in itemSubSerieLoaded.items():
                try:
                    widgetNumber=infoMetadatoSubSerie.values().index(tupla[0])
                    nambreW=infoMetadatoSubSerie.keys()[widgetNumber]
                    self.groups[1].widgets[nambreW].value=tupla[1]
                    self.groups[1].widgets[nambreW].update()
                except:
                    pass
                    #print u"el elemento no está"

        self.groups[3].mode='hidden'

        
        for tupla in itemLoaded.items():            
            try:
                widgetNumber=infoMetaItem.values().index(tupla[0])
                nombreW=  infoMetaItem.keys()[widgetNumber]
                valor=tupla[1]
                
                if isinstance(tupla[1],list):                    
                    valor = ""
                    for bloqtext in tupla[1]:
                        valor += bloqtext+"\r"
                self.groups[0].widgets[nombreW].value=valor
                self.groups[0].widgets[nombreW].update()
            except:
                pass
                #print u"el elemento no está"
        
        
                #super(EditItem, self).update()
                #self.groups[3].widgets["tituColec"].value=self.dameTituloColeccionByGSID(COLECCION)
                #if len(self.groups[3].widgets["tituColec"].value) >0:
                #    self.label="Formulario para edición de datos descriptivos de las fuentes primarias de la colección %s"%self.groups[3].widgets["tituColec"].value

                #if colec:
                #    self.groups[3].widgets["coleccion"].value = colec.encode('utf-8')
                #    COLECCION=self.groups[3].widgets["coleccion"].value
                #    self.groups[3].widgets["coleccion"].mode = HIDDEN_MODE

    def dameTituloDeColeccionPorID_GS(self,idGs):
        """dado el id de una colección Greenstone devuelve el título del Objeto Coleccion de Plone"""
        
        catalogo=getToolByName(self.context,"portal_catalog")
        
        colecs=catalogo(object_provides=IColeccion.__identifier__)
        for brain in colecs:
            if brain.getObject().GS_ID == idGs:
                return brain.Title
        return ""

    def apagrupo(self,grupo):
        for wid in grupo.widgets:
            grupo.widgets[wid].mode=HIDDEN_MODE

    def showSave(self):
        vva=True
        if 'cancel' in self.request.keys():
            vva=False
        return vva

    @button.buttonAndHandler(u'Guardar',condition=showSave)
    def saveHandler(self, action):
        self.saveFlag=self.saveFlag+1
        flagResult=""
        if self.saveFlag<2:
            mt=getToolByName(self.context,"portal_membership")
            operarioMail    = mt.getAuthenticatedMember().getProperty('email',None)
            operarioNombre  = mt.getAuthenticatedMember().getProperty('fullname',None)
            operarioDict={'nombre':operarioNombre,'mail':operarioMail}
            msj=rutaItem = rutaSubSerie = rutaSerie = ""
            subSerieOk=False

            infoMetadatos=infoMetaItem
            #infoMetadatosSerie=infoMetadatosSerie

            data, errors = self.extractData()

            if len(self.groups[3].widgets["subserie"].value)>0:
                subSerieOk=True
                
                #infoMetadatoSubSerie=infoMetadatoSubSerie

            if errors:
                self.status = self.formErrorsMessage
                return

            #rutaArchivos
            rutaItem = self.groups[0].widgets["f_ruta"].value

            if subSerieOk:
                arTmp = rutaItem.split("/")
                del arTmp[-2]
                del arTmp[-2]
                rutaSerie = "/".join(arTmp)

                arTmp = rutaItem.split("/")
                del arTmp[-2]
                rutaSubSerie = "/".join(arTmp)
            else:
                arTmp = rutaItem.split("/")
                del arTmp[-2]
                rutaSerie = "/".join(arTmp)
                
            
            #cargo ITEM
            tmpList={}
            for mxx in infoMetadatos:            
                if "form.widgets.%s"%mxx in self.request.form.keys():
                    itFtext=self.request.form["form.widgets."+mxx]
                    
                    #tmpList.append((infoMetaItem[x],itFtext))
                    tmpList[infoMetaItem[mxx]]=itFtext
                    
                    
                    
            nombreColeccion=self.dameTituloColeccionByGSID(self.groups[3].widgets["coleccion"].value)
            dicDatosItem={
                "version":"1",
                "nomreColeccion":nombreColeccion,
                "idColec":self.groups[3].widgets["coleccion"].value,
                "ruta":rutaItem,                
                "folder":self.groups[3].widgets["coleccion"].value+"/"+rutaItem.replace("/metadata.xml",""),
                "metadatos":tmpList,
                #"metadatos":[(infoMetaItem[x],self.groups[2].widgets[x].value) for x in infoMetadatos]
                }
            
            #-------- cargo ITEM
            tmpList={}
            for x in infoMetadatosSerie:
                if "form.widgets.%s"%x in self.request.form.keys():
                    itFtext=self.request.form["form.widgets."+x]
                    #itFtext=self.groups[2].widgets[x].value
                    #tmpList.append((infoMetadatosSerie[x],itFtext))
                    tmpList[infoMetadatosSerie[x]]=itFtext
                            
            dicDatosSerie={
                "version":"1",
                "nomreColeccion":nombreColeccion,
                "idColec":self.groups[3].widgets["coleccion"].value,
                "ruta":rutaSerie,
                "folder":self.groups[3].widgets["coleccion"].value+"/"+rutaSerie.replace("/metadata.xml",""),
                "metadatos":tmpList,
                #"metadatos":[(infoMetadatosSerie[x],self.groups[0].widgets[x].value) for x in infoMetadatosSerie]
            }
            
            if subSerieOk:
                tmpList={}
                for x in infoMetadatoSubSerie:
                    if "form.widgets.%s"%x in self.request.form.keys():
                        itFtext=self.request.form["form.widgets."+x]
                        #itFtext=self.groups[1].widgets[x].value                      
                        #tmpList.append((infoMetadatoSubSerie[x],itFtext))
                        tmpList[infoMetadatoSubSerie[x]]=itFtext
                
                dicDatosSubSerie={
                    "version":"1",
                    "nomreColeccion":nombreColeccion,
                    "idColec":self.groups[3].widgets["coleccion"].value,
                    "ruta":rutaSubSerie,
                    "folder":self.groups[3].widgets["coleccion"].value+"/"+rutaSubSerie.replace("/metadata.xml",""),
                    "metadatos":tmpList
                }
            self.fsmanager=FSManager()
            flagm=0
            
            #una lista para controlar si se guardo, si dio error o sin cambios
            saveStatusArr=[0,0]
            
            itemsaved=self.fsmanager.saveFile(dicDatosItem,"item",operarioDict)
            seriesaved=self.fsmanager.saveFile(dicDatosSerie,"serie",operarioDict)

            if itemsaved[0]=="error":
                msj+=u"> No se pudo guardar el item en %s \r"%rutaItem
                itemsaved[2]=rutaItem
                saveStatusArr[0]=1
            elif itemsaved[0]=="sin cambios":
                msj+=u"> No se encontraron cambios. \r"
                saveStatusArr[0]=10
                
            if seriesaved[0]=="error":
                msj+=u"> No se pudo guardar la serie en %s \r"%rutaSerie
                seriesaved[2]=rutaSerie
                saveStatusArr[1]=1
            elif seriesaved[0]=="sin cambios":
                msj+=u"> No se encontraron cambios en la Serie.\r"
                saveStatusArr[1]=10
                
            if subSerieOk:         
                subSeriesaved=self.fsmanager.saveFile(dicDatosSubSerie,"subSerie",operarioDict)
                saveStatusArr.append(0)
                if subSeriesaved[0]=="error":
                    msj+="> No se pudo guardar la sub serie en %s\r" %rutaSubSerie
                    subSeriesaved[2]=rutaSubSerie
                    saveStatusArr[2]=1
                elif subSeriesaved[0]=="sin cambios":
                    msj+="> No se encontraron cambios en la subsetire.\r"
                    saveStatusArr[2]=10
            else:
                subSeriesaved='sin sub serie'

            miurltmp=self.context.REQUEST.URL
            miurl   ="/".join(miurltmp.split("/")[:-2])

            
            if 0 in saveStatusArr:
                mandoCorreo=self.emails({'ritem':itemsaved,'rsubserie':subSeriesaved,'rserie':seriesaved,'nombreColeccion':nombreColeccion},operarioDict)            
                tituloMail=u"Cambios guardados correctamente"
                if 1 in saveStatusArr:
                    self.msjForm =u"Los cambios fueron guardados, pero surgieron errores. Se envió un email para control."                    
                    tituloMail=u"No todos los formularios fueron guardados"
                    if not mandoCorreo:
                        self.msjForm =u"Los cambios fueron guardados, pero surgieron errores. No pudo enviarse un email para control."
                else:
                    self.msjForm =u"Los cambios fueron guardados correctamente. Se generó una nueva versión de metadatos y se envió un email para control."                    
                    if not mandoCorreo:                                    
                        self.msjForm =u"Los cambios fueron guardados correctamente.  No pudo enviarse un email para control.."           
            

                self.context.REQUEST.RESPONSE.redirect(miurl+"/formsOk_view?mensaje="+self.msjForm.encode('utf8')+"&titulo="+tituloMail.encode('utf8'))
            
            elif 0 not in saveStatusArr:
                #Todo fue error
                
                if not 1 in saveStatusArr:
                    #sin cambios, form Ok, no se guardo nada.            
                    print u"sin cambios "
                    self.context.REQUEST.RESPONSE.redirect(miurl+"/formsOk_view?mensaje=No se encontraron cambios. No se envió ningú correo de control.&titulo=Formulario sin procesar")                                             
                else:
                    print u"No se pudo guardar nada... error de permisos?"
                    mandoCorreo=self.emails({'ritem':itemsaved,'rsubserie':subSeriesaved,'rserie':seriesaved,'nombreColeccion':nombreColeccion},operarioDict)
                    self.msjForm =u"No pudo guardase ningún dato. Puede haber un error de permisos en los directorios, o problemas con el metadato bi.ruta"
                    self.context.REQUEST.RESPONSE.redirect(miurl+"/formsCancel_view?mensaje="+self.msjForm.encode('utf8')+"&titulo=Error al guardar")                               
                
                    
            
        

    @button.buttonAndHandler(u"Cancel")
    def handleCancel(self, action):
        """User cancelled. Redirect back to the front page."""

        COLECCION=SERIE=SUBSERIE=""
        self.status = "Cambios cancelados"
        self.form._finishedAdd = True
        miurl="/".join(self.context.REQUEST.URL.split("/")[:-1])+"/formsCancel_view?mensaje= La edición fue cancelar&titulo=Formulario cancelado por el usuario"
        self.context.REQUEST.RESPONSE.redirect(miurl)

    def dameTituloColeccionByGSID(self,gsid):
        cata=getToolByName(self.context,"portal_catalog")
        brains=cata(portal_type="arcas.coleccion")
        nombreColeccion=""
        for elem in brains:
            if elem.getObject().GS_ID==gsid:
                nombreColeccion=elem.Title
                break

        return nombreColeccion
           
    def emails(self,datos,operarioDict):        
        msj=Cartero(self.context,operarioDict)
        loMando=msj.sendModificacion(datos)
        return loMando


    

