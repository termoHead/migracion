from zope.interface import implements
from zope.viewlet.interfaces import IViewlet
from zope.publisher.browser import BrowserView
from Products.Five.browser.pagetemplatefile import \
ViewPageTemplateFile

from arcas.content.coleccion import IColeccion
from zope.viewlet.interfaces import IViewletManager


class ISeccionUno(IViewletManager):
	"""Un marker para el viewlet manager de la seccion 1 de la columna derecha, en la vista de Coleccion"""


class ISeccionDos(IViewletManager):
	"""Un marker para el viewlet manager de la seccion 2 de la columna derecha, en la vista de Coleccion"""




class GaleriaViewlet(BrowserView):
    """Display the message subject
    """    
    def __init__(self, context, request, view, manager):
        self.context = context
        self.request = request
        self.__parent__ = view # from IContentProvider
        self.manager = manager # from IViewlet
        
    def update(self):
        pass
        render = ViewPageTemplateFile("viewlets/galeria_viewlet.pt")