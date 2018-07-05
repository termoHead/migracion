# -*- coding: utf-8 -*
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from arcas.content.coleccion import IColeccion

class ListadoColeccion(BrowserView):
    """Vista del Listado de colecciones"""
    
    def __init__(self, context, request):
        self.context    =context
        self.request =request
    
    def dameListaColecciones(self):
        """Devuelve una Lista con dicccionario de cada coleccion"""
        context = self.context.aq_inner
        catalogo=getToolByName(context,"portal_catalog")
        portal_state = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        portal=portal_state.portal()
        result=catalogo(object_provides=IColeccion.__identifier__)
        listados=[]
        for colec in result:
            miOb=context.unrestrictedTraverse(colec.getPath())
            listados.append({
                "titulo":colec.Title,
                "descri":colec.Description,
                "url":colec.getURL(),
                "img":miOb.imagenLista
            })
        return listados
