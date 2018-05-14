import json
import pdb
# Note that by default Add portal member permissions
# is only for the owner, so we need to by bass it here
from Products.CMFPlone.utils import _createObjectByType
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import queryUtility


myPortal = app.arcas
portada= myPortal.portada

archivos=("acerca_de_arcas.json","novedades.json","colecciones.json")
flag=0

def inicio():
    
    for ffile in archivos[0:1]:
        parseado = dameObjetoDesdeArchivo(ffile)
        print parseado
        objP={'id':'acerca_de_arcas','portal_type':'Folder','title':'Acerca de Arcas','content':parseado}
        cargandoDatosEnPlone(objP,portada)
            

def cargandoDatosEnPlone(jsonObj,carpeta):
    bascicData=("id","portal_type","content")
    

    esContenedor=False;
    if "content" in jsonObj.keys():
        esContenedor=True;


    if jsonObj['id'] in [k for k,d in carpeta.items()]:
        try:
            print "borrando el objeto %s" %jsonObj['id']
            carpeta.manage_delObjects([jsonObj['id']])
        except:
            print "problema borrando el objeto %s" %jsonObj['id']
            
        new_id      = carpeta.invokeFactory(jsonObj['portal_type'], jsonObj['id'])
        contenedor  = carpeta[new_id]

    for atri in jsonObj.keys():
        if atri not in bascicData:
            try:
                setattr(contenedor,atri,jsonObj[atri])
                print "seteo %s" %jsonObj[atri]
            except:
                print "no pude setear atributo %s a %s" %(conenedor.id,atri)

    fti = queryUtility(IDexterityFTI, name=jsonObj['portal_type'])
    
    if esContenedor:
        if len(jsonObj["content"])>0:
            cargandoDatosEnPlone(jsonObj["content"][0],contenedor)

    return

    if esContenedor:
        """cargandoDatosEnPlone(jsonObj)"""
        for subObj in jsonObj["content"]:
            cargandoDatosEnPlone(subObj)
            print "parsea CONTENT"
        

        



def saveParsedObject(self,objJson,objeto):
        newO={}
        newO["id"]=obj.id
        newO["portal_type"]=obj.portal_type
        fti = queryUtility(IDexterityFTI, name=obj.portal_type)
       
        if fti==None:
            
            if obj.portal_type=="File":
                self.log.append("AT type FILE")
                newO["title"]=obj.title
                newO["description"]=obj.description
                errorFlag=0
                msj="Blobo ok: "
                try:
                    blb=obj.__annotations__.items()[0][1].blob
                    pdfName=obj.__annotations__.items()[0][1].filename
                    ppf=blb.open()
                    pdfR=ppf.name
                    try:
                        with open(pdfR, 'rb') as f:
                            blobx = base64.b64encode(f.read())
                        blobY = base64.b64decode(blobx)
                        resultF = open("blobTMP/"+pdfName,'wb')
                        resultF.write(blobY)
                        resultF.close()
                    except:
                        print "algo salio mal al guardar el archivo"
                        msj="Blobo Error: No se pudieron guardar los datos: "
                except:
                    print "algo salio mal al extraer datos del archivo"
                    msj="Blobo Error: No se pudieron extraer los datos: "

                self.log.append(msj+pdfName)
            else:
                self.log.append("AT type")
                for nomField in obj.schema.keys():
                    if nomField=="image":
                        img = obj.Schema().getField('image').getScale(obj,scale="preview")
                        if img!='':
                            newO["image"]=img.data.encode("base64")
                    else:
                        newO[nomField]=str(obj[nomField])

        else:
            self.log.append("Dexterity type")
            behaviors = list(fti.behaviors)
            behaviors.append(fti.schema)
            for iface in behaviors:
                intrObject=resolve(iface)
                
                for nom,desc in intrObject.namesAndDescriptions():
                    campClass = desc.__class__.__name__
                    
                    if campClass == "RichText":
                        "si es rich tecxt"
                        if getattr(intrObject(obj),nom)==None:
                            newO[nom]=""
                        else:
                            estrin=(getattr(intrObject(obj),nom)).output
                            newO[nom]= estrin.encode("utf-8")
                    elif campClass == "NamedBlobImage":
                        try:
                            newO[nom]= getattr(intrObject(obj),nom).data.encode("base64")
                        except:
                            print "el campo %s no tiene y" %nom
                            
                    elif campClass == "NamedBlobFile":
                        try:
                            newO[nom]= getattr(intrObject(obj),nom).data.encode("base64")
                        except:
                            print "el campo %s no tiene x" %nom
                    else:
                        newO[nom]= getattr(intrObject(obj),nom)
        


def dameObjetoDesdeArchivo(filename):
    gals=[]
    with open(filename) as json_data:
        cab   = json.load(json_data)
        jsonf = json.loads(cab)
        
        for galeria in jsonf["contenidos"]:
            gg={}
            for elem in galeria.keys():
                gg[elem]=galeria[elem]
            gals.append(gg)

    return gals

inicio()